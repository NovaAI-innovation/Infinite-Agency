from typing import Dict, Any, List, Optional
from enum import Enum
from dataclasses import dataclass
from abc import ABC, abstractmethod
import asyncio
import json


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
    correlation_id: Optional[str] = None
    timestamp: float = 0.0
    metadata: Optional[Dict[str, Any]] = None


class CommunicationInterface(ABC):
    """Interface for inter-domain communication"""
    
    @abstractmethod
    async def send_message(self, message: Message) -> bool:
        """Send a message to another domain"""
        pass
    
    @abstractmethod
    async def receive_messages(self, domain_name: str) -> List[Message]:
        """Receive messages for a specific domain"""
        pass
    
    @abstractmethod
    async def broadcast_message(self, message: Message, exclude_sender: bool = True) -> List[bool]:
        """Broadcast a message to all domains"""
        pass


class InMemoryCommunicationHub(CommunicationInterface):
    """Simple in-memory communication hub for inter-domain messaging"""
    
    def __init__(self):
        self._message_queues: Dict[str, List[Message]] = {}
        self._registered_domains: List[str] = []
    
    def register_domain(self, domain_name: str):
        """Register a domain with the communication hub"""
        if domain_name not in self._registered_domains:
            self._registered_domains.append(domain_name)
            self._message_queues[domain_name] = []
    
    def unregister_domain(self, domain_name: str):
        """Unregister a domain from the communication hub"""
        if domain_name in self._registered_domains:
            self._registered_domains.remove(domain_name)
            if domain_name in self._message_queues:
                del self._message_queues[domain_name]
    
    async def send_message(self, message: Message) -> bool:
        """Send a message to a specific domain"""
        if message.receiver is None:
            # Broadcast message
            await self.broadcast_message(message)
            return True
        
        if message.receiver in self._message_queues:
            self._message_queues[message.receiver].append(message)
            return True
        else:
            return False  # Receiver not found
    
    async def receive_messages(self, domain_name: str) -> List[Message]:
        """Receive all messages for a specific domain"""
        if domain_name in self._message_queues:
            messages = self._message_queues[domain_name][:]
            # Clear the queue after reading
            self._message_queues[domain_name] = []
            return messages
        else:
            return []
    
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
    """Manages communication between domains"""
    
    def __init__(self, communication_hub: CommunicationInterface):
        self.hub = communication_hub
        self._pending_requests: Dict[str, asyncio.Future] = {}
    
    async def request_enhancement(self, sender: str, target_domain: str, content: Any) -> Optional[Any]:
        """Request enhancement from a specific domain"""
        correlation_id = f"enh_{sender}_{target_domain}_{hash(content) % 10000}"
        
        # Create a future to hold the response
        future = asyncio.Future()
        self._pending_requests[correlation_id] = future
        
        # Send enhancement request
        message = Message(
            message_type=MessageType.ENHANCEMENT_REQUEST,
            sender=sender,
            receiver=target_domain,
            content=content,
            correlation_id=correlation_id
        )
        
        success = await self.hub.send_message(message)
        
        if not success:
            # Clean up the future if sending failed
            del self._pending_requests[correlation_id]
            return None
        
        try:
            # Wait for response with timeout
            result = await asyncio.wait_for(future, timeout=10.0)
            return result
        except asyncio.TimeoutError:
            # Clean up the future on timeout
            if correlation_id in self._pending_requests:
                del self._pending_requests[correlation_id]
            return None
    
    async def send_notification(self, sender: str, content: Any, target_domains: Optional[List[str]] = None):
        """Send a notification to one or more domains"""
        message = Message(
            message_type=MessageType.NOTIFICATION,
            sender=sender,
            receiver=None,  # Will be set during broadcast
            content=content
        )
        
        if target_domains:
            # Send to specific domains
            for domain in target_domains:
                msg_copy = Message(
                    message_type=message.message_type,
                    sender=message.sender,
                    receiver=domain,
                    content=message.content,
                    metadata=message.metadata
                )
                await self.hub.send_message(msg_copy)
        else:
            # Broadcast to all domains
            await self.hub.broadcast_message(message)
    
    async def handle_incoming_messages(self, domain_name: str):
        """Process incoming messages for a domain"""
        messages = await self.hub.receive_messages(domain_name)
        
        for message in messages:
            if message.message_type == MessageType.ENHANCEMENT_REQUEST and message.correlation_id:
                # Handle enhancement request
                await self._handle_enhancement_request(message)
            elif message.message_type == MessageType.ENHANCEMENT_RESPONSE and message.correlation_id:
                # Handle enhancement response
                await self._handle_enhancement_response(message)
    
    async def _handle_enhancement_request(self, message: Message):
        """Handle an incoming enhancement request"""
        # This would be implemented by individual domains
        # For now, just log the request
        print(f"Enhancement request received by {message.receiver} from {message.sender}: {message.content}")
    
    async def _handle_enhancement_response(self, message: Message):
        """Handle an incoming enhancement response"""
        if message.correlation_id and message.correlation_id in self._pending_requests:
            future = self._pending_requests[message.correlation_id]
            if not future.done():
                future.set_result(message.content)
            del self._pending_requests[message.correlation_id]


# Global communicator instance
communication_hub = InMemoryCommunicationHub()
communicator = InterDomainCommunicator(communication_hub)


def get_communicator() -> InterDomainCommunicator:
    """Get the global inter-domain communicator"""
    return communicator