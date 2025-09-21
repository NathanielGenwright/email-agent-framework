"""
Email Agent Concepts Demonstration

This script demonstrates key agent concepts through simplified examples
that help understand the difference between bots and agents.
"""

import sys
from pathlib import Path

# Add src to path
sys.path.append(str(Path(__file__).parent.parent / "src"))

from typing import Dict, List, Any
from datetime import datetime
import json


class SimpleBot:
    """
    Example of a traditional bot - reactive and rule-based.
    
    Bots typically:
    - Respond to specific triggers
    - Follow predetermined scripts  
    - Have limited adaptability
    - Work with static rules
    """
    
    def __init__(self):
        self.responses = {
            "hello": "Hi there! How can I help you?",
            "status": "All systems operational",
            "help": "Available commands: hello, status, help, quit"
        }
    
    def process_command(self, command: str) -> str:
        """Simple command processing - bot behavior."""
        command = command.lower().strip()
        
        # Direct mapping - no reasoning or adaptation
        if command in self.responses:
            return self.responses[command]
        elif "time" in command:
            return f"Current time is {datetime.now().strftime('%H:%M:%S')}"
        else:
            return "I don't understand that command. Type 'help' for available commands."


class SimpleEmailAgent:
    """
    Example of an agent - autonomous and reasoning-based.
    
    Agents typically:
    - Perceive environment state
    - Reason about goals and plans
    - Take actions autonomously
    - Learn and adapt over time
    """
    
    def __init__(self):
        self.memory = []
        self.preferences = {}
        self.tools = {
            "classify_email": self._classify_email,
            "generate_response": self._generate_response,
            "update_preferences": self._update_preferences
        }
    
    def _classify_email(self, email_data: Dict) -> str:
        """Tool: Classify email type."""
        subject = email_data.get("subject", "").lower()
        body = email_data.get("body", "").lower()
        
        if any(word in subject + body for word in ["urgent", "asap", "emergency"]):
            return "urgent"
        elif any(word in subject + body for word in ["meeting", "calendar", "schedule"]):
            return "meeting"
        elif any(word in subject + body for word in ["invoice", "payment", "bill"]):
            return "financial"
        else:
            return "general"
    
    def _generate_response(self, email_data: Dict, classification: str) -> str:
        """Tool: Generate contextual response."""
        sender = email_data.get("sender", "")
        
        # Check learned preferences
        sender_pref = self.preferences.get(f"response_style_{sender}", "professional")
        
        if classification == "urgent":
            return f"Thank you for your urgent message. I will prioritize this and respond within the hour. [{sender_pref} tone]"
        elif classification == "meeting":
            return f"Thank you for the meeting invitation. Let me check my calendar and get back to you. [{sender_pref} tone]"
        elif classification == "financial":
            return f"I've received your financial communication and will review it promptly. [{sender_pref} tone]"
        else:
            return f"Thank you for your email. I'll respond appropriately soon. [{sender_pref} tone]"
    
    def _update_preferences(self, sender: str, style: str) -> None:
        """Tool: Update learned preferences."""
        self.preferences[f"response_style_{sender}"] = style
        print(f"Learned: {sender} prefers {style} communication style")
    
    def perceive(self, environment: Dict[str, Any]) -> Dict[str, Any]:
        """Perception: Gather and analyze environmental information."""
        emails = environment.get("emails", [])
        user_feedback = environment.get("feedback", [])
        
        perception = {
            "new_emails_count": len(emails),
            "emails_to_process": emails,
            "feedback_received": user_feedback,
            "timestamp": datetime.now().isoformat()
        }
        
        print(f"🔍 PERCEPTION: Found {len(emails)} emails to process")
        return perception
    
    def think(self, perception: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Reasoning: Plan actions based on perception."""
        emails = perception.get("emails_to_process", [])
        feedback = perception.get("feedback_received", [])
        
        actions = []
        
        # Process feedback first (learning)
        for fb in feedback:
            actions.append({
                "type": "learn_from_feedback",
                "data": fb
            })
        
        # Plan email processing
        for email in emails:
            actions.append({
                "type": "process_email",
                "email": email,
                "steps": ["classify_email", "generate_response"]
            })
        
        print(f"🧠 THINKING: Planned {len(actions)} actions")
        return actions
    
    def act(self, actions: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Action: Execute planned actions using available tools."""
        results = []
        
        for action in actions:
            if action["type"] == "learn_from_feedback":
                # Process user feedback
                fb_data = action["data"]
                if fb_data.get("type") == "response_style":
                    self._update_preferences(fb_data["sender"], fb_data["preferred_style"])
                
                results.append({"action": "learning", "success": True})
            
            elif action["type"] == "process_email":
                # Process individual email
                email = action["email"]
                email_results = {"email_id": email.get("id"), "actions": {}}
                
                # Execute processing steps
                classification = None
                for step in action["steps"]:
                    if step == "classify_email":
                        classification = self.tools[step](email)
                        email_results["actions"]["classification"] = classification
                        print(f"  📧 Classified email as: {classification}")
                    
                    elif step == "generate_response" and classification:
                        response = self.tools[step](email, classification)
                        email_results["actions"]["response"] = response
                        print(f"  ✍️  Generated response: {response[:50]}...")
                
                results.append(email_results)
        
        print(f"⚡ ACTING: Completed {len(results)} actions")
        return results
    
    def run_cycle(self, environment: Dict[str, Any]) -> Dict[str, Any]:
        """Execute one complete perceive-think-act cycle."""
        print("\n🤖 AGENT CYCLE STARTING")
        print("=" * 50)
        
        # 1. Perceive
        perception = self.perceive(environment)
        
        # 2. Think  
        planned_actions = self.think(perception)
        
        # 3. Act
        results = self.act(planned_actions)
        
        # Store in memory
        cycle_result = {
            "timestamp": datetime.now().isoformat(),
            "perception": perception,
            "planned_actions": planned_actions,
            "results": results
        }
        
        self.memory.append(cycle_result)
        
        print("=" * 50)
        print("🤖 AGENT CYCLE COMPLETED\n")
        
        return cycle_result


def demonstrate_bot_vs_agent():
    """Demonstrate the key differences between bots and agents."""
    
    print("🚀 EMAIL AGENT CONCEPTS DEMONSTRATION")
    print("=" * 60)
    
    # Bot demonstration
    print("\n1️⃣  TRADITIONAL BOT BEHAVIOR")
    print("-" * 30)
    
    bot = SimpleBot()
    
    commands = ["hello", "status", "what time is it", "process emails", "help"]
    
    for cmd in commands:
        response = bot.process_command(cmd)
        print(f"User: {cmd}")
        print(f"Bot:  {response}\n")
    
    print("📝 Bot Characteristics:")
    print("   • Reactive to specific commands")
    print("   • Follows predetermined responses")
    print("   • No learning or adaptation")
    print("   • Limited contextual understanding")
    
    # Agent demonstration
    print("\n\n2️⃣  INTELLIGENT AGENT BEHAVIOR")
    print("-" * 30)
    
    agent = SimpleEmailAgent()
    
    # Simulate email environment
    environment = {
        "emails": [
            {
                "id": "1",
                "sender": "boss@company.com",
                "subject": "URGENT: Project deadline moved up",
                "body": "We need to deliver the project by tomorrow. Please confirm ASAP."
            },
            {
                "id": "2", 
                "sender": "colleague@company.com",
                "subject": "Team meeting next week",
                "body": "Can we schedule our weekly team meeting for Tuesday at 2 PM?"
            },
            {
                "id": "3",
                "sender": "finance@company.com", 
                "subject": "Invoice #12345",
                "body": "Please find attached invoice for payment processing."
            }
        ],
        "feedback": []
    }
    
    # Run agent cycle
    result = agent.run_cycle(environment)
    
    print("📝 Agent Characteristics:")
    print("   • Autonomous reasoning and planning")
    print("   • Context-aware decision making")
    print("   • Goal-oriented behavior")
    print("   • Learning from interactions")
    
    # Demonstrate learning
    print("\n\n3️⃣  AGENT LEARNING DEMONSTRATION")
    print("-" * 30)
    
    # Simulate user feedback
    learning_environment = {
        "emails": [
            {
                "id": "4",
                "sender": "boss@company.com", 
                "subject": "Follow up",
                "body": "Just checking on the status."
            }
        ],
        "feedback": [
            {
                "type": "response_style",
                "sender": "boss@company.com",
                "preferred_style": "concise"
            }
        ]
    }
    
    print("👤 User provides feedback: Boss prefers concise communication")
    result2 = agent.run_cycle(learning_environment)
    
    print("\n📊 COMPARISON SUMMARY")
    print("=" * 60)
    
    comparison_table = [
        ["Aspect", "Bot", "Agent"],
        ["-" * 15, "-" * 20, "-" * 25],
        ["Behavior", "Reactive", "Proactive & Autonomous"],
        ["Intelligence", "Rule-based", "Reasoning & Planning"],
        ["Adaptability", "Static", "Learning & Improving"],
        ["Context", "Limited", "Contextually Aware"],
        ["Goals", "Command Response", "Objective Achievement"],
        ["Memory", "None", "Persistent & Learning"],
        ["Tools", "Fixed Functions", "Dynamic Tool Usage"]
    ]
    
    for row in comparison_table:
        print(f"{row[0]:<15} | {row[1]:<20} | {row[2]:<25}")
    
    print("\n💡 KEY INSIGHTS FOR AGENT BUILDING:")
    print("   1. Agents perceive their environment actively")
    print("   2. Agents reason about goals and plan actions")
    print("   3. Agents use tools to achieve objectives")
    print("   4. Agents learn from feedback and experience")
    print("   5. Agents maintain context and memory")
    print("   6. Agents can coordinate with other agents")
    
    print(f"\n🎓 To build effective agents:")
    print("   • Define clear perception mechanisms")
    print("   • Implement reasoning and planning logic")
    print("   • Create specialized tools for domain tasks")
    print("   • Add learning and memory capabilities")
    print("   • Monitor performance and optimize")


def demonstrate_multi_agent_concepts():
    """Demonstrate multi-agent coordination concepts."""
    
    print("\n\n4️⃣  MULTI-AGENT COORDINATION")
    print("-" * 30)
    
    print("In a multi-agent system like our email agent:")
    print()
    print("🏗️  ARCHITECTURE:")
    print("   Master Agent (Orchestrator)")
    print("   ├── Classification Agent (Specialist)")
    print("   ├── Response Agent (Specialist)")
    print("   └── Organization Agent (Specialist)")
    print()
    print("🔄 COORDINATION PATTERNS:")
    print("   • Sequential: One agent feeds into another")
    print("   • Parallel: Multiple agents work simultaneously")
    print("   • Hierarchical: Master coordinates sub-agents")
    print("   • Collaborative: Agents share information")
    print()
    print("💼 BUSINESS APPLICATIONS:")
    print("   • Customer Service: Route, analyze, respond")
    print("   • Document Processing: Extract, classify, archive")
    print("   • Workflow Automation: Monitor, decide, execute")
    print("   • Data Analysis: Collect, process, report")


if __name__ == "__main__":
    demonstrate_bot_vs_agent()
    demonstrate_multi_agent_concepts()
    
    print(f"\n\n🎯 NEXT STEPS:")
    print("   1. Explore the full email agent implementation")
    print("   2. Run: python src/main.py")
    print("   3. Try: python -m src.cli interactive") 
    print("   4. Study: src/agent/ directory for detailed examples")
    print("   5. Build: Your own specialized agents!")