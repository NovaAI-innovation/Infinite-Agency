"""
Context management system for agent conversations.
Manages conversation history, context persistence, and state tracking.
"""
import asyncio
import json
from typing import Dict, Any, List, Optional, Tuple
from dataclasses import dataclass
from datetime import datetime
import hashlib
from ..utils.logger import get_logger


@dataclass
class ConversationTurn:
    """Represents a single turn in a conversation"""
    role: str  # 'user', 'assistant', 'system', 'tool'
    content: str
    timestamp: datetime
    metadata: Optional[Dict[str, Any]] = None
    turn_id: Optional[str] = None

    def __post_init__(self):
        if self.turn_id is None:
            self.turn_id = hashlib.md5((str(self.timestamp) + self.role + self.content).encode()).hexdigest()


@dataclass
class ConversationContext:
    """Represents the context of a conversation"""
    conversation_id: str
    turns: List[ConversationTurn]
    metadata: Dict[str, Any]
    created_at: datetime
    updated_at: datetime
    participants: List[str]
    tags: List[str]

    def __post_init__(self):
        if self.created_at is None:
            self.created_at = datetime.now()
        if self.updated_at is None:
            self.updated_at = datetime.now()


class ContextManager:
    """Manages conversation contexts and history"""
    
    def __init__(self, max_history_size: int = 1000):
        self.conversations: Dict[str, ConversationContext] = {}
        self.max_history_size = max_history_size
        self._lock = asyncio.Lock()
        self._logger = get_logger(__name__)
    
    async def create_conversation(self, conversation_id: str, participants: List[str], tags: List[str] = None) -> ConversationContext:
        """Create a new conversation context"""
        async with self._lock:
            if conversation_id in self.conversations:
                raise ValueError(f"Conversation {conversation_id} already exists")
            
            context = ConversationContext(
                conversation_id=conversation_id,
                turns=[],
                metadata={},
                created_at=datetime.now(),
                updated_at=datetime.now(),
                participants=participants,
                tags=tags or []
            )
            
            self.conversations[conversation_id] = context
            self._logger.info(f"Created conversation {conversation_id}")
            return context
    
    async def add_turn(self, conversation_id: str, role: str, content: str, metadata: Dict[str, Any] = None) -> ConversationTurn:
        """Add a turn to a conversation"""
        async with self._lock:
            if conversation_id not in self.conversations:
                raise ValueError(f"Conversation {conversation_id} does not exist")
            
            turn = ConversationTurn(
                role=role,
                content=content,
                timestamp=datetime.now(),
                metadata=metadata or {}
            )
            
            conversation = self.conversations[conversation_id]
            conversation.turns.append(turn)
            conversation.updated_at = datetime.now()
            
            # Trim history if it exceeds the maximum size
            if len(conversation.turns) > self.max_history_size:
                conversation.turns = conversation.turns[-self.max_history_size:]
            
            self._logger.debug(f"Added turn to conversation {conversation_id}")
            return turn
    
    async def get_conversation(self, conversation_id: str) -> Optional[ConversationContext]:
        """Get a conversation by ID"""
        return self.conversations.get(conversation_id)
    
    async def get_recent_turns(self, conversation_id: str, count: int = 5) -> List[ConversationTurn]:
        """Get the most recent turns from a conversation"""
        conversation = await self.get_conversation(conversation_id)
        if conversation:
            return conversation.turns[-count:]
        return []
    
    async def update_metadata(self, conversation_id: str, metadata: Dict[str, Any]):
        """Update metadata for a conversation"""
        async with self._lock:
            if conversation_id not in self.conversations:
                raise ValueError(f"Conversation {conversation_id} does not exist")
            
            conversation = self.conversations[conversation_id]
            conversation.metadata.update(metadata)
            conversation.updated_at = datetime.now()
    
    async def search_conversations(self, query: str, tags: List[str] = None) -> List[ConversationContext]:
        """Search conversations by content and/or tags"""
        results = []
        
        for conversation in self.conversations.values():
            # Check if tags match if provided
            if tags and not any(tag in conversation.tags for tag in tags):
                continue
            
            # Search in conversation turns
            for turn in conversation.turns:
                if query.lower() in turn.content.lower():
                    if conversation not in results:
                        results.append(conversation)
                    break  # Found a match in this conversation, no need to check other turns
        
        return results
    
    async def get_conversations_by_participant(self, participant: str) -> List[ConversationContext]:
        """Get all conversations involving a specific participant"""
        results = []
        for conversation in self.conversations.values():
            if participant in conversation.participants:
                results.append(conversation)
        return results
    
    async def delete_conversation(self, conversation_id: str) -> bool:
        """Delete a conversation"""
        async with self._lock:
            if conversation_id in self.conversations:
                del self.conversations[conversation_id]
                self._logger.info(f"Deleted conversation {conversation_id}")
                return True
            return False
    
    async def clear_all_conversations(self):
        """Clear all conversations"""
        async with self._lock:
            self.conversations.clear()
            self._logger.info("Cleared all conversations")
    
    async def export_conversation(self, conversation_id: str) -> str:
        """Export a conversation to JSON string"""
        conversation = await self.get_conversation(conversation_id)
        if not conversation:
            raise ValueError(f"Conversation {conversation_id} does not exist")
        
        # Convert to serializable format
        conv_dict = {
            "conversation_id": conversation.conversation_id,
            "turns": [
                {
                    "role": turn.role,
                    "content": turn.content,
                    "timestamp": turn.timestamp.isoformat(),
                    "metadata": turn.metadata,
                    "turn_id": turn.turn_id
                }
                for turn in conversation.turns
            ],
            "metadata": conversation.metadata,
            "created_at": conversation.created_at.isoformat(),
            "updated_at": conversation.updated_at.isoformat(),
            "participants": conversation.participants,
            "tags": conversation.tags
        }
        
        return json.dumps(conv_dict, indent=2)
    
    async def import_conversation(self, json_str: str) -> str:
        """Import a conversation from JSON string"""
        try:
            conv_dict = json.loads(json_str)
            
            # Reconstruct conversation
            turns = [
                ConversationTurn(
                    role=turn["role"],
                    content=turn["content"],
                    timestamp=datetime.fromisoformat(turn["timestamp"]),
                    metadata=turn.get("metadata", {}),
                    turn_id=turn.get("turn_id")
                )
                for turn in conv_dict["turns"]
            ]
            
            conversation = ConversationContext(
                conversation_id=conv_dict["conversation_id"],
                turns=turns,
                metadata=conv_dict["metadata"],
                created_at=datetime.fromisoformat(conv_dict["created_at"]),
                updated_at=datetime.fromisoformat(conv_dict["updated_at"]),
                participants=conv_dict["participants"],
                tags=conv_dict["tags"]
            )
            
            async with self._lock:
                self.conversations[conversation.conversation_id] = conversation
            
            self._logger.info(f"Imported conversation {conversation.conversation_id}")
            return conversation.conversation_id
        except Exception as e:
            self._logger.error(f"Error importing conversation: {e}")
            raise


# Global context manager instance
context_manager = ContextManager()


def get_context_manager() -> ContextManager:
    """Get the global context manager instance"""
    return context_manager