from typing import Dict, Any
from ...core.base_domain import BaseDomain, DomainInput, DomainOutput
import asyncio
import json


class CommunicationDomain(BaseDomain):
    """Domain responsible for sending notifications to users via agent mail API"""

    def __init__(self, name: str = "communication", description: str = "Handles sending notifications to users via agent mail API for task completion, milestones, and other events", resource_manager=None, cache_enabled: bool = True):
        super().__init__(name=name, description=description, resource_manager=resource_manager, cache_enabled=cache_enabled)
        self.notification_types = [
            "task_completion", "milestone_reached", "error_occurred", 
            "status_update", "custom_event", "reminder", "alert"
        ]
        self.channels = ["email", "sms", "push_notification", "in_app", "webhook"]
        self.priority_levels = ["low", "normal", "high", "critical"]
        self.communication_templates = {
            "task_completion": self._generate_task_completion_template,
            "milestone_reached": self._generate_milestone_template,
            "error_occurred": self._generate_error_template,
            "status_update": self._generate_status_update_template,
            "reminder": self._generate_reminder_template,
            "alert": self._generate_alert_template
        }

    async def execute(self, input_data: DomainInput) -> DomainOutput:
        """Send notifications based on the input specification"""
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

                # Determine the type of notification to send
                notification_type = self._determine_notification_type(query)
                channel = params.get("channel", context.get("channel", "email"))
                priority = params.get("priority", context.get("priority", "normal"))
                recipient = params.get("recipient", context.get("recipient", "default_user"))

                if notification_type not in self.notification_types:
                    return DomainOutput(
                        success=False,
                        error=f"Notification type '{notification_type}' not supported. Available types: {', '.join(self.notification_types)}"
                    )

                if channel not in self.channels:
                    return DomainOutput(
                        success=False,
                        error=f"Channel '{channel}' not supported. Available channels: {', '.join(self.channels)}"
                    )

                # Generate the notification content
                notification_content = await self._generate_notification_content(notification_type, query, channel, priority, params)

                # Send the notification via agent mail API
                send_result = await self._send_via_agent_mail_api(
                    recipient=recipient,
                    subject=notification_content.get("subject", f"Notification: {notification_type}"),
                    body=notification_content.get("body", f"Notification content for {notification_type}"),
                    channel=channel,
                    priority=priority,
                    metadata=notification_content.get("metadata", {})
                )

                return DomainOutput(
                    success=send_result.get("success", False),
                    data={
                        "notification_type": notification_type,
                        "channel": channel,
                        "priority": priority,
                        "recipient": recipient,
                        "content": notification_content,
                        "send_result": send_result,
                        "original_query": query
                    },
                    metadata={
                        "domain": self.name,
                        "notification_sent": send_result.get("success", False)
                    }
                )
            finally:
                # Always release resources after execution
                self.resource_manager.release_resources(self.name)
        except Exception as e:
            return DomainOutput(
                success=False,
                error=f"Notification sending failed: {str(e)}"
            )

    def can_handle(self, input_data: DomainInput) -> bool:
        """Determine if this domain can handle the input"""
        query = input_data.query.lower()

        # Check for keywords that suggest notification sending
        notification_keywords = [
            "notify", "notification", "send message", "alert", "inform", 
            "email", "sms", "message", "reminder", "update", "task completion",
            "milestone", "completion", "done", "finished", "achieved",
            "send notification", "send alert", "send reminder", "send update",
            "contact user", "reach out", "communicate", "broadcast"
        ]

        return any(keyword in query for keyword in notification_keywords)

    def _determine_notification_type(self, query: str) -> str:
        """Determine what type of notification to send based on the query"""
        if any(word in query for word in ["task", "completion", "done", "finished"]):
            return "task_completion"
        elif any(word in query for word in ["milestone", "achieved", "reached", "completed"]):
            return "milestone_reached"
        elif any(word in query for word in ["error", "failure", "failed", "problem"]):
            return "error_occurred"
        elif any(word in query for word in ["update", "status", "progress"]):
            return "status_update"
        elif any(word in query for word in ["reminder", "remind", "remember"]):
            return "reminder"
        elif any(word in query for word in ["alert", "urgent", "critical"]):
            return "alert"
        else:
            return "custom_event"

    async def _generate_notification_content(self, notification_type: str, query: str, channel: str, priority: str, params: Dict[str, Any]) -> Dict[str, Any]:
        """Generate appropriate notification content based on type and parameters"""
        if notification_type in self.communication_templates:
            return await self.communication_templates[notification_type](query, channel, priority, params)
        else:
            return await self._generate_generic_notification_content(query, notification_type, channel, priority, params)

    async def _generate_task_completion_template(self, query: str, channel: str, priority: str, params: Dict[str, Any]) -> Dict[str, Any]:
        """Generate content for task completion notification"""
        task_name = params.get("task_name", "Unnamed Task")
        task_id = params.get("task_id", "unknown")
        completion_time = params.get("completion_time", "just now")
        
        subject = f"Task Completed: {task_name}"
        body = f"""Task '{task_name}' (ID: {task_id}) has been completed successfully.

Details:
- Task: {task_name}
- ID: {task_id}
- Completed at: {completion_time}
- Priority: {priority.title()}

Next steps: The task has been marked as completed in the system.

Thank you for using our service."""

        return {
            "subject": subject,
            "body": body,
            "metadata": {
                "notification_type": "task_completion",
                "task_name": task_name,
                "task_id": task_id,
                "completion_time": completion_time,
                "priority": priority
            }
        }

    async def _generate_milestone_template(self, query: str, channel: str, priority: str, params: Dict[str, Any]) -> Dict[str, Any]:
        """Generate content for milestone notification"""
        milestone_name = params.get("milestone_name", "Unnamed Milestone")
        project_name = params.get("project_name", "Unnamed Project")
        milestone_percentage = params.get("percentage", "100%")
        
        subject = f"Milestone Achieved: {milestone_name}"
        body = f"""Milestone '{milestone_name}' in project '{project_name}' has been achieved!

Achievement Details:
- Milestone: {milestone_name}
- Project: {project_name}
- Progress: {milestone_percentage}
- Priority: {priority.title()}

Congratulations on reaching this important milestone!

Next steps: The project continues to the next phase."""

        return {
            "subject": subject,
            "body": body,
            "metadata": {
                "notification_type": "milestone_reached",
                "milestone_name": milestone_name,
                "project_name": project_name,
                "percentage": milestone_percentage,
                "priority": priority
            }
        }

    async def _generate_error_template(self, query: str, channel: str, priority: str, params: Dict[str, Any]) -> Dict[str, Any]:
        """Generate content for error notification"""
        error_message = params.get("error_message", "An error occurred")
        error_code = params.get("error_code", "UNKNOWN")
        affected_component = params.get("affected_component", "System")
        
        subject = f"Error Alert: {error_message[:50]}..."
        body = f"""An error has occurred in the system:

Error Details:
- Message: {error_message}
- Code: {error_code}
- Affected Component: {affected_component}
- Priority: {priority.title()}

Action Required:
- Check system logs for more details
- Investigate and resolve the issue
- Contact support if needed

This is an automated error notification."""

        return {
            "subject": subject,
            "body": body,
            "metadata": {
                "notification_type": "error_occurred",
                "error_message": error_message,
                "error_code": error_code,
                "affected_component": affected_component,
                "priority": priority
            }
        }

    async def _generate_status_update_template(self, query: str, channel: str, priority: str, params: Dict[str, Any]) -> Dict[str, Any]:
        """Generate content for status update notification"""
        status_message = params.get("status_message", "Status update")
        component_name = params.get("component_name", "System")
        update_time = params.get("update_time", "now")
        
        subject = f"Status Update: {component_name}"
        body = f"""Status update for '{component_name}':

Update Details:
- Status: {status_message}
- Component: {component_name}
- Time: {update_time}
- Priority: {priority.title()}

Additional Information:
{params.get('details', 'No additional details provided.')}"""

        return {
            "subject": subject,
            "body": body,
            "metadata": {
                "notification_type": "status_update",
                "status_message": status_message,
                "component_name": component_name,
                "update_time": update_time,
                "priority": priority
            }
        }

    async def _generate_reminder_template(self, query: str, channel: str, priority: str, params: Dict[str, Any]) -> Dict[str, Any]:
        """Generate content for reminder notification"""
        reminder_title = params.get("reminder_title", "Upcoming Event")
        due_date = params.get("due_date", "soon")
        description = params.get("description", "Event details")
        
        subject = f"Reminder: {reminder_title}"
        body = f"""This is a reminder about an upcoming event/task:

Reminder Details:
- Title: {reminder_title}
- Due Date: {due_date}
- Description: {description}
- Priority: {priority.title()}

Action Required:
- Review the task/event
- Take necessary actions before the due date

Don't forget to complete this on time!"""

        return {
            "subject": subject,
            "body": body,
            "metadata": {
                "notification_type": "reminder",
                "reminder_title": reminder_title,
                "due_date": due_date,
                "description": description,
                "priority": priority
            }
        }

    async def _generate_alert_template(self, query: str, channel: str, priority: str, params: Dict[str, Any]) -> Dict[str, Any]:
        """Generate content for alert notification"""
        alert_title = params.get("alert_title", "System Alert")
        alert_level = params.get("alert_level", priority)
        alert_description = params.get("alert_description", "Alert details")
        
        subject = f"ALERT: {alert_title}"
        body = f"""URGENT SYSTEM ALERT:

Alert Details:
- Title: {alert_title}
- Level: {alert_level.upper()}
- Description: {alert_description}
- Priority: {priority.title()}

IMMEDIATE ACTION REQUIRED:
- Review the alert details
- Take corrective measures
- Escalate if necessary

This is a critical system alert requiring immediate attention."""

        return {
            "subject": subject,
            "body": body,
            "metadata": {
                "notification_type": "alert",
                "alert_title": alert_title,
                "alert_level": alert_level,
                "alert_description": alert_description,
                "priority": priority
            }
        }

    async def _generate_generic_notification_content(self, query: str, notification_type: str, channel: str, priority: str, params: Dict[str, Any]) -> Dict[str, Any]:
        """Generate generic notification content when specific type isn't determined"""
        subject = f"Notification: {notification_type.replace('_', ' ').title()}"
        body = f"""You have received a notification:

Query: {query}
Type: {notification_type.replace('_', ' ').title()}
Channel: {channel}
Priority: {priority.title()}

Additional details:
{json.dumps(params, indent=2)}

This is an automated notification from the communication system."""

        return {
            "subject": subject,
            "body": body,
            "metadata": {
                "notification_type": notification_type,
                "channel": channel,
                "priority": priority,
                "query": query,
                "params": params
            }
        }

    async def _send_via_agent_mail_api(self, recipient: str, subject: str, body: str, channel: str, priority: str, metadata: Dict[str, Any]) -> Dict[str, Any]:
        """Send notification via agent mail API (simulated)"""
        # In a real implementation, this would connect to the actual agent mail API
        # For now, we'll simulate the API call
        
        # Simulate API call delay
        await asyncio.sleep(0.1)
        
        # Simulate sending result
        success = True  # In real implementation, this would come from the API response
        
        return {
            "success": success,
            "recipient": recipient,
            "channel": channel,
            "priority": priority,
            "message_id": f"msg_{hash(subject + recipient + str(metadata)) % 1000000}",
            "timestamp": asyncio.get_event_loop().time(),
            "delivery_status": "delivered" if success else "failed",
            "metadata": metadata
        }

    async def _enhance_with_other_domains(self, result_data: Dict[str, Any], input_data: DomainInput) -> Dict[str, Any]:
        """Allow other domains to enhance the communication result"""
        # In a real implementation, this would coordinate with other domains
        # For now, we'll just return the original result
        return result_data