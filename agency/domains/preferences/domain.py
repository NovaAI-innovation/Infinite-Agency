from typing import Dict, Any, List, Optional
from ...core.base_domain import BaseDomain, DomainInput, DomainOutput
import asyncio
import json
from datetime import datetime


class PreferencesDomain(BaseDomain):
    """Domain responsible for managing user notification preferences and CRUD operations for preferences"""

    def __init__(self, name: str = "preferences", description: str = "Manages user notification preferences and CRUD operations for notification event preferences", resource_manager=None, cache_enabled: bool = True):
        super().__init__(name=name, description=description, resource_manager=resource_manager, cache_enabled=cache_enabled)
        self.preference_types = ["notification", "communication", "alert", "reminder", "update"]
        self.event_types = [
            "task_completion", "milestone_reached", "error_occurred", 
            "status_update", "custom_event", "reminder", "alert"
        ]
        self.channels = ["email", "sms", "push_notification", "in_app", "webhook"]
        self.storage_backends = ["json_file", "sqlite", "memory", "redis"]
        
        # Initialize storage (in-memory for this example)
        self.preferences_storage = {}
        
        self.preferences_templates = {
            "create_preference": self._handle_create_preference,
            "read_preference": self._handle_read_preference,
            "update_preference": self._handle_update_preference,
            "delete_preference": self._handle_delete_preference,
            "list_preferences": self._handle_list_preferences
        }

    async def execute(self, input_data: DomainInput) -> DomainOutput:
        """Handle CRUD operations for user notification preferences"""
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

                # Determine the type of CRUD operation to perform
                operation_type = self._determine_operation_type(query)
                user_id = params.get("user_id", context.get("user_id", "default_user"))
                preference_type = params.get("preference_type", context.get("preference_type", "notification"))
                event_type = params.get("event_type", context.get("event_type", "task_completion"))

                if operation_type not in self.preferences_templates:
                    return DomainOutput(
                        success=False,
                        error=f"Operation type '{operation_type}' not supported. Available operations: {', '.join(self.preferences_templates.keys())}"
                    )

                # Execute the appropriate CRUD operation
                result = await self.preferences_templates[operation_type](
                    user_id=user_id,
                    preference_type=preference_type,
                    event_type=event_type,
                    params=params
                )

                return DomainOutput(
                    success=result.get("success", False),
                    data={
                        "operation_type": operation_type,
                        "user_id": user_id,
                        "preference_type": preference_type,
                        "event_type": event_type,
                        "result": result,
                        "original_query": query
                    },
                    metadata={
                        "domain": self.name,
                        "operation_performed": operation_type
                    }
                )
            finally:
                # Always release resources after execution
                self.resource_manager.release_resources(self.name)
        except Exception as e:
            return DomainOutput(
                success=False,
                error=f"Preferences operation failed: {str(e)}"
            )

    def can_handle(self, input_data: DomainInput) -> bool:
        """Determine if this domain can handle the input"""
        query = input_data.query.lower()

        # Check for keywords that suggest preference management
        preference_keywords = [
            "preference", "preferences", "settings", "configuration", 
            "notification settings", "notification preferences", 
            "user settings", "user preferences", "customize",
            "configure", "set", "update", "change", "modify",
            "get", "retrieve", "fetch", "read", "view",
            "delete", "remove", "unsubscribe", "opt-out",
            "enable", "disable", "toggle", "switch",
            "manage", "control", "adjust", "personalize"
        ]

        return any(keyword in query for keyword in preference_keywords)

    def _determine_operation_type(self, query: str) -> str:
        """Determine what type of CRUD operation to perform based on the query"""
        if any(word in query for word in ["create", "add", "set", "configure", "enable"]):
            return "create_preference"
        elif any(word in query for word in ["get", "read", "fetch", "retrieve", "view", "show"]):
            return "read_preference"
        elif any(word in query for word in ["update", "modify", "change", "adjust", "edit"]):
            return "update_preference"
        elif any(word in query for word in ["delete", "remove", "clear", "reset", "disable"]):
            return "delete_preference"
        elif any(word in query for word in ["list", "all", "get all", "show all"]):
            return "list_preferences"
        else:
            return "read_preference"  # Default to read

    async def _handle_create_preference(self, user_id: str, preference_type: str, event_type: str, params: Dict[str, Any]) -> Dict[str, Any]:
        """Create a new user preference"""
        try:
            # Extract preference details from parameters
            channels = params.get("channels", ["email"])
            enabled = params.get("enabled", True)
            priority = params.get("priority", "normal")
            custom_message = params.get("custom_message", "")
            
            # Create preference object
            preference = {
                "user_id": user_id,
                "preference_type": preference_type,
                "event_type": event_type,
                "channels": channels,
                "enabled": enabled,
                "priority": priority,
                "custom_message": custom_message,
                "created_at": datetime.now().isoformat(),
                "updated_at": datetime.now().isoformat()
            }
            
            # Store in preferences (using user_id and event_type as key)
            key = f"{user_id}:{event_type}"
            self.preferences_storage[key] = preference
            
            return {
                "success": True,
                "message": f"Preference created for user {user_id} and event {event_type}",
                "preference": preference,
                "key": key
            }
        except Exception as e:
            return {
                "success": False,
                "error": f"Failed to create preference: {str(e)}"
            }

    async def _handle_read_preference(self, user_id: str, preference_type: str, event_type: str, params: Dict[str, Any]) -> Dict[str, Any]:
        """Read a user preference"""
        try:
            # Retrieve preference from storage
            key = f"{user_id}:{event_type}"
            preference = self.preferences_storage.get(key)
            
            if preference:
                return {
                    "success": True,
                    "message": f"Preference found for user {user_id} and event {event_type}",
                    "preference": preference,
                    "key": key
                }
            else:
                return {
                    "success": False,
                    "message": f"No preference found for user {user_id} and event {event_type}",
                    "key": key
                }
        except Exception as e:
            return {
                "success": False,
                "error": f"Failed to read preference: {str(e)}"
            }

    async def _handle_update_preference(self, user_id: str, preference_type: str, event_type: str, params: Dict[str, Any]) -> Dict[str, Any]:
        """Update an existing user preference"""
        try:
            # Retrieve existing preference
            key = f"{user_id}:{event_type}"
            existing_preference = self.preferences_storage.get(key)
            
            if not existing_preference:
                return {
                    "success": False,
                    "message": f"No existing preference found for user {user_id} and event {event_type}"
                }
            
            # Update fields based on provided params
            if "channels" in params:
                existing_preference["channels"] = params["channels"]
            if "enabled" in params:
                existing_preference["enabled"] = params["enabled"]
            if "priority" in params:
                existing_preference["priority"] = params["priority"]
            if "custom_message" in params:
                existing_preference["custom_message"] = params["custom_message"]
            
            # Update timestamp
            existing_preference["updated_at"] = datetime.now().isoformat()
            
            # Save updated preference
            self.preferences_storage[key] = existing_preference
            
            return {
                "success": True,
                "message": f"Preference updated for user {user_id} and event {event_type}",
                "preference": existing_preference,
                "key": key
            }
        except Exception as e:
            return {
                "success": False,
                "error": f"Failed to update preference: {str(e)}"
            }

    async def _handle_delete_preference(self, user_id: str, preference_type: str, event_type: str, params: Dict[str, Any]) -> Dict[str, Any]:
        """Delete a user preference"""
        try:
            # Remove preference from storage
            key = f"{user_id}:{event_type}"
            if key in self.preferences_storage:
                deleted_preference = self.preferences_storage.pop(key)
                return {
                    "success": True,
                    "message": f"Preference deleted for user {user_id} and event {event_type}",
                    "deleted_preference": deleted_preference,
                    "key": key
                }
            else:
                return {
                    "success": False,
                    "message": f"No preference found for user {user_id} and event {event_type} to delete"
                }
        except Exception as e:
            return {
                "success": False,
                "error": f"Failed to delete preference: {str(e)}"
            }

    async def _handle_list_preferences(self, user_id: str, preference_type: str, event_type: str, params: Dict[str, Any]) -> Dict[str, Any]:
        """List all preferences for a user"""
        try:
            # Find all preferences for the user
            user_preferences = []
            for key, preference in self.preferences_storage.items():
                if key.startswith(f"{user_id}:"):
                    user_preferences.append({
                        "key": key,
                        "preference": preference
                    })
            
            return {
                "success": True,
                "message": f"Found {len(user_preferences)} preferences for user {user_id}",
                "preferences": user_preferences,
                "count": len(user_preferences)
            }
        except Exception as e:
            return {
                "success": False,
                "error": f"Failed to list preferences: {str(e)}"
            }

    async def get_user_preference(self, user_id: str, event_type: str) -> Optional[Dict[str, Any]]:
        """Helper method to get a specific user preference"""
        key = f"{user_id}:{event_type}"
        return self.preferences_storage.get(key)

    async def is_notification_enabled(self, user_id: str, event_type: str) -> bool:
        """Check if notifications are enabled for a specific user and event type"""
        preference = await self.get_user_preference(user_id, event_type)
        if preference:
            return preference.get("enabled", True)  # Default to True if not specified
        return True  # Default to True if no preference exists

    async def get_notification_channels(self, user_id: str, event_type: str) -> List[str]:
        """Get notification channels for a specific user and event type"""
        preference = await self.get_user_preference(user_id, event_type)
        if preference:
            return preference.get("channels", ["email"])  # Default to email if not specified
        return ["email"]  # Default to email if no preference exists

    async def get_notification_priority(self, user_id: str, event_type: str) -> str:
        """Get notification priority for a specific user and event type"""
        preference = await self.get_user_preference(user_id, event_type)
        if preference:
            return preference.get("priority", "normal")  # Default to normal if not specified
        return "normal"  # Default to normal if no preference exists

    async def _enhance_with_other_domains(self, result_data: Dict[str, Any], input_data: DomainInput) -> Dict[str, Any]:
        """Allow other domains to enhance the preferences result"""
        # In a real implementation, this would coordinate with other domains
        # For now, we'll just return the original result
        return result_data