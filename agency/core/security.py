from typing import Dict, Any, List, Optional, Callable
import asyncio
import secrets
import hashlib
import hmac
import jwt
import time
from datetime import datetime, timedelta
from enum import Enum
from dataclasses import dataclass
from functools import wraps
import bcrypt
from ..utils.logger import get_logger


class Permission(Enum):
    """Permissions for different operations"""
    READ = "read"
    WRITE = "write"
    EXECUTE = "execute"
    ADMIN = "admin"
    MONITOR = "monitor"


class AuthProvider(Enum):
    """Authentication providers"""
    BASIC = "basic"
    JWT = "jwt"
    OAUTH2 = "oauth2"
    API_KEY = "api_key"


@dataclass
class User:
    """Represents a user in the system"""
    id: str
    username: str
    email: str
    permissions: List[Permission]
    created_at: datetime
    last_login: Optional[datetime] = None
    is_active: bool = True
    auth_provider: AuthProvider = AuthProvider.BASIC


@dataclass
class Token:
    """Authentication token"""
    token: str
    user_id: str
    expires_at: datetime
    issued_at: datetime
    permissions: List[Permission]
    revoked: bool = False


class AuthenticationError(Exception):
    """Raised when authentication fails"""
    pass


class AuthorizationError(Exception):
    """Raised when authorization fails"""
    pass


class SecurityManager:
    """Manages security aspects of the agency system"""
    
    def __init__(self, secret_key: str = None):
        self.secret_key = secret_key or secrets.token_hex(32)
        self.users: Dict[str, User] = {}
        self.tokens: Dict[str, Token] = {}
        self.api_keys: Dict[str, str] = {}  # api_key -> user_id
        self.rate_limits: Dict[str, List[float]] = {}  # user_id -> list of request timestamps
        self._logger = get_logger(__name__)
    
    def create_user(self, username: str, email: str, password: str, permissions: List[Permission]) -> User:
        """Create a new user with hashed password"""
        user_id = secrets.token_hex(16)
        hashed_password = self._hash_password(password)
        
        # Store password hash in api_keys dict for basic auth
        self.api_keys[user_id] = hashed_password
        
        user = User(
            id=user_id,
            username=username,
            email=email,
            permissions=permissions,
            created_at=datetime.now(),
            is_active=True
        )
        
        self.users[user_id] = user
        self._logger.info(f"Created user: {username} with ID: {user_id}")
        
        return user
    
    def authenticate_basic(self, username: str, password: str) -> Optional[User]:
        """Authenticate user with username/password"""
        # Find user by username
        user = None
        for u in self.users.values():
            if u.username == username:
                user = u
                break
        
        if not user or not self._verify_password(password, self.api_keys[user.id]):
            raise AuthenticationError("Invalid credentials")
        
        if not user.is_active:
            raise AuthenticationError("User account is inactive")
        
        user.last_login = datetime.now()
        self._logger.info(f"User {username} authenticated successfully")
        
        return user
    
    def authenticate_api_key(self, api_key: str) -> Optional[User]:
        """Authenticate user with API key"""
        if api_key not in self.api_keys:
            raise AuthenticationError("Invalid API key")
        
        user_id = self.api_keys[api_key]
        user = self.users.get(user_id)
        
        if not user or not user.is_active:
            raise AuthenticationError("Invalid user or account inactive")
        
        user.last_login = datetime.now()
        self._logger.info(f"User {user.username} authenticated via API key")
        
        return user
    
    def create_jwt_token(self, user_id: str, expires_in: int = 3600) -> str:
        """Create a JWT token for a user"""
        user = self.users.get(user_id)
        if not user:
            raise AuthenticationError("User not found")
        
        payload = {
            "user_id": user_id,
            "username": user.username,
            "permissions": [perm.value for perm in user.permissions],
            "exp": datetime.utcnow() + timedelta(seconds=expires_in),
            "iat": datetime.utcnow()
        }
        
        token = jwt.encode(payload, self.secret_key, algorithm="HS256")
        
        # Store token info
        self.tokens[token] = Token(
            token=token,
            user_id=user_id,
            expires_at=datetime.utcnow() + timedelta(seconds=expires_in),
            issued_at=datetime.utcnow(),
            permissions=user.permissions
        )
        
        self._logger.info(f"JWT token created for user: {user.username}")
        return token
    
    def verify_jwt_token(self, token: str) -> Optional[User]:
        """Verify a JWT token and return the user"""
        if token in self.tokens and self.tokens[token].revoked:
            raise AuthenticationError("Token has been revoked")
        
        try:
            payload = jwt.decode(token, self.secret_key, algorithms=["HS256"])
        except jwt.ExpiredSignatureError:
            raise AuthenticationError("Token has expired")
        except jwt.InvalidTokenError:
            raise AuthenticationError("Invalid token")
        
        user_id = payload.get("user_id")
        user = self.users.get(user_id)
        
        if not user or not user.is_active:
            raise AuthenticationError("User not found or inactive")
        
        user.last_login = datetime.now()
        self._logger.debug(f"JWT token verified for user: {user.username}")
        
        return user
    
    def revoke_token(self, token: str):
        """Revoke a token"""
        if token in self.tokens:
            self.tokens[token].revoked = True
            self._logger.info(f"Token revoked")
    
    def check_permission(self, user: User, permission: Permission) -> bool:
        """Check if user has a specific permission"""
        return permission in user.permissions or Permission.ADMIN in user.permissions
    
    def authorize(self, user: User, permission: Permission):
        """Raise AuthorizationError if user doesn't have permission"""
        if not self.check_permission(user, permission):
            raise AuthorizationError(f"User {user.username} does not have permission: {permission.value}")
    
    def rate_limit(self, identifier: str, max_requests: int = 100, window: int = 60) -> bool:
        """Check if a request exceeds rate limits"""
        now = time.time()
        window_start = now - window
        
        # Clean old requests
        if identifier in self.rate_limits:
            self.rate_limits[identifier] = [
                timestamp for timestamp in self.rate_limits[identifier]
                if timestamp > window_start
            ]
        else:
            self.rate_limits[identifier] = []
        
        # Check if limit exceeded
        if len(self.rate_limits[identifier]) >= max_requests:
            self._logger.warning(f"Rate limit exceeded for {identifier}")
            return False
        
        # Add current request
        self.rate_limits[identifier].append(now)
        return True
    
    def _hash_password(self, password: str) -> str:
        """Hash a password using bcrypt"""
        salt = bcrypt.gensalt()
        return bcrypt.hashpw(password.encode('utf-8'), salt).decode('utf-8')
    
    def _verify_password(self, password: str, hashed: str) -> bool:
        """Verify a password against its hash"""
        return bcrypt.checkpw(password.encode('utf-8'), hashed.encode('utf-8'))


class SecureDomainWrapper:
    """Wrapper to add security to domains"""
    
    def __init__(self, domain, security_manager: SecurityManager):
        self.domain = domain
        self.security_manager = security_manager
        self._logger = get_logger(f"SecureDomain.{domain.name}")
    
    async def execute(self, input_data, user: User = None):
        """Securely execute domain operation"""
        if user:
            # Check if user has execute permission
            self.security_manager.authorize(user, Permission.EXECUTE)
        
        # Log the execution
        self._logger.info(f"Secure execution of {self.domain.name} by user {user.username if user else 'anonymous'}")
        
        # Execute the wrapped domain
        return await self.domain.execute(input_data)
    
    def can_handle(self, input_data):
        """Check if domain can handle input (no auth required for this)"""
        return self.domain.can_handle(input_data)


class SecurityMiddleware:
    """Middleware for securing API endpoints and operations"""
    
    def __init__(self, security_manager: SecurityManager):
        self.security_manager = security_manager
        self._logger = get_logger(__name__)
    
    def require_auth(self, permission: Permission = Permission.READ):
        """Decorator to require authentication and specific permission"""
        def decorator(func):
            @wraps(func)
            async def wrapper(*args, **kwargs):
                # Extract token from kwargs or headers
                token = kwargs.get('auth_token') or self._extract_token_from_headers(kwargs.get('headers', {}))
                
                if not token:
                    raise AuthenticationError("Authentication token required")
                
                # Verify token
                user = self.security_manager.verify_jwt_token(token)
                
                # Check permission
                self.security_manager.authorize(user, permission)
                
                # Add user to kwargs for downstream functions
                kwargs['authenticated_user'] = user
                
                return await func(*args, **kwargs)
            return wrapper
        return decorator
    
    def rate_limit(self, max_requests: int = 100, window: int = 60):
        """Decorator to apply rate limiting"""
        def decorator(func):
            @wraps(func)
            async def wrapper(*args, **kwargs):
                # Extract client identifier (could be IP, user ID, etc.)
                client_id = kwargs.get('client_id') or kwargs.get('user_id', 'anonymous')
                
                if not self.security_manager.rate_limit(client_id, max_requests, window):
                    raise AuthorizationError("Rate limit exceeded")
                
                return await func(*args, **kwargs)
            return wrapper
        return decorator
    
    def _extract_token_from_headers(self, headers: Dict[str, str]) -> Optional[str]:
        """Extract token from Authorization header"""
        auth_header = headers.get('Authorization', '')
        if auth_header.startswith('Bearer '):
            return auth_header[7:]  # Remove 'Bearer ' prefix
        return None


# Global security manager instance
security_manager = SecurityManager()


def get_security_manager() -> SecurityManager:
    """Get the global security manager"""
    return security_manager