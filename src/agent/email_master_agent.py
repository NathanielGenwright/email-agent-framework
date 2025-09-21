"""
Email Master Agent - demonstrates agent orchestration and coordination.

This is the main agent that coordinates all sub-agents and manages the overall
email management workflow. It shows how to build complex multi-agent systems.
"""

import logging
from typing import Dict, List, Any, Optional
from datetime import datetime
from concurrent.futures import ThreadPoolExecutor, as_completed

from .base import BaseAgent, Tool, ToolResult
from .email_classifier import EmailClassifier
from .email_responder import EmailResponder  
from .inbox_organizer import InboxOrganizer
from ..tools.email_tools import EmailMessage, email_tools
from ..memory.persistent_memory import memory

logger = logging.getLogger(__name__)


class EmailMasterAgent(BaseAgent):
    """
    Master agent that orchestrates email management workflow.
    
    This demonstrates:
    1. Multi-agent coordination
    2. Workflow orchestration
    3. Decision making and prioritization
    4. Learning and adaptation
    5. Performance monitoring
    """
    
    def __init__(self):
        super().__init__(
            name="EmailMasterAgent",
            description="Orchestrates comprehensive email management using specialized sub-agents"
        )
        
        # Initialize sub-agents
        self.classifier = EmailClassifier()
        self.responder = EmailResponder()
        self.organizer = InboxOrganizer()
        
        # Workflow configurations
        self.workflow_settings = {
            "auto_classify": True,
            "auto_organize": True,
            "auto_generate_responses": True,
            "auto_send_responses": False,  # Requires user approval
            "parallel_processing": True,
            "batch_size": 20
        }
        
        # Performance tracking
        self.performance_metrics = {
            "emails_processed": 0,
            "classifications_made": 0,
            "responses_generated": 0,
            "organization_actions": 0,
            "user_feedback_received": 0
        }
        
        # Register coordination tools
        self._register_coordination_tools()
    
    def _register_coordination_tools(self):
        """Register tools for agent coordination and workflow management."""
        
        def run_email_analysis_pipeline(emails: List[EmailMessage]) -> Dict[str, Any]:
            """Run comprehensive analysis pipeline on emails."""
            results = {
                "total_emails": len(emails),
                "classification_results": [],
                "organization_suggestions": [],
                "response_candidates": []
            }
            
            if self.workflow_settings["parallel_processing"]:
                # Run agents in parallel for better performance
                with ThreadPoolExecutor(max_workers=3) as executor:
                    # Submit classification tasks
                    classification_future = executor.submit(
                        self._run_classification_batch, emails
                    )
                    
                    # Submit organization analysis
                    organization_future = executor.submit(
                        self._run_organization_analysis, emails
                    )
                    
                    # Submit response generation for emails needing responses
                    response_future = executor.submit(
                        self._run_response_generation, emails
                    )
                    
                    # Collect results
                    for future in as_completed([classification_future, organization_future, response_future]):
                        try:
                            result = future.result()
                            if "classifications" in result:
                                results["classification_results"] = result["classifications"]
                            elif "organization" in result:
                                results["organization_suggestions"] = result["organization"]
                            elif "responses" in result:
                                results["response_candidates"] = result["responses"]
                        except Exception as e:
                            logger.error(f"Sub-agent processing failed: {e}")
            else:
                # Sequential processing
                results["classification_results"] = self._run_classification_batch(emails)
                results["organization_suggestions"] = self._run_organization_analysis(emails)
                results["response_candidates"] = self._run_response_generation(emails)
            
            return results
        
        def coordinate_workflow_execution(analysis_results: Dict[str, Any]) -> Dict[str, Any]:
            """Coordinate execution of actions based on analysis results."""
            execution_plan = {
                "immediate_actions": [],
                "user_approval_needed": [],
                "scheduled_actions": [],
                "completed_actions": []
            }
            
            # Process classification results
            if self.workflow_settings["auto_classify"]:
                for classification in analysis_results.get("classification_results", []):
                    if classification.get("confidence", 0) > 0.7:
                        execution_plan["immediate_actions"].append({
                            "type": "apply_classification",
                            "email_id": classification["email_id"],
                            "category": classification["category"],
                            "confidence": classification["confidence"]
                        })
                    else:
                        execution_plan["user_approval_needed"].append({
                            "type": "review_classification",
                            "email_id": classification["email_id"],
                            "suggested_category": classification["category"],
                            "confidence": classification["confidence"]
                        })
            
            # Process organization suggestions
            if self.workflow_settings["auto_organize"]:
                for suggestion in analysis_results.get("organization_suggestions", []):
                    execution_plan["immediate_actions"].append({
                        "type": "apply_organization",
                        "action": suggestion["action"],
                        "target": suggestion["target"],
                        "confidence": suggestion.get("confidence", 0.5)
                    })
            
            # Process response candidates
            for response in analysis_results.get("response_candidates", []):
                if self.workflow_settings["auto_send_responses"] and response.get("confidence", 0) > 0.8:
                    execution_plan["immediate_actions"].append({
                        "type": "send_response",
                        "email_id": response["email_id"],
                        "response_text": response["response_text"]
                    })
                else:
                    execution_plan["user_approval_needed"].append({
                        "type": "review_response",
                        "email_id": response["email_id"],
                        "response_text": response["response_text"],
                        "confidence": response.get("confidence", 0)
                    })
            
            return execution_plan
        
        def execute_workflow_actions(execution_plan: Dict[str, Any]) -> Dict[str, Any]:
            """Execute the planned workflow actions."""
            execution_results = {
                "successful_actions": 0,
                "failed_actions": 0,
                "action_details": []
            }
            
            for action in execution_plan.get("immediate_actions", []):
                try:
                    result = self._execute_single_action(action)
                    if result:
                        execution_results["successful_actions"] += 1
                        execution_results["action_details"].append({
                            "action": action,
                            "result": "success",
                            "timestamp": datetime.now().isoformat()
                        })
                    else:
                        execution_results["failed_actions"] += 1
                        execution_results["action_details"].append({
                            "action": action,
                            "result": "failed",
                            "timestamp": datetime.now().isoformat()
                        })
                except Exception as e:
                    execution_results["failed_actions"] += 1
                    execution_results["action_details"].append({
                        "action": action,
                        "result": f"error: {str(e)}",
                        "timestamp": datetime.now().isoformat()
                    })
            
            return execution_results
        
        def monitor_agent_performance() -> Dict[str, Any]:
            """Monitor performance of all sub-agents."""
            performance_report = {
                "master_agent": self.get_status(),
                "sub_agents": {
                    "classifier": self.classifier.get_status(),
                    "responder": self.responder.get_status(),
                    "organizer": self.organizer.get_status()
                },
                "workflow_metrics": self.performance_metrics.copy(),
                "memory_usage": memory.get_learning_summary()
            }
            
            # Add specific performance indicators
            performance_report["health_indicators"] = {
                "classifier_accuracy": self._estimate_classifier_accuracy(),
                "response_approval_rate": self._calculate_response_approval_rate(),
                "organization_effectiveness": self._assess_organization_effectiveness()
            }
            
            return performance_report
        
        # Register coordination tools
        self.register_tool(Tool(
            name="run_analysis_pipeline",
            description="Run comprehensive email analysis using all sub-agents",
            function=run_email_analysis_pipeline
        ))
        
        self.register_tool(Tool(
            name="coordinate_workflow",
            description="Coordinate workflow execution based on analysis",
            function=coordinate_workflow_execution
        ))
        
        self.register_tool(Tool(
            name="execute_actions",
            description="Execute planned workflow actions",
            function=execute_workflow_actions
        ))
        
        self.register_tool(Tool(
            name="monitor_performance",
            description="Monitor performance of all agents",
            function=monitor_agent_performance
        ))
    
    def _run_classification_batch(self, emails: List[EmailMessage]) -> List[Dict[str, Any]]:
        """Run classification on a batch of emails."""
        # Prepare emails for classifier
        perception = {"emails_to_classify": [email.to_dict() for email in emails]}
        
        # Run classifier
        actions = self.classifier.think(perception)
        results = self.classifier.act(actions)
        
        # Extract classification results
        classifications = []
        for result in results:
            if result.success:
                data = result.result
                classifications.append({
                    "email_id": data["email_id"],
                    "category": data.get("classify_category", "unknown"),
                    "priority": data.get("calculate_priority", 5),
                    "sentiment": data.get("analyze_sentiment", "neutral"),
                    "confidence": 0.8  # Would calculate based on multiple factors
                })
        
        self.performance_metrics["classifications_made"] += len(classifications)
        return {"classifications": classifications}
    
    def _run_organization_analysis(self, emails: List[EmailMessage]) -> List[Dict[str, Any]]:
        """Run organization analysis on emails."""
        # Prepare emails for organizer
        perception = {
            "emails_for_organization": [email.to_dict() for email in emails],
            "total_emails": len(emails)
        }
        
        # Run organizer
        actions = self.organizer.think(perception)
        results = self.organizer.act(actions)
        
        # Extract organization suggestions
        suggestions = []
        for result in results:
            if result.success:
                data = result.result
                if "apply_labels" in data:
                    for label, email_ids in data["apply_labels"].items():
                        for email_id in email_ids:
                            suggestions.append({
                                "action": "apply_label",
                                "target": email_id,
                                "value": label,
                                "confidence": 0.7
                            })
        
        self.performance_metrics["organization_actions"] += len(suggestions)
        return {"organization": suggestions}
    
    def _run_response_generation(self, emails: List[EmailMessage]) -> List[Dict[str, Any]]:
        """Run response generation for emails that need responses."""
        # Filter emails that likely need responses
        response_candidates = []
        for email in emails:
            text = f"{email.subject} {email.body}".lower()
            if any(word in text for word in ["?", "please", "can you", "need", "request"]):
                response_candidates.append(email)
        
        if not response_candidates:
            return {"responses": []}
        
        # Prepare for responder
        perception = {
            "emails_needing_response": [email.to_dict() for email in response_candidates]
        }
        
        # Run responder
        actions = self.responder.think(perception)
        results = self.responder.act(actions)
        
        # Extract response candidates
        responses = []
        for result in results:
            if result.success:
                data = result.result
                responses.append({
                    "email_id": data["email_id"],
                    "response_text": data.get("suggested_response", ""),
                    "intent": data.get("intent_analysis", {}).get("primary_intent", ""),
                    "confidence": 0.6  # Would calculate based on response quality
                })
        
        self.performance_metrics["responses_generated"] += len(responses)
        return {"responses": responses}
    
    def _execute_single_action(self, action: Dict[str, Any]) -> bool:
        """Execute a single workflow action."""
        action_type = action.get("type")
        
        if action_type == "apply_classification":
            # Apply classification to email
            email_id = action["email_id"]
            category = action["category"]
            return email_tools.add_label(email_id, f"category:{category}")
        
        elif action_type == "apply_organization":
            # Apply organization action
            org_action = action["action"]
            target = action["target"]
            
            if org_action == "apply_label":
                return email_tools.add_label(target, action["value"])
            elif org_action == "archive":
                return email_tools.archive_email(target)
            
        elif action_type == "send_response":
            # Send response (this would require more careful implementation)
            email_id = action["email_id"]
            response_text = action["response_text"]
            # For now, just log the action
            logger.info(f"Would send response to email {email_id}")
            return True
        
        return False
    
    def _estimate_classifier_accuracy(self) -> float:
        """Estimate classifier accuracy based on user feedback."""
        # This would analyze feedback patterns in memory
        feedback_events = memory.search_events(
            event_type="user_feedback",
            limit=100
        )
        
        if not feedback_events:
            return 0.85  # Default estimate
        
        # Calculate accuracy from correction feedback
        corrections = 0
        total_feedback = 0
        
        for event in feedback_events:
            if "classification_correction" in event.data:
                total_feedback += 1
                if event.data.get("was_correct", False):
                    corrections += 1
        
        if total_feedback == 0:
            return 0.85
        
        return 1.0 - (corrections / total_feedback)
    
    def _calculate_response_approval_rate(self) -> float:
        """Calculate rate of response approvals."""
        # This would analyze response approval patterns
        approval_events = memory.search_events(
            event_type="response_approval",
            limit=100
        )
        
        if not approval_events:
            return 0.0
        
        approved = sum(1 for event in approval_events 
                      if event.data.get("approved", False))
        
        return approved / len(approval_events)
    
    def _assess_organization_effectiveness(self) -> float:
        """Assess effectiveness of organization actions."""
        # This would measure how often organization actions are undone
        return 0.80  # Placeholder
    
    def perceive(self) -> Dict[str, Any]:
        """
        Master agent perception: Get overall email environment state.
        """
        # Get fresh emails for processing
        recent_emails = email_tools.fetch_recent_emails(
            limit=self.workflow_settings["batch_size"]
        )
        
        # Get status from all sub-agents
        agent_statuses = {
            "classifier": self.classifier.get_status(),
            "responder": self.responder.get_status(),
            "organizer": self.organizer.get_status()
        }
        
        # Get user preferences for workflow adaptation
        workflow_prefs = {
            "auto_classify": memory.get_preference("workflow", "auto_classify", True)[0],
            "auto_organize": memory.get_preference("workflow", "auto_organize", True)[0],
            "auto_respond": memory.get_preference("workflow", "auto_respond", False)[0]
        }
        
        return {
            "new_emails": [email.to_dict() for email in recent_emails],
            "total_new_emails": len(recent_emails),
            "sub_agent_status": agent_statuses,
            "workflow_preferences": workflow_prefs,
            "system_health": self._assess_system_health(),
            "timestamp": datetime.now().isoformat()
        }
    
    def think(self, perception: Dict[str, Any]) -> List[Dict[str, Any]]:
        """
        Master agent reasoning: Plan comprehensive email management workflow.
        """
        new_emails = perception.get("new_emails", [])
        total_emails = perception.get("total_new_emails", 0)
        
        if total_emails == 0:
            return []
        
        # Reconstruct EmailMessage objects
        emails = []
        for email_data in new_emails:
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
        
        # Plan comprehensive workflow
        actions = []
        
        # Main processing workflow
        actions.append({
            "type": "comprehensive_email_processing",
            "emails": emails,
            "steps": [
                "run_analysis_pipeline",
                "coordinate_workflow", 
                "execute_actions",
                "monitor_performance"
            ]
        })
        
        logger.info(f"Planned comprehensive processing for {total_emails} emails")
        return actions
    
    def act(self, actions: List[Dict[str, Any]]) -> List[ToolResult]:
        """
        Master agent action: Execute comprehensive email management workflow.
        """
        results = []
        
        for action in actions:
            if action["type"] == "comprehensive_email_processing":
                emails = action["emails"]
                
                workflow_result = {
                    "workflow_type": "comprehensive_email_processing",
                    "emails_processed": len(emails),
                    "start_time": datetime.now().isoformat()
                }
                
                # Execute workflow steps
                pipeline_results = None
                execution_plan = None
                
                for step in action["steps"]:
                    if step == "run_analysis_pipeline":
                        tool_result = self.use_tool(step, emails=emails)
                        if tool_result.success:
                            pipeline_results = tool_result.result
                            workflow_result["analysis_results"] = pipeline_results
                    
                    elif step == "coordinate_workflow" and pipeline_results:
                        tool_result = self.use_tool(step, analysis_results=pipeline_results)
                        if tool_result.success:
                            execution_plan = tool_result.result
                            workflow_result["execution_plan"] = execution_plan
                    
                    elif step == "execute_actions" and execution_plan:
                        tool_result = self.use_tool(step, execution_plan=execution_plan)
                        if tool_result.success:
                            workflow_result["execution_results"] = tool_result.result
                    
                    elif step == "monitor_performance":
                        tool_result = self.use_tool(step)
                        if tool_result.success:
                            workflow_result["performance_report"] = tool_result.result
                
                workflow_result["end_time"] = datetime.now().isoformat()
                
                # Record workflow execution in memory
                memory.add_event(
                    event_type="workflow_execution",
                    data=workflow_result,
                    importance=0.8,
                    tags=["workflow", "email_processing"]
                )
                
                # Update performance metrics
                self.performance_metrics["emails_processed"] += len(emails)
                
                results.append(ToolResult(
                    success=True,
                    result=workflow_result,
                    metadata={"agent": self.name, "workflow": "comprehensive"}
                ))
        
        logger.info(f"Completed {len(results)} workflow executions")
        return results
    
    def _assess_system_health(self) -> Dict[str, str]:
        """Assess overall system health."""
        return {
            "email_connection": "healthy" if email_tools.connection else "disconnected",
            "memory_system": "healthy",
            "sub_agents": "operational",
            "overall_status": "healthy"
        }
    
    def process_user_feedback(self, email_id: str, feedback_type: str, 
                            feedback_data: Dict[str, Any]) -> bool:
        """Process user feedback for learning and improvement."""
        try:
            memory.add_user_feedback(email_id, feedback_type, feedback_data)
            self.performance_metrics["user_feedback_received"] += 1
            
            logger.info(f"Processed user feedback: {feedback_type} for email {email_id}")
            return True
        except Exception as e:
            logger.error(f"Failed to process user feedback: {e}")
            return False
    
    def get_comprehensive_status(self) -> Dict[str, Any]:
        """Get comprehensive status of the entire email agent system."""
        return {
            "master_agent": self.get_status(),
            "sub_agents": {
                "classifier": self.classifier.get_status(),
                "responder": self.responder.get_status(), 
                "organizer": self.organizer.get_status()
            },
            "performance_metrics": self.performance_metrics,
            "workflow_settings": self.workflow_settings,
            "memory_summary": memory.get_learning_summary(),
            "system_health": self._assess_system_health()
        }