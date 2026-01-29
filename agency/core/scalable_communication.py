from typing import Dict, Any, List, Optional, Protocol
from enum import Enum
from dataclasses import dataclass
from abc import ABC, abstractmethod
import asyncio
import json
import uuid
from datetime import datetime
from ..utils.logger import get_logger


class MessageType(Enum):
    """Types of messages that can be exchanged between domains"""
    REQUEST = "request"
    RESPONSE = "response"
    NOTIFICATION = "notification"
    ERROR = "error"
    ENHANCEMENT_REQUEST = "enhancement_request"
    ENHANCEMENT_RESPONSE = "enhancement_response"


@dataclass
class Message:
    """Message structure for inter-domain communication"""
    message_type: MessageType
    sender: str
    receiver: Optional[str]
    content: Any
    correlation_id: str
    timestamp: float
    metadata: Optional[Dict[str, Any]] = None
    
    def __post_init__(self):
        if self.correlation_id is None:
            self.correlation_id = str(uuid.uuid4())


class CommunicationInterface(ABC):
    """Interface for inter-domain communication"""
    
    @abstractmethod
    async def send_message(self, message: Message) -> bool:
        """Send a message to another domain"""
        pass
    
    @abstractmethod
    async def receive_messages(self, domain_name: str, timeout: float = 1.0) -> List[Message]:
        """Receive messages for a specific domain"""
        pass
    
    @abstractmethod
    async def broadcast_message(self, message: Message, exclude_sender: bool = True) -> List[bool]:
        """Broadcast a message to all domains"""
        pass
    
    @abstractmethod
    async def register_domain(self, domain_name: str):
        """Register a domain with the communication system"""
        pass
    
    @abstractmethod
    async def unregister_domain(self, domain_name: str):
        """Unregister a domain from the communication system"""
        pass


class ScalableCommunicationHub(CommunicationInterface):
    """Scalable communication hub supporting multiple backends"""
    
    def __init__(self, max_queue_size: int = 1000):
        self._message_queues: Dict[str, asyncio.Queue] = {}
        self._registered_domains: List[str] = []
        self._max_queue_size = max_queue_size
        self._logger = get_logger(__name__)
    
    async def register_domain(self, domain_name: str):
        """Register a domain with the communication hub"""
        if domain_name not in self._registered_domains:
            self._registered_domains.append(domain_name)
            self._message_queues[domain_name] = asyncio.Queue(maxsize=self._max_queue_size)
            self._logger.info(f"Domain {domain_name} registered with communication hub")
    
    async def unregister_domain(self, domain_name: str):
        """Unregister a domain from the communication hub"""
        if domain_name in self._registered_domains:
            self._registered_domains.remove(domain_name)
            if domain_name in self._message_queues:
                del self._message_queues[domain_name]
            self._logger.info(f"Domain {domain_name} unregistered from communication hub")
    
    async def send_message(self, message: Message) -> bool:
        """Send a message to a specific domain"""
        if message.receiver is None:
            # This is a broadcast message
            await self.broadcast_message(message)
            return True
        
        if message.receiver in self._message_queues:
            try:
                await self._message_queues[message.receiver].put(message)
                return True
            except asyncio.QueueFull:
                self._logger.warning(f"Message queue for {message.receiver} is full, dropping message")
                return False
        else:
            self._logger.error(f"Receiver {message.receiver} not found in message queues")
            return False
    
    async def receive_messages(self, domain_name: str, timeout: float = 1.0) -> List[Message]:
        """Receive messages for a specific domain"""
        if domain_name not in self._message_queues:
            return []
        
        messages = []
        queue = self._message_queues[domain_name]
        
        # Try to get messages without blocking for too long
        try:
            while True:
                # Use timeout to prevent indefinite blocking
                message = await asyncio.wait_for(queue.get(), timeout=0.1)
                messages.append(message)
                
                # Check if there are more messages without blocking
                try:
                    while not queue.empty():
                        messages.append(queue.get_nowait())
                except asyncio.QueueEmpty:
                    break
        except asyncio.TimeoutError:
            # No messages available within timeout
            pass
        
        return messages
    
    async def broadcast_message(self, message: Message, exclude_sender: bool = True) -> List[bool]:
        """Broadcast a message to all registered domains"""
        results = []
        for domain in self._registered_domains:
            if exclude_sender and domain == message.sender:
                continue
            
            # Create a copy of the message for each recipient
            broadcast_msg = Message(
                message_type=message.message_type,
                sender=message.sender,
                receiver=domain,
                content=message.content,
                correlation_id=message.correlation_id,
                timestamp=message.timestamp,
                metadata=message.metadata
            )
            
            result = await self.send_message(broadcast_msg)
            results.append(result)
        
        return results


class InterDomainCommunicator:
    """Manages communication between domains with enhanced features"""
    
    def __init__(self, communication_hub: CommunicationInterface):
        self.hub = communication_hub
        self._pending_requests: Dict[str, asyncio.Future] = {}
        self._logger = get_logger(__name__)
    
    async def register_domain(self, domain_name: str):
        """Register a domain with the communication system"""
        await self.hub.register_domain(domain_name)
    
    async def unregister_domain(self, domain_name: str):
        """Unregister a domain from the communication system"""
        # Cancel any pending requests for this domain
        for corr_id, future in list(self._pending_requests.items()):
            if not future.done():
                future.cancel()
                del self._pending_requests[corr_id]
        
        await self.hub.unregister_domain(domain_name)
    
    async def request_enhancement(
        self, 
        sender: str, 
        target_domain: str, 
        content: Any, 
        timeout: float = 10.0
    ) -> Optional[Any]:
        """Request enhancement from a specific domain with timeout"""
        correlation_id = f"enh_{uuid.uuid4()}"
        
        # Create a future to hold the response
        future = asyncio.Future()
        self._pending_requests[correlation_id] = future
        
        # Send enhancement request
        message = Message(
            message_type=MessageType.ENHANCEMENT_REQUEST,
            sender=sender,
            receiver=target_domain,
            content=content,
            correlation_id=correlation_id,
            timestamp=datetime.now().timestamp()
        )
        
        success = await self.hub.send_message(message)
        
        if not success:
            # Clean up the future if sending failed
            del self._pending_requests[correlation_id]
            self._logger.error(f"Failed to send enhancement request from {sender} to {target_domain}")
            return None
        
        try:
            # Wait for response with timeout
            result = await asyncio.wait_for(future, timeout=timeout)
            return result
        except asyncio.TimeoutError:
            # Clean up the future on timeout
            if correlation_id in self._pending_requests:
                del self._pending_requests[correlation_id]
            self._logger.warning(f"Timeout waiting for enhancement response from {target_domain}")
            return None
    
    async def send_notification(
        self, 
        sender: str, 
        content: Any, 
        target_domains: Optional[List[str]] = None,
        timeout: float = 5.0
    ):
        """Send a notification to one or more domains"""
        if target_domains:
            # Send to specific domains
            for domain in target_domains:
                message = Message(
                    message_type=MessageType.NOTIFICATION,
                    sender=sender,
                    receiver=domain,
                    content=content,
                    correlation_id=str(uuid.uuid4()),
                    timestamp=datetime.now().timestamp()
                )
                await self.hub.send_message(message)
        else:
            # Create broadcast message
            message = Message(
                message_type=MessageType.NOTIFICATION,
                sender=sender,
                receiver=None,  # Will be set during broadcast
                content=content,
                correlation_id=str(uuid.uuid4()),
                timestamp=datetime.now().timestamp()
            )
            await self.hub.broadcast_message(message)
    
    async def handle_incoming_messages(self, domain_name: str, timeout: float = 1.0):
        """Process incoming messages for a domain"""
        messages = await self.hub.receive_messages(domain_name, timeout)
        
        for message in messages:
            if message.message_type == MessageType.ENHANCEMENT_REQUEST and message.correlation_id:
                # Handle enhancement request
                await self._handle_enhancement_request(message)
            elif message.message_type == MessageType.ENHANCEMENT_RESPONSE and message.correlation_id:
                # Handle enhancement response
                await self._handle_enhancement_response(message)
            elif message.message_type == MessageType.RESPONSE and message.correlation_id:
                # Handle general response
                await self._handle_general_response(message)
    
    async def _handle_enhancement_request(self, message: Message):
        """Handle an incoming enhancement request"""
        # This would be processed by individual domains
        # For now, just log the request
        self._logger.debug(f"Enhancement request received by {message.receiver} from {message.sender}")
    
    async def _handle_enhancement_response(self, message: Message):
        """Handle an incoming enhancement response"""
        if message.correlation_id and message.correlation_id in self._pending_requests:
            future = self._pending_requests[message.correlation_id]
            if not future.done():
                future.set_result(message.content)
            del self._pending_requests[message.correlation_id]
    
    async def _handle_general_response(self, message: Message):
        """Handle a general response message"""
        if message.correlation_id and message.correlation_id in self._pending_requests:
            future = self._pending_requests[message.correlation_id]
            if not future.done():
                future.set_result(message.content)
            del self._pending_requests[message.correlation_id]


# Global communicator instance
communication_hub = ScalableCommunicationHub()
communicator = InterDomainCommunicator(communication_hub)


def get_communicator() -> InterDomainCommunicator:
    """Get the global inter-domain communicator"""
    return communicator