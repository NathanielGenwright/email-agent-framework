#!/usr/bin/env python3
"""
Tutorial: Building Your Own Agent

This example shows how to create a custom agent from scratch,
demonstrating all the key concepts for teaching others.
"""

import sys
from pathlib import Path
from typing import Dict, List, Any
from datetime import datetime
import re

# Add src to path for imports (in real project, you'd install as package)
sys.path.append(str(Path(__file__).parent.parent / "src"))


# Step 1: Define Your Agent's Purpose
class TaskExtractorAgent:
    """
    Custom agent that extracts and manages tasks from text.
    
    Purpose: Demonstrate how to build a specialized agent that:
    1. Finds action items in text (emails, documents, etc.)
    2. Prioritizes tasks based on urgency
    3. Tracks completion status
    4. Learns user preferences for task categories
    
    This shows all the key agent concepts in a simple domain.
    """
    
    def __init__(self):
        self.name = "TaskExtractorAgent"
        self.description = "Extracts and manages tasks from text input"
        
        # Agent's knowledge base (patterns for finding tasks)
        self.task_patterns = [
            r"(?:need to|must|should|have to)\s+([^.!?]+)",
            r"(?:action required|todo|task):\s*([^.!?]+)",
            r"(?:please|can you)\s+([^.!?]+)",
            r"(?:reminder|don't forget)\s+(?:to\s+)?([^.!?]+)"
        ]
        
        # Agent's memory
        self.memory = {
            "extracted_tasks": [],
            "completed_tasks": [],
            "user_preferences": {},
            "task_history": []
        }
        
        # Agent's tools
        self.tools = {
            "extract_tasks": self._extract_tasks_tool,
            "prioritize_tasks": self._prioritize_tasks_tool,
            "categorize_task": self._categorize_task_tool,
            "update_preferences": self._update_preferences_tool
        }
    
    def _extract_tasks_tool(self, text: str) -> List[Dict[str, Any]]:
        """Tool: Extract tasks from text using pattern matching."""
        tasks = []
        
        for pattern in self.task_patterns:
            matches = re.findall(pattern, text, re.IGNORECASE)
            for match in matches:
                task_text = match.strip()
                if len(task_text) > 3:  # Filter out very short matches
                    tasks.append({
                        "text": task_text,
                        "source_pattern": pattern,
                        "extracted_at": datetime.now().isoformat(),
                        "completed": False
                    })
        
        return tasks
    
    def _prioritize_tasks_tool(self, tasks: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Tool: Assign priority scores to tasks."""
        priority_keywords = {
            "urgent": 9,
            "asap": 9,
            "immediate": 9,
            "today": 8,
            "tomorrow": 7,
            "this week": 6,
            "important": 7,
            "critical": 9,
            "deadline": 8
        }
        
        for task in tasks:
            priority_score = 5  # Default priority
            text_lower = task["text"].lower()
            
            # Check for priority keywords
            for keyword, score in priority_keywords.items():
                if keyword in text_lower:
                    priority_score = max(priority_score, score)
            
            # Check user preferences
            user_pref = self.memory["user_preferences"].get("default_priority", 5)
            if priority_score == 5:  # If no keywords found, use user preference
                priority_score = user_pref
            
            task["priority"] = priority_score
        
        # Sort by priority (highest first)
        return sorted(tasks, key=lambda x: x["priority"], reverse=True)
    
    def _categorize_task_tool(self, task: Dict[str, Any]) -> str:
        """Tool: Categorize task based on content."""
        text = task["text"].lower()
        
        categories = {
            "meeting": ["meeting", "call", "schedule", "calendar"],
            "email": ["email", "send", "reply", "contact"],
            "document": ["write", "draft", "report", "document"],
            "research": ["research", "find", "look up", "investigate"],
            "administrative": ["file", "organize", "clean", "update"],
            "personal": ["buy", "pick up", "remember", "personal"]
        }
        
        for category, keywords in categories.items():
            if any(keyword in text for keyword in keywords):
                return category
        
        return "general"
    
    def _update_preferences_tool(self, feedback: Dict[str, Any]) -> None:
        """Tool: Update user preferences based on feedback."""
        feedback_type = feedback.get("type")
        
        if feedback_type == "priority_adjustment":
            # Learn from priority corrections
            old_priority = feedback["old_priority"]
            new_priority = feedback["new_priority"]
            task_category = feedback.get("category", "general")
            
            # Update preference for this category
            pref_key = f"priority_{task_category}"
            self.memory["user_preferences"][pref_key] = new_priority
            
            print(f"🎓 Learned: {task_category} tasks should have priority {new_priority}")
        
        elif feedback_type == "category_correction":
            # Learn from category corrections
            old_category = feedback["old_category"]
            new_category = feedback["new_category"]
            task_keywords = feedback.get("keywords", [])
            
            # Store the correction
            correction_key = f"category_correction_{old_category}_to_{new_category}"
            self.memory["user_preferences"][correction_key] = task_keywords
            
            print(f"🎓 Learned: Tasks with {task_keywords} should be {new_category}, not {old_category}")
    
    # Core Agent Methods: Perceive-Think-Act
    
    def perceive(self, environment: Dict[str, Any]) -> Dict[str, Any]:
        """
        PERCEIVE: Analyze input for task extraction opportunities.
        """
        text_input = environment.get("text", "")
        user_feedback = environment.get("feedback", [])
        
        perception = {
            "input_text": text_input,
            "text_length": len(text_input),
            "has_feedback": len(user_feedback) > 0,
            "feedback_items": user_feedback,
            "timestamp": datetime.now().isoformat()
        }
        
        print(f"🔍 PERCEIVE: Analyzing {len(text_input)} characters of text")
        if user_feedback:
            print(f"🔍 PERCEIVE: {len(user_feedback)} feedback items received")
        
        return perception
    
    def think(self, perception: Dict[str, Any]) -> List[Dict[str, Any]]:
        """
        THINK: Plan actions based on what was perceived.
        """
        actions = []
        
        # Process feedback first (learning)
        feedback_items = perception.get("feedback_items", [])
        for feedback in feedback_items:
            actions.append({
                "type": "process_feedback",
                "feedback": feedback
            })
        
        # Plan task extraction if there's text
        text_input = perception.get("input_text", "")
        if text_input and len(text_input) > 10:
            actions.append({
                "type": "extract_and_process_tasks",
                "text": text_input,
                "steps": [
                    "extract_tasks",
                    "categorize_tasks", 
                    "prioritize_tasks"
                ]
            })
        
        print(f"🧠 THINK: Planned {len(actions)} actions")
        return actions
    
    def act(self, actions: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        ACT: Execute the planned actions using available tools.
        """
        results = []
        
        for action in actions:
            if action["type"] == "process_feedback":
                # Process user feedback for learning
                feedback = action["feedback"]
                self.tools["update_preferences"](feedback)
                results.append({
                    "action": "learning",
                    "feedback_processed": True,
                    "feedback_type": feedback.get("type")
                })
            
            elif action["type"] == "extract_and_process_tasks":
                # Extract and process tasks from text
                text = action["text"]
                task_results = {"text_processed": text[:50] + "..."}
                
                # Step 1: Extract tasks
                raw_tasks = self.tools["extract_tasks"](text)
                task_results["tasks_extracted"] = len(raw_tasks)
                print(f"  📋 Extracted {len(raw_tasks)} potential tasks")
                
                # Step 2: Categorize each task
                for task in raw_tasks:
                    category = self.tools["categorize_task"](task)
                    task["category"] = category
                
                # Step 3: Prioritize tasks
                prioritized_tasks = self.tools["prioritize_tasks"](raw_tasks)
                task_results["tasks_prioritized"] = prioritized_tasks
                
                # Store in memory
                self.memory["extracted_tasks"].extend(prioritized_tasks)
                self.memory["task_history"].append({
                    "timestamp": datetime.now().isoformat(),
                    "tasks_count": len(prioritized_tasks),
                    "source_text": text[:100]
                })
                
                # Show results
                for i, task in enumerate(prioritized_tasks[:3]):  # Show top 3
                    print(f"  📋 Task {i+1}: [{task['category']}] {task['text'][:40]}... (Priority: {task['priority']})")
                
                results.append(task_results)
        
        print(f"⚡ ACT: Completed {len(results)} actions")
        return results
    
    def run_cycle(self, environment: Dict[str, Any]) -> Dict[str, Any]:
        """Execute complete perceive-think-act cycle."""
        print(f"\n🤖 {self.name.upper()} CYCLE")
        print("=" * 60)
        
        # 1. Perceive
        perception = self.perceive(environment)
        
        # 2. Think
        planned_actions = self.think(perception)
        
        # 3. Act
        results = self.act(planned_actions)
        
        cycle_result = {
            "agent": self.name,
            "timestamp": datetime.now().isoformat(),
            "perception": perception,
            "planned_actions": planned_actions,
            "results": results,
            "success": True
        }
        
        print("=" * 60)
        print(f"🤖 {self.name.upper()} CYCLE COMPLETE\n")
        
        return cycle_result
    
    def get_task_summary(self) -> Dict[str, Any]:
        """Get summary of extracted and managed tasks."""
        all_tasks = self.memory["extracted_tasks"]
        
        # Calculate statistics
        total_tasks = len(all_tasks)
        completed_tasks = len([t for t in all_tasks if t.get("completed", False)])
        
        # Group by category
        categories = {}
        priorities = {}
        
        for task in all_tasks:
            category = task.get("category", "unknown")
            priority = task.get("priority", 5)
            
            categories[category] = categories.get(category, 0) + 1
            priorities[priority] = priorities.get(priority, 0) + 1
        
        return {
            "total_tasks": total_tasks,
            "completed_tasks": completed_tasks,
            "completion_rate": completed_tasks / total_tasks if total_tasks > 0 else 0,
            "categories": categories,
            "priorities": priorities,
            "learned_preferences": len(self.memory["user_preferences"])
        }


def demonstrate_custom_agent():
    """Demonstrate building and using a custom agent."""
    print("🚀 BUILDING YOUR OWN AGENT TUTORIAL")
    print("=" * 80)
    print("🎯 Creating a TaskExtractorAgent from scratch")
    print()
    
    # Create the agent
    agent = TaskExtractorAgent()
    print(f"✅ Agent created: {agent.name}")
    print(f"📋 Purpose: {agent.description}")
    print(f"🛠️ Tools available: {list(agent.tools.keys())}")
    print()
    
    # Test with sample text
    sample_text = """
    Hi team,
    
    I need to finish the quarterly report by Friday. Please remember to 
    send me your section updates by Wednesday. We also need to schedule 
    a meeting with the client next week to discuss the project timeline.
    
    Don't forget to review the budget proposal - it's urgent and needs 
    approval by tomorrow. I should also research the new compliance 
    requirements that were mentioned in yesterday's call.
    
    Thanks!
    """
    
    print("📝 Processing sample text:")
    print(f"   '{sample_text[:100]}...'")
    print()
    
    # Run agent cycle
    environment = {"text": sample_text, "feedback": []}
    result = agent.run_cycle(environment)
    
    # Show summary
    print("📊 TASK EXTRACTION SUMMARY:")
    summary = agent.get_task_summary()
    
    print(f"   📋 Total tasks extracted: {summary['total_tasks']}")
    print(f"   📂 Categories found: {list(summary['categories'].keys())}")
    print(f"   ⭐ Priority distribution: {summary['priorities']}")
    print()
    
    # Demonstrate learning with feedback
    print("🎓 DEMONSTRATING LEARNING:")
    print("   User provides feedback that 'research' tasks should be priority 8")
    
    feedback_environment = {
        "text": "",
        "feedback": [{
            "type": "priority_adjustment",
            "old_priority": 5,
            "new_priority": 8,
            "category": "research"
        }]
    }
    
    agent.run_cycle(feedback_environment)
    
    # Test learning by processing text with research task
    research_text = "I need to research the new compliance requirements for our industry."
    print(f"\n   Processing new text: '{research_text}'")
    
    agent.run_cycle({"text": research_text, "feedback": []})
    
    # Show final summary
    final_summary = agent.get_task_summary()
    print(f"\n📈 FINAL RESULTS:")
    print(f"   📋 Total tasks: {final_summary['total_tasks']}")
    print(f"   🎓 Preferences learned: {final_summary['learned_preferences']}")
    print()
    
    print("✅ CUSTOM AGENT TUTORIAL COMPLETE!")
    print()
    print("🎯 Key Concepts Demonstrated:")
    print("   1. ✅ Agent specialization (task extraction domain)")
    print("   2. ✅ Tool-based capabilities (extract, categorize, prioritize)")
    print("   3. ✅ Perceive-Think-Act loop implementation")
    print("   4. ✅ Learning from user feedback")
    print("   5. ✅ Memory and state management")
    print()
    print("📚 To build your own agent:")
    print("   • Define the agent's purpose and domain")
    print("   • Create specialized tools for that domain")
    print("   • Implement perceive(), think(), act() methods")
    print("   • Add learning and memory capabilities")
    print("   • Test with real-world scenarios")


if __name__ == "__main__":
    demonstrate_custom_agent()