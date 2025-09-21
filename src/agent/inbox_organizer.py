"""
Inbox Organization Agent - demonstrates workflow automation capabilities.

This agent specializes in organizing and managing email inbox structure.
It shows how agents can perform repetitive tasks and maintain organizational systems.
"""

import logging
from typing import Dict, List, Any, Tuple
from datetime import datetime, timedelta
from collections import defaultdict

from .base import BaseAgent, Tool, ToolResult
from ..tools.email_tools import EmailMessage, email_tools

logger = logging.getLogger(__name__)


class InboxOrganizer(BaseAgent):
    """
    Sub-agent that specializes in inbox organization and maintenance.
    
    This demonstrates:
    1. Workflow automation
    2. Rule-based organization systems
    3. Batch processing capabilities
    4. Maintenance and cleanup tasks
    """
    
    def __init__(self):
        super().__init__(
            name="InboxOrganizer",
            description="Organizes and maintains email inbox structure automatically"
        )
        
        # Organization rules
        self.organization_rules = {
            "archive_after_days": {
                "newsletter": 7,
                "promotional": 3,
                "general": 30,
                "work": 90,
                "personal": 180
            },
            "auto_labels": {
                "urgent": ["urgent", "asap", "emergency"],
                "meetings": ["meeting", "calendar", "appointment"],
                "receipts": ["receipt", "invoice", "payment"],
                "travel": ["flight", "hotel", "reservation"],
                "finance": ["bank", "credit card", "statement"]
            },
            "folder_structure": [
                "Action Required",
                "Waiting For Response", 
                "Archive",
                "Newsletters",
                "Receipts",
                "Travel",
                "Projects"
            ]
        }
        
        # Priority settings
        self.vip_senders = [
            "boss@company.com",
            "client@important.com",
            "family@personal.com"
        ]
        
        # Register organization tools
        self._register_organization_tools()
    
    def _register_organization_tools(self):
        """Register tools specific to inbox organization."""
        
        def apply_auto_labels(emails: List[EmailMessage]) -> Dict[str, List[str]]:
            """Automatically apply labels based on content."""
            labeling_results = defaultdict(list)
            
            for email in emails:
                text = f"{email.subject} {email.body}".lower()
                
                for label, keywords in self.organization_rules["auto_labels"].items():
                    if any(keyword in text for keyword in keywords):
                        labeling_results[label].append(email.id)
                        
                        # Apply the label (simulated)
                        email_tools.add_label(email.id, label)
                        logger.info(f"Applied label '{label}' to email {email.id}")
            
            return dict(labeling_results)
        
        def identify_archive_candidates(emails: List[EmailMessage]) -> List[Dict[str, Any]]:
            """Identify emails that should be archived based on age and category."""
            candidates = []
            now = datetime.now()
            
            for email in emails:
                # Determine email category (would use classifier results)
                category = self._guess_email_category(email)
                
                # Check if email is old enough to archive
                archive_days = self.organization_rules["archive_after_days"].get(category, 30)
                age_threshold = now - timedelta(days=archive_days)
                
                if email.date < age_threshold:
                    candidates.append({
                        "email_id": email.id,
                        "subject": email.subject,
                        "sender": email.sender,
                        "category": category,
                        "age_days": (now - email.date).days,
                        "threshold_days": archive_days
                    })
            
            return candidates
        
        def organize_by_sender(emails: List[EmailMessage]) -> Dict[str, List[str]]:
            """Group emails by sender for batch processing."""
            sender_groups = defaultdict(list)
            
            for email in emails:
                # Clean sender email
                sender = email.sender.lower().strip()
                if "<" in sender and ">" in sender:
                    sender = sender.split("<")[1].split(">")[0]
                
                sender_groups[sender].append({
                    "id": email.id,
                    "subject": email.subject,
                    "date": email.date.isoformat()
                })
            
            return dict(sender_groups)
        
        def create_smart_folders(emails: List[EmailMessage]) -> Dict[str, int]:
            """Create and populate smart folders based on email patterns."""
            folder_assignments = defaultdict(int)
            
            for email in emails:
                text = f"{email.subject} {email.body}".lower()
                
                # Action Required folder
                if any(phrase in text for phrase in ["please", "action required", "need", "asap"]):
                    folder_assignments["Action Required"] += 1
                
                # Waiting For Response folder
                elif any(phrase in text for phrase in ["following up", "any update", "status"]):
                    folder_assignments["Waiting For Response"] += 1
                
                # Newsletters folder
                elif any(phrase in text for phrase in ["newsletter", "unsubscribe", "digest"]):
                    folder_assignments["Newsletters"] += 1
                
                # Receipts folder
                elif any(phrase in text for phrase in ["receipt", "invoice", "payment", "order"]):
                    folder_assignments["Receipts"] += 1
                
                # Travel folder
                elif any(phrase in text for phrase in ["flight", "hotel", "reservation", "booking"]):
                    folder_assignments["Travel"] += 1
                
                # Projects folder (would be customized based on project names)
                elif any(phrase in text for phrase in ["project", "milestone", "deliverable"]):
                    folder_assignments["Projects"] += 1
                
                else:
                    folder_assignments["General"] += 1
            
            return dict(folder_assignments)
        
        def prioritize_vip_emails(emails: List[EmailMessage]) -> List[Dict[str, Any]]:
            """Identify and prioritize emails from VIP senders."""
            vip_emails = []
            
            for email in emails:
                sender_email = email.sender.lower()
                
                # Check if sender is in VIP list
                is_vip = any(vip.lower() in sender_email for vip in self.vip_senders)
                
                if is_vip:
                    vip_emails.append({
                        "email_id": email.id,
                        "subject": email.subject,
                        "sender": email.sender,
                        "date": email.date.isoformat(),
                        "vip_reason": "Known VIP sender"
                    })
                
                # Also check for high-priority keywords
                elif any(word in email.subject.lower() for word in ["urgent", "important", "asap"]):
                    vip_emails.append({
                        "email_id": email.id,
                        "subject": email.subject,
                        "sender": email.sender,
                        "date": email.date.isoformat(),
                        "vip_reason": "Urgent keywords detected"
                    })
            
            return vip_emails
        
        def clean_duplicate_emails(emails: List[EmailMessage]) -> List[str]:
            """Identify potential duplicate emails for cleanup."""
            seen_combinations = {}
            duplicates = []
            
            for email in emails:
                # Create signature based on subject, sender, and approximate content
                signature = (
                    email.subject.lower().strip(),
                    email.sender.lower().strip(),
                    len(email.body),  # Simple content similarity
                    email.date.date()  # Same day
                )
                
                if signature in seen_combinations:
                    duplicates.append(email.id)
                    logger.info(f"Potential duplicate found: {email.id}")
                else:
                    seen_combinations[signature] = email.id
            
            return duplicates
        
        # Register all tools
        self.register_tool(Tool(
            name="apply_labels",
            description="Apply automatic labels to emails",
            function=apply_auto_labels
        ))
        
        self.register_tool(Tool(
            name="find_archive_candidates",
            description="Find emails that should be archived",
            function=identify_archive_candidates
        ))
        
        self.register_tool(Tool(
            name="organize_by_sender",
            description="Group emails by sender",
            function=organize_by_sender
        ))
        
        self.register_tool(Tool(
            name="create_folders",
            description="Create smart folders and categorize emails",
            function=create_smart_folders
        ))
        
        self.register_tool(Tool(
            name="prioritize_vips",
            description="Identify VIP emails for priority handling",
            function=prioritize_vip_emails
        ))
        
        self.register_tool(Tool(
            name="clean_duplicates",
            description="Find and flag duplicate emails",
            function=clean_duplicate_emails
        ))
    
    def _guess_email_category(self, email: EmailMessage) -> str:
        """Simple email categorization for organization rules."""
        text = f"{email.subject} {email.body}".lower()
        
        if any(word in text for word in ["newsletter", "unsubscribe"]):
            return "newsletter"
        elif any(word in text for word in ["sale", "discount", "offer"]):
            return "promotional"
        elif any(word in text for word in ["project", "work", "meeting"]):
            return "work"
        elif any(word in email.sender.lower() for word in ["family", "friend"]):
            return "personal"
        else:
            return "general"
    
    def perceive(self) -> Dict[str, Any]:
        """
        Perception: Assess current inbox state and organization needs.
        """
        # Get all emails for organization analysis
        emails = email_tools.fetch_recent_emails(limit=100)
        
        # Basic inbox statistics
        total_emails = len(emails)
        unread_count = sum(1 for email in emails if not email.is_read)
        today_count = sum(1 for email in emails if email.date.date() == datetime.now().date())
        
        return {
            "total_emails": total_emails,
            "unread_count": unread_count,
            "emails_today": today_count,
            "emails_for_organization": [email.to_dict() for email in emails],
            "inbox_health_score": self._calculate_inbox_health(emails),
            "timestamp": datetime.now().isoformat()
        }
    
    def think(self, perception: Dict[str, Any]) -> List[Dict[str, Any]]:
        """
        Reasoning: Plan organization strategy based on inbox analysis.
        """
        emails_data = perception.get("emails_for_organization", [])
        total_emails = perception.get("total_emails", 0)
        
        # Reconstruct EmailMessage objects
        emails = []
        for email_data in emails_data:
            emails.append(EmailMessage(
                id=email_data["id"],
                subject=email_data["subject"],
                sender=email_data["sender"],
                recipients=email_data["recipients"],
                body=email_data["body"],
                html_body=email_data.get("html_body"),
                date=datetime.fromisoformat(email_data["date"]),
                labels=email_data.get("labels", []),
                is_read=email_data.get("is_read", False),
                is_important=email_data.get("is_important", False),
                attachments=email_data.get("attachments", [])
            ))
        
        actions = []
        
        # Plan organization tasks based on inbox size and health
        if total_emails > 0:
            actions.append({
                "type": "inbox_organization",
                "emails": emails,
                "tasks": [
                    "apply_labels",
                    "prioritize_vips",
                    "create_folders",
                    "organize_by_sender"
                ]
            })
            
            # Add maintenance tasks if inbox is large
            if total_emails > 50:
                actions.append({
                    "type": "inbox_maintenance",
                    "emails": emails,
                    "tasks": [
                        "find_archive_candidates",
                        "clean_duplicates"
                    ]
                })
        
        logger.info(f"Planned {len(actions)} organization workflows")
        return actions
    
    def act(self, actions: List[Dict[str, Any]]) -> List[ToolResult]:
        """
        Action: Execute inbox organization tasks.
        """
        results = []
        
        for action in actions:
            emails = action["emails"]
            action_type = action["type"]
            
            organization_result = {
                "action_type": action_type,
                "emails_processed": len(emails),
                "timestamp": datetime.now().isoformat()
            }
            
            # Execute each organization task
            for task in action["tasks"]:
                tool_result = self.use_tool(task, emails=emails)
                if tool_result.success:
                    organization_result[task] = tool_result.result
                else:
                    organization_result[task] = f"Error: {tool_result.error}"
            
            # Store organization results
            self.memory.store_long_term(
                f"organization_{action_type}_{datetime.now().strftime('%Y%m%d_%H%M%S')}", 
                organization_result
            )
            
            results.append(ToolResult(
                success=True,
                result=organization_result,
                metadata={"action_type": action_type, "agent": self.name}
            ))
        
        logger.info(f"Completed {len(results)} organization workflows")
        return results
    
    def _calculate_inbox_health(self, emails: List[EmailMessage]) -> float:
        """Calculate a health score for the inbox (0-100)."""
        if not emails:
            return 100.0
        
        score = 100.0
        now = datetime.now()
        
        # Penalize for too many emails
        if len(emails) > 100:
            score -= min(20, (len(emails) - 100) / 10)
        
        # Penalize for old unread emails
        old_unread = sum(1 for email in emails 
                        if not email.is_read and (now - email.date).days > 7)
        score -= min(30, old_unread * 2)
        
        # Penalize for lack of organization (no labels)
        unlabeled = sum(1 for email in emails if not email.labels)
        score -= min(20, (unlabeled / len(emails)) * 20)
        
        return max(0, score)
    
    def get_organization_report(self) -> Dict[str, Any]:
        """Generate comprehensive inbox organization report."""
        # Analyze recent organization activities
        org_activities = [
            event for event in self.memory.short_term[-20:]
            if event.get("type") == "tool_usage"
        ]
        
        # Get latest organization results
        latest_results = {}
        for key, value in self.memory.long_term.items():
            if key.startswith("organization_"):
                latest_results[key] = value
        
        return {
            "agent_status": self.get_status(),
            "recent_activities": len(org_activities),
            "organization_results": latest_results,
            "health_metrics": {
                "last_cleanup": "N/A",  # Would track actual cleanup times
                "auto_labels_applied": sum(1 for activity in org_activities if "apply_labels" in activity.get("tool", "")),
                "emails_archived": "N/A"  # Would track archival actions
            }
        }