from typing import Dict, Any
from ...core.base_domain import BaseDomain, DomainInput, DomainOutput
import json


class BackendDomain(BaseDomain):
    """Domain responsible for backend development including APIs, databases, and server-side logic"""

    def __init__(self, name: str = "backend", description: str = "Develops backend services including APIs, databases, and server-side logic", resource_manager=None, cache_enabled: bool = True):
        super().__init__(name=name, description=description, resource_manager=resource_manager, cache_enabled=cache_enabled)
        self.frameworks = ["django", "flask", "fastapi", "express", "spring_boot", "laravel", "rails", "aspnet_core"]
        self.databases = ["postgresql", "mysql", "mongodb", "sqlite", "redis", "cassandra", "elasticsearch"]
        self.api_types = ["rest", "graphql", "grpc", "soap", "websocket"]
        self.authentication_methods = ["jwt", "oauth2", "session", "basic_auth", "api_key"]
        self.backend_templates = {
            "api_endpoint": self._generate_api_endpoint_template,
            "model": self._generate_model_template,
            "service": self._generate_service_template,
            "middleware": self._generate_middleware_template,
            "authentication": self._generate_authentication_template
        }

    async def execute(self, input_data: DomainInput) -> DomainOutput:
        """Generate backend code based on the input specification"""
        try:
            # Acquire resources before executing
            if not await self.resource_manager.acquire_resources(self.name):
                return DomainOutput(
                    success=False,
                    error=f"Resource limits exceeded for domain {self.name}"
                )

            try:
                query = input_data.query.lower()
                context = input_data.context
                params = input_data.parameters

                # Determine the type of backend code to generate
                backend_type = self._determine_backend_type(query)
                framework = params.get("framework", context.get("framework", "fastapi"))
                database = params.get("database", context.get("database", "postgresql"))
                api_type = params.get("api_type", context.get("api_type", "rest"))
                auth_method = params.get("auth_method", context.get("auth_method", "jwt"))

                if framework not in self.frameworks:
                    return DomainOutput(
                        success=False,
                        error=f"Framework '{framework}' not supported. Available frameworks: {', '.join(self.frameworks)}"
                    )

                # Generate the backend code
                generated_code = self._generate_backend_code(backend_type, query, framework, database, api_type, auth_method, params)

                # Enhance the code if other domains are available
                enhanced_code = await self._enhance_with_other_domains(generated_code, input_data)

                return DomainOutput(
                    success=True,
                    data={
                        "code": enhanced_code,
                        "framework": framework,
                        "database": database,
                        "api_type": api_type,
                        "auth_method": auth_method,
                        "type": backend_type,
                        "original_query": query
                    },
                    metadata={
                        "domain": self.name,
                        "enhanced": enhanced_code != generated_code
                    }
                )
            finally:
                # Always release resources after execution
                self.resource_manager.release_resources(self.name)
        except Exception as e:
            return DomainOutput(
                success=False,
                error=f"Backend code generation failed: {str(e)}"
            )

    def can_handle(self, input_data: DomainInput) -> bool:
        """Determine if this domain can handle the input"""
        query = input_data.query.lower()

        # Check for keywords that suggest backend development
        backend_keywords = [
            "backend", "api", "server", "database", "model", "service", 
            "middleware", "authentication", "authorization", "orm", 
            "rest api", "graphql", "grpc", "microservice", "server-side", 
            "django", "flask", "fastapi", "express", "spring boot", 
            "postgresql", "mysql", "mongodb", "redis", "database schema", 
            "migration", "validation", "serialization", "deserialization", 
            "endpoint", "route", "controller", "repository", "dao", 
            "jwt", "oauth", "session", "login", "logout", "register", 
            "crud", "create", "read", "update", "delete"
        ]

        return any(keyword in query for keyword in backend_keywords)

    def _determine_backend_type(self, query: str) -> str:
        """Determine what type of backend code to generate based on the query"""
        if any(word in query for word in ["api", "endpoint", "route", "controller"]):
            return "api_endpoint"
        elif any(word in query for word in ["model", "schema", "entity", "database"]):
            return "model"
        elif any(word in query for word in ["service", "business logic", "manager"]):
            return "service"
        elif any(word in query for word in ["middleware", "filter", "interceptor"]):
            return "middleware"
        elif any(word in query for word in ["authentication", "auth", "login", "register", "jwt", "oauth"]):
            return "authentication"
        else:
            return "api_endpoint"  # Default to API endpoint

    def _generate_backend_code(self, backend_type: str, query: str, framework: str, database: str, api_type: str, auth_method: str, params: Dict[str, Any]) -> str:
        """Generate backend code based on type, query, and framework"""
        if backend_type in self.backend_templates:
            return self.backend_templates[backend_type](query, framework, database, api_type, auth_method, params)
        else:
            return self._generate_generic_backend_code(query, backend_type, framework, database, api_type, auth_method, params)

    def _generate_api_endpoint_template(self, query: str, framework: str, database: str, api_type: str, auth_method: str, params: Dict[str, Any]) -> str:
        """Generate a backend API endpoint based on the query"""
        endpoint_path = params.get("endpoint_path", "/api/items")
        method = params.get("method", "get")
        
        if framework == "fastapi":
            return f"""from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List
import schemas, models, database
from auth import get_current_user

router = APIRouter(
    prefix="{endpoint_path}",
    tags=['{endpoint_path.split("/")[-1].capitalize()}']
)

@router.{method}("/")
async def get_items(db: Session = Depends(database.get_db)):
    """
    Retrieve a list of items.
    """
    items = db.query(models.Item).all()
    return items

@router.post("/", status_code=status.HTTP_201_CREATED)
async def create_item(item: schemas.ItemCreate, db: Session = Depends(database.get_db)):
    """
    Create a new item.
    """
    new_item = models.Item(**item.dict())
    db.add(new_item)
    db.commit()
    db.refresh(new_item)
    return new_item

@router.get("/{"/".join(["{id}"] * endpoint_path.count("/"))}", status_code=status.HTTP_200_OK)
async def get_item(id: int, db: Session = Depends(database.get_db)):
    """
    Retrieve a specific item by ID.
    """
    item = db.query(models.Item).filter(models.Item.id == id).first()
    if not item:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Item with id {{id}} not found")
    return item

@router.put("/{"/".join(["{id}"] * endpoint_path.count("/"))}")
async def update_item(id: int, item_update: schemas.ItemUpdate, db: Session = Depends(database.get_db)):
    """
    Update a specific item by ID.
    """
    item_query = db.query(models.Item).filter(models.Item.id == id)
    item = item_query.first()
    
    if not item:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Item with id {{id}} not found")
    
    item_query.update(item_update.dict(), synchronize_session=False)
    db.commit()
    return item_query.first()

@router.delete("/{"/".join(["{id}"] * endpoint_path.count("/"))}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_item(id: int, db: Session = Depends(database.get_db)):
    """
    Delete a specific item by ID.
    """
    item = db.query(models.Item).filter(models.Item.id == id)
    
    if not item.first():
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Item with id {{id}} not found")
    
    item.delete(synchronize_session=False)
    db.commit()
    return
"""
        elif framework == "flask":
            return f"""from flask import Blueprint, request, jsonify
from models import Item, db
from auth import token_required
import json

bp = Blueprint('{endpoint_path.split("/")[-1]}', __name__, url_prefix='{endpoint_path}')

@bp.route('/', methods=['GET'])
@token_required
def get_items(current_user):
    """
    Retrieve a list of items.
    """
    items = Item.query.all()
    return jsonify([item.to_dict() for item in items])

@bp.route('/', methods=['POST'])
@token_required
def create_item(current_user):
    """
    Create a new item.
    """
    data = request.get_json()
    
    new_item = Item(
        name=data['name'],
        description=data.get('description'),
        # Add other fields as needed
    )
    
    db.session.add(new_item)
    db.session.commit()
    
    return jsonify(new_item.to_dict()), 201

@bp.route('/<int:item_id>', methods=['GET'])
@token_required
def get_item(current_user, item_id):
    """
    Retrieve a specific item by ID.
    """
    item = Item.query.get_or_404(item_id)
    return jsonify(item.to_dict())

@bp.route('/<int:item_id>', methods=['PUT'])
@token_required
def update_item(current_user, item_id):
    """
    Update a specific item by ID.
    """
    item = Item.query.get_or_404(item_id)
    data = request.get_json()
    
    item.name = data.get('name', item.name)
    item.description = data.get('description', item.description)
    # Update other fields as needed
    
    db.session.commit()
    return jsonify(item.to_dict())

@bp.route('/<int:item_id>', methods=['DELETE'])
@token_required
def delete_item(current_user, item_id):
    """
    Delete a specific item by ID.
    """
    item = Item.query.get_or_404(item_id)
    db.session.delete(item)
    db.session.commit()
    
    return jsonify({{'message': 'Item deleted successfully'}}), 204
"""
        elif framework == "express":
            return f"""const express = require('express');
const router = express.Router();
const Item = require('../models/Item');
const auth = require('../middleware/auth');

// @route    GET {endpoint_path}/
// @desc     Get all items
// @access   Private
router.get('/', auth, async (req, res) => {{
  try {{
    const items = await Item.find();
    res.json(items);
  }} catch (err) {{
    console.error(err.message);
    res.status(500).send('Server Error');
  }}
}});

// @route    POST {endpoint_path}/
// @desc     Create a new item
// @access   Private
router.post('/', auth, async (req, res) => {{
  const {{ name, description }} = req.body;

  try {{
    const newItem = new Item({{
      name,
      description
      // Add other fields as needed
    }});

    const item = await newItem.save();
    res.json(item);
  }} catch (err) {{
    console.error(err.message);
    res.status(500).send('Server Error');
  }}
}});

// @route    GET {endpoint_path}/:id
// @desc     Get item by ID
// @access   Private
router.get('/:id', auth, async (req, res) => {{
  try {{
    const item = await Item.findById(req.params.id);

    if (!item) {{
      return res.status(404).json({{ msg: 'Item not found' }});
    }}

    res.json(item);
  }} catch (err) {{
    console.error(err.message);
    res.status(500).send('Server Error');
  }}
}});

// @route    PUT {endpoint_path}/:id
// @desc     Update item by ID
// @access   Private
router.put('/:id', auth, async (req, res) => {{
  const {{ name, description }} = req.body;

  const itemFields = {{
    name,
    description
    // Add other fields as needed
  }};

  try {{
    let item = await Item.findById(req.params.id);

    if (!item) {{
      return res.status(404).json({{ msg: 'Item not found' }});
    }}

    item = await Item.findByIdAndUpdate(
      {{ _id: req.params.id }},
      {{ $set: itemFields }},
      {{ new: true }}
    );

    res.json(item);
  }} catch (err) {{
    console.error(err.message);
    res.status(500).send('Server Error');
  }}
}});

// @route    DELETE {endpoint_path}/:id
// @desc     Delete item by ID
// @access   Private
router.delete('/:id', auth, async (req, res) => {{
  try {{
    const item = await Item.findById(req.params.id);

    if (!item) {{
      return res.status(404).json({{ msg: 'Item not found' }});
    }}

    await Item.findByIdAndRemove(req.params.id);
    res.json({{ msg: 'Item removed' }});
  }} catch (err) {{
    console.error(err.message);
    res.status(500).send('Server Error');
  }}
}});

module.exports = router;
"""
        else:
            return f"# API endpoint for {query} using {framework}"

    def _generate_model_template(self, query: str, framework: str, database: str, api_type: str, auth_method: str, params: Dict[str, Any]) -> str:
        """Generate a backend model based on the query"""
        model_name = params.get("model_name", "Item")
        
        if framework == "django":
            return f"""from django.db import models
from django.contrib.auth.models import User
from django.urls import reverse


class {model_name}(models.Model):
    """
    {model_name} model representing {query}
    """
    name = models.CharField(max_length=100)
    description = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    owner = models.ForeignKey(User, on_delete=models.CASCADE, related_name='{model_name.lower()}s')
    
    class Meta:
        ordering = ['-created_at']
        verbose_name = '{model_name}'
        verbose_name_plural = '{model_name}s'

    def __str__(self):
        return self.name

    def get_absolute_url(self):
        return reverse('{model_name.lower()}_detail', kwargs={{'pk': self.pk}})
"""
        elif framework == "fastapi":
            return f"""from sqlalchemy import Column, Integer, String, Text, DateTime, ForeignKey
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
from datetime import datetime

Base = declarative_base()

class {model_name}(Base):
    """
    {model_name} model representing {query}
    """
    __tablename__ = '{model_name.lower()}s'

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), nullable=False)
    description = Column(Text, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    owner_id = Column(Integer, ForeignKey('users.id'))

    # Relationships
    owner = relationship("User", back_populates="{model_name.lower()}s")
"""
        elif framework == "express":
            return f"""const mongoose = require('mongoose');

const {model_name.lower()}Schema = new mongoose.Schema({{
  name: {{
    type: String,
    required: true,
    trim: true
  }},
  description: {{
    type: String,
    required: false
  }},
  createdAt: {{
    type: Date,
    default: Date.now
  }},
  updatedAt: {{
    type: Date,
    default: Date.now
  }},
  owner: {{
    type: mongoose.Schema.Types.ObjectId,
    ref: 'User',
    required: true
  }}
}});

// Update 'updatedAt' field before saving
{model_name.lower()}Schema.pre('save', function(next) {{
  this.updatedAt = Date.now();
  next();
}});

module.exports = mongoose.model('{model_name}', {model_name.lower()}Schema);
"""
        else:
            return f"# Model for {model_name} representing {query} using {framework} and {database}"

    def _generate_service_template(self, query: str, framework: str, database: str, api_type: str, auth_method: str, params: Dict[str, Any]) -> str:
        """Generate a backend service based on the query"""
        service_name = params.get("service_name", "ItemService")
        
        if framework == "fastapi":
            return f"""from typing import Optional, List
from sqlalchemy.orm import Session
from models import {service_name.replace('Service', '')}
from schemas import {service_name.replace('Service', '')}Create, {service_name.replace('Service', '')}Update


class {service_name}:
    """
    Service class for handling {query} business logic
    """
    
    def __init__(self, db: Session):
        self.db = db

    def get_{service_name.replace('Service', '').lower()}(self, {service_name.replace('Service', '').lower()}_id: int) -> Optional[{service_name.replace('Service', '')}]:
        """
        Retrieve a {service_name.replace('Service', '').lower()} by ID
        """
        return self.db.query({service_name.replace('Service', '')}).filter({service_name.replace('Service', '')}.id == {service_name.replace('Service', '').lower()}_id).first()

    def get_{service_name.replace('Service', '').lower()}s(self, skip: int = 0, limit: int = 100) -> List[{service_name.replace('Service', '')}]:
        """
        Retrieve a list of {service_name.replace('Service', '').lower()}s with pagination
        """
        return self.db.query({service_name.replace('Service', '')}).offset(skip).limit(limit).all()

    def create_{service_name.replace('Service', '').lower()}(self, {service_name.replace('Service', '').lower()}_data: {service_name.replace('Service', '')}Create) -> {service_name.replace('Service', '')}:
        """
        Create a new {service_name.replace('Service', '').lower()}
        """
        new_{service_name.replace('Service', '').lower()} = {service_name.replace('Service', '')}(**{service_name.replace('Service', '').lower()}_data.dict())
        self.db.add(new_{service_name.replace('Service', '').lower()})
        self.db.commit()
        self.db.refresh(new_{service_name.replace('Service', '').lower()})
        return new_{service_name.replace('Service', '').lower()}

    def update_{service_name.replace('Service', '').lower()}(self, {service_name.replace('Service', '').lower()}_id: int, {service_name.replace('Service', '').lower()}_data: {service_name.replace('Service', '')}Update) -> Optional[{service_name.replace('Service', '')}]:
        """
        Update an existing {service_name.replace('Service', '').lower()}
        """
        {service_name.replace('Service', '').lower()} = self.get_{service_name.replace('Service', '').lower()}({service_name.replace('Service', '').lower()}_id)
        if {service_name.replace('Service', '').lower()}:
            update_data = {service_name.replace('Service', '').lower()}_data.dict(exclude_unset=True)
            for field, value in update_data.items():
                setattr({service_name.replace('Service', '').lower()}, field, value)
            self.db.commit()
            self.db.refresh({service_name.replace('Service', '').lower()})
        return {service_name.replace('Service', '').lower()}

    def delete_{service_name.replace('Service', '').lower()}(self, {service_name.replace('Service', '').lower()}_id: int) -> bool:
        """
        Delete a {service_name.replace('Service', '').lower()}
        """
        {service_name.replace('Service', '').lower()} = self.get_{service_name.replace('Service', '').lower()}({service_name.replace('Service', '').lower()}_id)
        if {service_name.replace('Service', '').lower()}:
            self.db.delete({service_name.replace('Service', '').lower()})
            self.db.commit()
            return True
        return False
"""
        elif framework == "express":
            return f"""const {service_name.replace('Service', '')} = require('../models/{service_name.replace('Service', '')}');

class {service_name} {{
    /**
     * Service class for handling {query} business logic
     */

    static async getAll{service_name.replace('Service', '')}(options = {{}}) {{
        try {{
            const {{ skip = 0, limit = 10, sort = {{ createdAt: -1 }} }} = options;
            const items = await {service_name.replace('Service', '')}.find()
                .skip(parseInt(skip))
                .limit(parseInt(limit))
                .sort(sort);
            return items;
        }} catch (error) {{
            throw new Error(`Error retrieving {service_name.replace('Service', '').toLowerCase()}s: ${{error.message}}`);
        }}
    }}

    static async get{service_name.replace('Service', '')}(id) {{
        try {{
            const item = await {service_name.replace('Service', '')}.findById(id);
            if (!item) {{
                throw new Error('{service_name.replace('Service', '').toLowerCase()} not found');
            }}
            return item;
        }} catch (error) {{
            throw new Error(`Error retrieving {service_name.replace('Service', '').toLowerCase()} by ID: ${{error.message}}`);
        }}
    }}

    static async create{service_name.replace('Service', '')}(data) {{
        try {{
            const newItem = new {service_name.replace('Service', '')}(data);
            const savedItem = await newItem.save();
            return savedItem;
        }} catch (error) {{
            throw new Error(`Error creating {service_name.replace('Service', '').toLowerCase()} : ${{error.message}}`);
        }}
    }}

    static async update{service_name.replace('Service', '')}(id, data) {{
        try {{
            const updatedItem = await {service_name.replace('Service', '')}.findByIdAndUpdate(
                id,
                {{ ...data, updatedAt: Date.now() }},
                {{ new: true, runValidators: true }}
            );
            if (!updatedItem) {{
                throw new Error('{service_name.replace('Service', '').toLowerCase()} not found');
            }}
            return updatedItem;
        }} catch (error) {{
            throw new Error(`Error updating {service_name.replace('Service', '').toLowerCase()} : ${{error.message}}`);
        }}
    }}

    static async delete{service_name.replace('Service', '')}(id) {{
        try {{
            const deletedItem = await {service_name.replace('Service', '')}.findByIdAndDelete(id);
            if (!deletedItem) {{
                throw new Error('{service_name.replace('Service', '').toLowerCase()} not found');
            }}
            return deletedItem;
        }} catch (error) {{
            throw new Error(`Error deleting {service_name.replace('Service', '').toLowerCase()} : ${{error.message}}`);
        }}
    }}
}}

module.exports = {service_name};
"""
        else:
            return f"# Service for {service_name} handling {query} using {framework}"

    def _generate_middleware_template(self, query: str, framework: str, database: str, api_type: str, auth_method: str, params: Dict[str, Any]) -> str:
        """Generate a backend middleware based on the query"""
        middleware_name = params.get("middleware_name", "AuthMiddleware")
        
        if framework == "express":
            return f"""const jwt = require('jsonwebtoken');
require('dotenv').config();

const auth = async (req, res, next) => {{
  // Get token from header
  const token = req.header('x-auth-token');

  // Check if no token
  if (!token) {{
    return res.status(401).json({{ msg: 'No token, authorization denied' }});
  }}

  try {{
    // Verify token
    const decoded = jwt.verify(token, process.env.JWT_SECRET);

    // Add user from payload
    req.user = decoded.user;
    next();
  }} catch (err) {{
    res.status(401).json({{ msg: 'Token is not valid' }});
  }}
}};

module.exports = auth;
"""
        elif framework == "fastapi":
            return f"""from fastapi import Request, HTTPException
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
import jwt
from config import settings


class JWTBearer(HTTPBearer):
    """
    JWT Bearer token authentication middleware
    """
    def __init__(self, auto_error: bool = True):
        super(JWTBearer, self).__init__(auto_error=auto_error)

    async def __call__(self, request: Request):
        credentials: HTTPAuthorizationCredentials = await super(JWTBearer, self).__call__(request)
        if credentials:
            if not credentials.scheme == "Bearer":
                raise HTTPException(status_code=403, detail="Invalid authentication scheme.")
            token = credentials.credentials
            if not self.verify_jwt(token):
                raise HTTPException(status_code=403, detail="Invalid token or expired token.")
            return credentials.credentials
        else:
            raise HTTPException(status_code=403, detail="Invalid authorization code.")

    def verify_jwt(self, jwtoken: str) -> bool:
        """
        Verify the JWT token
        """
        isTokenValid: bool = False

        try:
            payload = jwt.decode(jwtoken, settings.JWT_SECRET_KEY, algorithms=["HS256"])
            isTokenValid = True if payload['exp'] >= time.time() else False
        except:
            isTokenValid = False
        return isTokenValid
"""
        elif framework == "django":
            return f"""import jwt
from django.conf import settings
from django.http import JsonResponse
from django.contrib.auth.models import User
from functools import wraps


def jwt_required(view_func):
    """
    JWT token authentication decorator
    """
    @wraps(view_func)
    def _wrapped_view(request, *args, **kwargs):
        token = None

        # Extract token from Authorization header
        if 'HTTP_AUTHORIZATION' in request.META:
            try:
                token = request.META['HTTP_AUTHORIZATION'].split(' ')[1]
            except IndexError:
                return JsonResponse({{'error': 'Bearer token malformed'}}, status=401)

        if not token:
            return JsonResponse({{'error': 'Token is missing'}}, status=401)

        try:
            # Decode the token
            payload = jwt.decode(token, settings.SECRET_KEY, algorithms=['HS256'])
            user_id = payload['user_id']

            # Get user from database
            user = User.objects.get(id=user_id)
        except jwt.ExpiredSignatureError:
            return JsonResponse({{'error': 'Token has expired'}}, status=401)
        except jwt.InvalidTokenError:
            return JsonResponse({{'error': 'Invalid token'}}, status=401)
        except User.DoesNotExist:
            return JsonResponse({{'error': 'User not found'}}, status=401)

        # Add user to request object
        request.user = user

        # Call the original view function
        return view_func(request, *args, **kwargs)

    return _wrapped_view
"""
        else:
            return f"# Middleware for {middleware_name} handling {query} using {framework}"

    def _generate_authentication_template(self, query: str, framework: str, database: str, api_type: str, auth_method: str, params: Dict[str, Any]) -> str:
        """Generate backend authentication code based on the query"""
        if auth_method == "jwt":
            if framework == "fastapi":
                return f"""from datetime import datetime, timedelta
from typing import Optional
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer
from jose import JWTError, jwt
from passlib.context import CryptContext
from sqlalchemy.orm import Session
from models import User
from database import get_db
from config import settings

# Password hashing
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# JWT token scheme
security = HTTPBearer()

def verify_password(plain_password: str, hashed_password: str) -> bool:
    return pwd_context.verify(plain_password, hashed_password)

def get_password_hash(password: str) -> str:
    return pwd_context.hash(password)

def authenticate_user(db: Session, email: str, password: str) -> Optional[User]:
    user = db.query(User).filter(User.email == email).first()
    if not user or not verify_password(password, user.hashed_password):
        return None
    return user

def create_access_token(data: dict, expires_delta: Optional[timedelta] = None):
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=15)
    to_encode.update({{"exp": expire}})
    encoded_jwt = jwt.encode(to_encode, settings.JWT_SECRET_KEY, algorithm=settings.JWT_ALGORITHM)
    return encoded_jwt

async def get_current_user(db: Session = Depends(get_db), token: str = Depends(security)):
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={{"WWW-Authenticate": "Bearer"}},
    )
    try:
        payload = jwt.decode(
            token.credentials, settings.JWT_SECRET_KEY, algorithms=[settings.JWT_ALGORITHM]
        )
        email: str = payload.get("sub")
        if email is None:
            raise credentials_exception
    except JWTError:
        raise credentials_exception
    user = db.query(User).filter(User.email == email).first()
    if user is None:
        raise credentials_exception
    return user
"""
            elif framework == "express":
                return f"""const jwt = require('jsonwebtoken');
const bcrypt = require('bcryptjs');
const User = require('../models/User');
require('dotenv').config();

// @desc    Register user
// @route   POST /api/auth/register
// @access  Public
const register = async (req, res) => {{
  const {{ name, email, password }} = req.body;

  try {{
    // Check if user already exists
    let user = await User.findOne({{ email }});

    if (user) {{
      return res.status(400).json({{ msg: 'User already exists' }});
    }}

    // Create new user
    user = new User({{
      name,
      email,
      password
    }});

    // Hash password
    const salt = await bcrypt.genSalt(10);
    user.password = await bcrypt.hash(password, salt);

    // Save user
    await user.save();

    // Create and return JWT token
    const payload = {{
      user: {{
        id: user.id
      }}
    }};

    jwt.sign(
      payload,
      process.env.JWT_SECRET,
      {{ expiresIn: '5 days' }},
      (err, token) => {{
        if (err) throw err;
        res.json({{
          token,
          user: {{
            id: user.id,
            name: user.name,
            email: user.email
          }}
        }});
      }}
    );
  }} catch (err) {{
    console.error(err.message);
    res.status(500).send('Server error');
  }}
}};

// @desc    Login user
// @route   POST /api/auth/login
// @access  Public
const login = async (req, res) => {{
  const {{ email, password }} = req.body;

  try {{
    // Check if user exists
    let user = await User.findOne({{ email }});

    if (!user) {{
      return res.status(400).json({{ msg: 'Invalid Credentials' }});
    }}

    // Validate password
    const isMatch = await bcrypt.compare(password, user.password);

    if (!isMatch) {{
      return res.status(400).json({{ msg: 'Invalid Credentials' }});
    }}

    // Create and return JWT token
    const payload = {{
      user: {{
        id: user.id
      }}
    }};

    jwt.sign(
      payload,
      process.env.JWT_SECRET,
      {{ expiresIn: '5 days' }},
      (err, token) => {{
        if (err) throw err;
        res.json({{
          token,
          user: {{
            id: user.id,
            name: user.name,
            email: user.email
          }}
        }});
      }}
    );
  }} catch (err) {{
    console.error(err.message);
    res.status(500).send('Server error');
  }}
}};

module.exports = {{ register, login }};
"""
            else:
                return f"# JWT Authentication for {query} using {framework}"
        else:
            return f"# Authentication for {query} using {auth_method} and {framework}"

    def _generate_generic_backend_code(self, query: str, backend_type: str, framework: str, database: str, api_type: str, auth_method: str, params: Dict[str, Any]) -> str:
        """Generate generic backend code when specific type isn't determined"""
        return f"""# {backend_type.title()} for {query}
# Framework: {framework}
# Database: {database}
# API Type: {api_type}
# Auth Method: {auth_method}

# TODO: Implement the {backend_type} based on the requirements
"""

    async def _enhance_with_other_domains(self, generated_code: str, input_data: DomainInput) -> str:
        """Allow other domains to enhance the generated backend code"""
        # In a real implementation, this would coordinate with other domains
        # For now, we'll just return the original code
        return generated_code