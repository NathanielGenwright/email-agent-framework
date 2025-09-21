"""
Email Response Generation Agent - demonstrates AI-powered agent capabilities.

This agent specializes in generating appropriate email responses.
It shows how agents can use LLMs for complex reasoning and content generation.
"""

import logging
import json
from typing import Dict, List, Any, Optional
from datetime import datetime

try:
    import openai
    from openai import OpenAI
    OPENAI_AVAILABLE = True
except ImportError:
    OPENAI_AVAILABLE = False

from .base import BaseAgent, Tool, ToolResult
from ..tools.email_tools import EmailMessage, email_tools
from ..config.settings import settings

logger = logging.getLogger(__name__)


class EmailResponder(BaseAgent):
    """
    Sub-agent that specializes in generating email responses.
    
    This demonstrates:
    1. AI-powered content generation
    2. Context-aware reasoning
    3. Template management and personalization
    4. Integration with external LLM services
    """
    
    def __init__(self):
        super().__init__(
            name="EmailResponder", 
            description="Generates appropriate responses to emails using AI"
        )
        
        # Initialize LLM client
        self.llm_client = None
        if OPENAI_AVAILABLE and settings.openai_api_key:
            self.llm_client = OpenAI(api_key=settings.openai_api_key)
        
        # Response templates for common scenarios
        self.response_templates = {
            "meeting_request": {
                "template": "Thank you for the meeting invitation. I'm available on {suggested_times}. Please let me know what works best for you.",
                "context_required": ["suggested_times"]
            },
            "information_request": {
                "template": "Thank you for your inquiry about {topic}. {information}. Please let me know if you need any additional details.",
                "context_required": ["topic", "information"]
            },
            "acknowledgment": {
                "template": "Thank you for your email regarding {subject}. I have received your message and will {action} by {timeline}.",
                "context_required": ["subject", "action", "timeline"]
            },
            "decline_politely": {
                "template": "Thank you for thinking of me for {opportunity}. Unfortunately, I won't be able to {specific_request} due to {reason}. I appreciate your understanding.",
                "context_required": ["opportunity", "specific_request", "reason"]
            },
            "follow_up": {
                "template": "I wanted to follow up on {previous_topic}. {update_or_question}. Please let me know your thoughts.",
                "context_required": ["previous_topic", "update_or_question"]
            }
        }
        
        # Register response generation tools
        self._register_response_tools()
    
    def _register_response_tools(self):
        """Register tools specific to email response generation."""
        
        def analyze_email_intent(email: EmailMessage) -> Dict[str, Any]:
            """Analyze what the email is asking for."""
            text = f"{email.subject} {email.body}".lower()
            
            intents = {
                "meeting_request": ["meeting", "call", "schedule", "appointment", "available"],
                "information_request": ["please send", "can you provide", "need information", "details about"],
                "task_assignment": ["please", "can you", "need you to", "action required"],
                "confirmation": ["confirm", "verify", "check", "is this correct"],
                "complaint": ["problem", "issue", "unhappy", "disappointed", "wrong"],
                "thank_you": ["thank you", "thanks", "appreciate", "grateful"],
                "introduction": ["introduce", "meet", "new to", "joining"]
            }
            
            detected_intents = []
            confidence_scores = {}
            
            for intent, keywords in intents.items():
                score = sum(1 for keyword in keywords if keyword in text)
                if score > 0:
                    detected_intents.append(intent)
                    confidence_scores[intent] = score / len(keywords)
            
            primary_intent = max(confidence_scores, key=confidence_scores.get) if confidence_scores else "general"
            
            return {
                "primary_intent": primary_intent,
                "all_intents": detected_intents,
                "confidence_scores": confidence_scores,
                "requires_response": len(detected_intents) > 0
            }
        
        def generate_ai_response(email: EmailMessage, intent_analysis: Dict) -> str:
            """Generate AI-powered response using LLM."""
            if not self.llm_client:
                return self._generate_template_response(email, intent_analysis)
            
            try:
                system_prompt = """You are an AI assistant helping to draft professional email responses. 
                Generate a helpful, polite, and contextually appropriate response to the given email.
                Keep responses concise but warm. Match the tone of the original email.
                Do not make commitments or promises without user approval."""
                
                user_prompt = f"""
                Original Email:
                From: {email.sender}
                Subject: {email.subject}
                Body: {email.body[:1000]}  # Limit for API
                
                Intent Analysis: {intent_analysis['primary_intent']}
                
                Please draft a professional response.
                """
                
                response = self.llm_client.chat.completions.create(
                    model="gpt-3.5-turbo",
                    messages=[
                        {"role": "system", "content": system_prompt},
                        {"role": "user", "content": user_prompt}
                    ],
                    max_tokens=300,
                    temperature=0.7
                )
                
                return response.choices[0].message.content.strip()
                
            except Exception as e:
                logger.error(f"AI response generation failed: {e}")
                return self._generate_template_response(email, intent_analysis)
        
        def _generate_template_response(self, email: EmailMessage, intent_analysis: Dict) -> str:
            """Fallback template-based response generation."""
            intent = intent_analysis.get("primary_intent", "general")
            
            if intent == "meeting_request":
                return "Thank you for the meeting invitation. I'll check my calendar and get back to you with my availability."
            elif intent == "information_request":
                return "Thank you for your inquiry. I'll gather the requested information and send it to you shortly."
            elif intent == "task_assignment":
                return "Thank you for your email. I've noted the request and will work on this. I'll update you on my progress."
            elif intent == "confirmation":
                return "Thank you for reaching out. I'll review the details and confirm shortly."
            elif intent == "thank_you":
                return "You're very welcome! I'm glad I could help. Please don't hesitate to reach out if you need anything else."
            else:
                return "Thank you for your email. I've received your message and will respond appropriately soon."
        
        def suggest_response_actions(email: EmailMessage, intent_analysis: Dict) -> List[str]:
            """Suggest possible actions based on email content."""
            intent = intent_analysis.get("primary_intent", "general")
            actions = []
            
            if intent == "meeting_request":
                actions.extend([
                    "Check calendar for availability",
                    "Propose alternative times",
                    "Ask for meeting agenda",
                    "Confirm meeting platform (Zoom, Teams, etc.)"
                ])
            elif intent == "information_request":
                actions.extend([
                    "Gather requested information",
                    "Check if information is publicly available",
                    "Ask clarifying questions if needed",
                    "Set follow-up reminder"
                ])
            elif intent == "task_assignment":
                actions.extend([
                    "Clarify task requirements",
                    "Estimate time needed",
                    "Check resource availability",
                    "Set deadline expectations"
                ])
            elif intent == "complaint":
                actions.extend([
                    "Acknowledge the concern",
                    "Investigate the issue",
                    "Offer solution or compensation",
                    "Follow up to ensure resolution"
                ])
            
            return actions
        
        def determine_response_priority(email: EmailMessage, intent_analysis: Dict) -> str:
            """Determine how quickly this email should be responded to."""
            # Check for urgency indicators
            urgent_senders = ["boss@", "client@", "emergency@"]
            urgent_subjects = ["urgent", "asap", "emergency", "immediate"]
            
            if any(sender in email.sender.lower() for sender in urgent_senders):
                return "immediate"
            
            if any(word in email.subject.lower() for word in urgent_subjects):
                return "high"
            
            intent = intent_analysis.get("primary_intent", "general")
            if intent in ["meeting_request", "task_assignment", "complaint"]:
                return "medium"
            elif intent in ["information_request", "confirmation"]:
                return "low"
            else:
                return "normal"
        
        # Register all tools
        self.register_tool(Tool(
            name="analyze_intent",
            description="Analyze what the email is asking for",
            function=analyze_email_intent
        ))
        
        self.register_tool(Tool(
            name="generate_response",
            description="Generate AI-powered email response",
            function=generate_ai_response
        ))
        
        self.register_tool(Tool(
            name="suggest_actions",
            description="Suggest follow-up actions for email",
            function=suggest_response_actions
        ))
        
        self.register_tool(Tool(
            name="determine_priority",
            description="Determine response priority level",
            function=determine_response_priority
        ))
    
    def perceive(self) -> Dict[str, Any]:
        """
        Perception: Identify emails that need responses.
        In practice, this might be triggered by classification results.
        """
        # Get recent emails that haven't been responded to
        emails = email_tools.fetch_recent_emails(limit=5)
        
        # Filter for emails that likely need responses
        response_needed = []
        for email in emails:
            # Simple heuristic: not from ourselves and contains question words
            if settings.email_address.lower() not in email.sender.lower():
                text = f"{email.subject} {email.body}".lower()
                if any(word in text for word in ["?", "please", "can you", "need", "request"]):
                    response_needed.append(email)
        
        return {
            "emails_needing_response": [email.to_dict() for email in response_needed],
            "total_count": len(response_needed),
            "timestamp": datetime.now().isoformat()
        }
    
    def think(self, perception: Dict[str, Any]) -> List[Dict[str, Any]]:
        """
        Reasoning: Plan response strategy for each email.
        This shows intelligent task prioritization.
        """
        emails = perception.get("emails_needing_response", [])
        actions = []
        
        for email_data in emails:
            # Reconstruct EmailMessage
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
            
            # Plan comprehensive response generation
            actions.append({
                "type": "generate_email_response",
                "email_id": email_msg.id,
                "email": email_msg,
                "steps": [
                    "analyze_intent",
                    "determine_priority",
                    "suggest_actions",
                    "generate_response"
                ]
            })
        
        # Sort actions by priority (would implement priority scoring)
        logger.info(f"Planned responses for {len(actions)} emails")
        return actions
    
    def act(self, actions: List[Dict[str, Any]]) -> List[ToolResult]:
        """
        Action: Generate responses for emails.
        This demonstrates coordinated tool usage for complex tasks.
        """
        results = []
        
        for action in actions:
            if action["type"] == "generate_email_response":
                email = action["email"]
                email_id = action["email_id"]
                
                response_package = {
                    "email_id": email_id,
                    "original_subject": email.subject,
                    "original_sender": email.sender,
                    "response_generated_at": datetime.now().isoformat()
                }
                
                # Execute response generation pipeline
                intent_result = None
                for step in action["steps"]:
                    if step == "analyze_intent":
                        tool_result = self.use_tool(step, email=email)
                        if tool_result.success:
                            intent_result = tool_result.result
                            response_package["intent_analysis"] = intent_result
                    
                    elif step == "generate_response" and intent_result:
                        tool_result = self.use_tool(step, email=email, intent_analysis=intent_result)
                        if tool_result.success:
                            response_package["suggested_response"] = tool_result.result
                    
                    else:
                        tool_result = self.use_tool(step, email=email)
                        if tool_result.success:
                            response_package[step] = tool_result.result
                
                # Store response package in memory
                self.memory.store_long_term(f"response_package_{email_id}", response_package)
                
                results.append(ToolResult(
                    success=True,
                    result=response_package,
                    metadata={"email_id": email_id, "agent": self.name}
                ))
        
        logger.info(f"Generated responses for {len(results)} emails")
        return results
    
    def send_response(self, email_id: str, approved: bool = False) -> bool:
        """Send a generated response if approved by user."""
        response_package = self.memory.long_term.get(f"response_package_{email_id}")
        
        if not response_package or not approved:
            return False
        
        # Extract response details
        suggested_response = response_package.get("suggested_response", "")
        original_sender = response_package.get("original_sender", "")
        original_subject = response_package.get("original_subject", "")
        
        # Format reply subject
        reply_subject = f"Re: {original_subject}" if not original_subject.startswith("Re:") else original_subject
        
        # Send the response
        success = email_tools.send_email(
            to=[original_sender],
            subject=reply_subject,
            body=suggested_response,
            reply_to=email_id
        )
        
        if success:
            # Record the sent response
            self.memory.add_to_short_term({
                "type": "response_sent",
                "email_id": email_id,
                "recipient": original_sender,
                "timestamp": datetime.now().isoformat()
            })
        
        return success
    
    def get_pending_responses(self) -> List[Dict[str, Any]]:
        """Get all generated responses pending user approval."""
        pending = []
        
        for key, value in self.memory.long_term.items():
            if key.startswith("response_package_") and isinstance(value, dict):
                email_id = key.replace("response_package_", "")
                pending.append({
                    "email_id": email_id,
                    "original_subject": value.get("original_subject", ""),
                    "original_sender": value.get("original_sender", ""),
                    "suggested_response": value.get("suggested_response", ""),
                    "intent": value.get("intent_analysis", {}).get("primary_intent", ""),
                    "priority": value.get("determine_priority", "normal"),
                    "generated_at": value.get("response_generated_at", "")
                })
        
        return pending