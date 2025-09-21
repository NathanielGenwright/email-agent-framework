"""
Email Classification Agent - demonstrates how sub-agents work.

This agent specializes in analyzing and categorizing emails.
It shows the concept of domain-specific agents with focused capabilities.
"""

import logging
import re
from typing import Dict, List, Any
from datetime import datetime

from .base import BaseAgent, Tool, ToolResult
from ..tools.email_tools import EmailMessage, email_tools

logger = logging.getLogger(__name__)


class EmailClassifier(BaseAgent):
    """
    Sub-agent that specializes in email classification.
    
    This demonstrates:
    1. Specialized domain knowledge (email patterns)
    2. Rule-based reasoning with ML potential
    3. Sub-agent autonomy within defined scope
    """
    
    def __init__(self):
        super().__init__(
            name="EmailClassifier",
            description="Analyzes and categorizes emails automatically"
        )
        
        # Register specialized tools
        self._register_classification_tools()
        
        # Classification rules and patterns
        self.category_patterns = {
            "urgent": [
                r"\b(urgent|asap|immediate|emergency|critical)\b",
                r"\b(deadline|due date|expires?)\b",
                r"!!+",
                r"\b(action required|please respond)\b"
            ],
            "meeting": [
                r"\b(meeting|call|conference|zoom|teams)\b",
                r"\b(calendar|schedule|appointment)\b",
                r"\b(agenda|minutes)\b"
            ],
            "newsletter": [
                r"\b(newsletter|unsubscribe|digest)\b",
                r"\b(weekly|monthly|update)\b",
                r"no-reply|noreply"
            ],
            "promotional": [
                r"\b(sale|discount|offer|promotion|deal)\b",
                r"\b(buy now|limited time|expires)\b",
                r"\b(marketing|advertisement)\b"
            ],
            "personal": [
                r"\b(family|friend|personal)\b",
                r"\b(happy birthday|congratulations)\b"
            ],
            "work": [
                r"\b(project|task|deadline|report)\b",
                r"\b(colleague|team|department)\b",
                r"\b(proposal|contract|invoice)\b"
            ],
            "spam": [
                r"\b(viagra|casino|lottery|prince)\b",
                r"\b(click here|act now)\b",
                r"suspicious patterns"
            ]
        }
        
        # Priority scoring weights
        self.priority_weights = {
            "sender_importance": 0.3,
            "subject_urgency": 0.25,
            "content_urgency": 0.25,
            "recency": 0.2
        }
    
    def _register_classification_tools(self):
        """Register tools specific to email classification."""
        
        def classify_email_category(email: EmailMessage) -> str:
            """Classify email into primary category."""
            text = f"{email.subject} {email.body}".lower()
            
            scores = {}
            for category, patterns in self.category_patterns.items():
                score = 0
                for pattern in patterns:
                    matches = len(re.findall(pattern, text, re.IGNORECASE))
                    score += matches
                scores[category] = score
            
            # Return category with highest score, or 'general' if no matches
            if not scores or max(scores.values()) == 0:
                return "general"
            
            return max(scores, key=scores.get)
        
        def calculate_priority_score(email: EmailMessage) -> float:
            """Calculate priority score from 0-10."""
            score = 5.0  # Base score
            
            # Sender importance (would be learned from user behavior)
            known_important_senders = ["boss@company.com", "client@important.com"]
            if any(sender in email.sender.lower() for sender in known_important_senders):
                score += 2.0
            
            # Subject urgency indicators
            urgent_words = ["urgent", "asap", "immediate", "emergency"]
            for word in urgent_words:
                if word.lower() in email.subject.lower():
                    score += 1.5
                    break
            
            # Content urgency
            urgent_content = ["deadline", "action required", "please respond"]
            for phrase in urgent_content:
                if phrase.lower() in email.body.lower():
                    score += 1.0
                    break
            
            # Recency bonus
            hours_old = (datetime.now() - email.date).total_seconds() / 3600
            if hours_old < 1:
                score += 1.0
            elif hours_old < 6:
                score += 0.5
            
            return min(max(score, 0), 10)  # Clamp to 0-10
        
        def detect_action_items(email: EmailMessage) -> List[str]:
            """Extract action items from email content."""
            actions = []
            text = email.body.lower()
            
            # Pattern matching for common action indicators
            action_patterns = [
                r"please (.*?)(?:\.|$)",
                r"can you (.*?)(?:\.|$)",
                r"need to (.*?)(?:\.|$)",
                r"action required:? (.*?)(?:\.|$)",
                r"todo:? (.*?)(?:\.|$)"
            ]
            
            for pattern in action_patterns:
                matches = re.findall(pattern, text)
                actions.extend([match.strip() for match in matches if len(match.strip()) > 10])
            
            return actions[:5]  # Limit to 5 actions
        
        def analyze_sentiment(email: EmailMessage) -> str:
            """Basic sentiment analysis of email."""
            text = f"{email.subject} {email.body}".lower()
            
            positive_words = ["thank", "great", "excellent", "appreciate", "wonderful"]
            negative_words = ["problem", "issue", "urgent", "error", "failed", "angry"]
            
            positive_count = sum(1 for word in positive_words if word in text)
            negative_count = sum(1 for word in negative_words if word in text)
            
            if positive_count > negative_count:
                return "positive"
            elif negative_count > positive_count:
                return "negative"
            else:
                return "neutral"
        
        # Register tools
        self.register_tool(Tool(
            name="classify_category",
            description="Classify email into a primary category",
            function=classify_email_category
        ))
        
        self.register_tool(Tool(
            name="calculate_priority",
            description="Calculate priority score for email",
            function=calculate_priority_score
        ))
        
        self.register_tool(Tool(
            name="detect_actions",
            description="Extract action items from email",
            function=detect_action_items
        ))
        
        self.register_tool(Tool(
            name="analyze_sentiment",
            description="Analyze email sentiment",
            function=analyze_sentiment
        ))
    
    def perceive(self) -> Dict[str, Any]:
        """
        Perception: Get emails that need classification.
        In a real system, this might be triggered by new email events.
        """
        # For demo, we'll fetch recent unclassified emails
        emails = email_tools.fetch_recent_emails(limit=10)
        
        return {
            "emails_to_classify": [email.to_dict() for email in emails],
            "total_count": len(emails),
            "timestamp": datetime.now().isoformat()
        }
    
    def think(self, perception: Dict[str, Any]) -> List[Dict[str, Any]]:
        """
        Reasoning: Plan classification actions for each email.
        This shows how agents break down complex tasks.
        """
        emails = perception.get("emails_to_classify", [])
        actions = []
        
        for email_data in emails:
            # Reconstruct EmailMessage from dict
            email_msg = EmailMessage(
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
            )
            
            # Plan comprehensive analysis for this email
            actions.append({
                "type": "analyze_email",
                "email_id": email_msg.id,
                "email": email_msg,
                "analysis_steps": [
                    "classify_category",
                    "calculate_priority", 
                    "detect_actions",
                    "analyze_sentiment"
                ]
            })
        
        logger.info(f"Planned analysis for {len(actions)} emails")
        return actions
    
    def act(self, actions: List[Dict[str, Any]]) -> List[ToolResult]:
        """
        Action: Execute classification analysis on emails.
        This demonstrates tool orchestration within an agent.
        """
        results = []
        
        for action in actions:
            if action["type"] == "analyze_email":
                email = action["email"]
                email_id = action["email_id"]
                
                # Perform comprehensive analysis
                analysis_result = {
                    "email_id": email_id,
                    "subject": email.subject,
                    "sender": email.sender
                }
                
                # Execute each analysis step
                for step in action["analysis_steps"]:
                    tool_result = self.use_tool(step, email=email)
                    if tool_result.success:
                        analysis_result[step] = tool_result.result
                    else:
                        analysis_result[step] = f"Error: {tool_result.error}"
                
                # Store complete analysis in memory
                self.memory.store_long_term(f"email_analysis_{email_id}", analysis_result)
                
                results.append(ToolResult(
                    success=True,
                    result=analysis_result,
                    metadata={"email_id": email_id, "agent": self.name}
                ))
        
        logger.info(f"Completed analysis of {len(results)} emails")
        return results
    
    def get_classification_summary(self) -> Dict[str, Any]:
        """Get summary of recent classifications."""
        # Analyze patterns in recent classifications
        recent_analyses = [
            event for event in self.memory.short_term[-50:]
            if event.get("type") == "tool_usage" and event.get("tool") == "classify_category"
        ]
        
        categories = {}
        for analysis in recent_analyses:
            result = analysis.get("result", "unknown")
            categories[result] = categories.get(result, 0) + 1
        
        return {
            "total_classified": len(recent_analyses),
            "category_distribution": categories,
            "agent_status": self.get_status()
        }