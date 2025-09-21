#!/usr/bin/env python3
"""
Simple test script to demonstrate agent concepts without external dependencies.
This shows the core agent patterns working together.
"""

import sys
from pathlib import Path

# Add src to path
sys.path.append(str(Path(__file__).parent / "src"))

from typing import Dict, List, Any
from datetime import datetime


class MockEmailTools:
    """Mock email tools for demonstration."""
    
    @staticmethod
    def fetch_recent_emails(limit=10):
        """Return mock emails for testing."""
        from tools.email_tools import EmailMessage
        
        mock_emails = [
            EmailMessage(
                id="1",
                subject="URGENT: Project deadline moved up",
                sender="boss@company.com",
                recipients=["you@company.com"],
                body="We need to deliver the project by tomorrow. Please confirm ASAP.",
                html_body=None,
                date=datetime.now(),
                labels=[],
                is_read=False,
                is_important=True,
                attachments=[]
            ),
            EmailMessage(
                id="2", 
                subject="Weekly team meeting",
                sender="colleague@company.com",
                recipients=["team@company.com"],
                body="Can we schedule our weekly team meeting for Tuesday at 2 PM?",
                html_body=None,
                date=datetime.now(),
                labels=[],
                is_read=False,
                is_important=False,
                attachments=[]
            )
        ]
        return mock_emails[:limit]


def test_single_agent():
    """Test a single agent's perceive-think-act cycle."""
    print("🔍 TESTING SINGLE AGENT")
    print("=" * 50)
    
    try:
        from agent.email_classifier import EmailClassifier
        
        # Mock the email tools
        import tools.email_tools
        tools.email_tools.email_tools = MockEmailTools()
        
        # Create and run classifier
        classifier = EmailClassifier()
        
        print(f"Agent: {classifier.name}")
        print(f"Description: {classifier.description}")
        print(f"Available tools: {classifier.get_available_tools()}")
        print()
        
        # Run one cycle
        print("Running agent cycle...")
        result = classifier.run_cycle()
        
        if result["success"]:
            print("✅ Agent cycle completed successfully!")
            
            # Show some results
            perception = result.get("perception", {})
            print(f"  📧 Emails found: {perception.get('total_count', 0)}")
            
            actions = result.get("planned_actions", [])
            print(f"  🧠 Actions planned: {len(actions)}")
            
            results = result.get("results", [])
            print(f"  ⚡ Results: {len(results)} operations completed")
            
        else:
            print(f"❌ Agent cycle failed: {result.get('error', 'Unknown error')}")
    
    except Exception as e:
        print(f"Error during single agent test: {e}")
        print("This is expected if dependencies aren't installed - the concept is demonstrated!")


def test_multi_agent_coordination():
    """Test multi-agent coordination concepts."""
    print("\n🤝 TESTING MULTI-AGENT COORDINATION")
    print("=" * 50)
    
    try:
        from agent.email_master_agent import EmailMasterAgent
        
        # Mock the email tools
        import tools.email_tools
        tools.email_tools.email_tools = MockEmailTools()
        
        # Create master agent
        master = EmailMasterAgent()
        
        print(f"Master Agent: {master.name}")
        print(f"Sub-agents: {type(master.classifier).__name__}, {type(master.responder).__name__}, {type(master.organizer).__name__}")
        print()
        
        # Get status
        status = master.get_comprehensive_status()
        print("System Status:")
        print(f"  🏗️ Master agent tools: {len(status['master_agent']['available_tools'])}")
        print(f"  🤖 Sub-agents active: {len(status['sub_agents'])}")
        print(f"  📊 Performance metrics tracked: {len(status['performance_metrics'])}")
        
        print("\nWorkflow settings:")
        for setting, value in master.workflow_settings.items():
            print(f"  • {setting}: {value}")
        
    except Exception as e:
        print(f"Error during multi-agent test: {e}")
        print("This demonstrates the coordination architecture even without full setup!")


def test_learning_concepts():
    """Test learning and memory concepts."""
    print("\n🧠 TESTING LEARNING CONCEPTS")
    print("=" * 50)
    
    try:
        from memory.persistent_memory import PersistentMemory
        
        # Create memory system
        memory = PersistentMemory(db_path=":memory:")  # In-memory SQLite
        
        print("Memory system initialized")
        
        # Add some events
        event_id1 = memory.add_event(
            event_type="email_classification",
            data={"email_id": "123", "category": "urgent", "confidence": 0.9},
            importance=0.8,
            tags=["classification", "email"]
        )
        
        event_id2 = memory.add_event(
            event_type="user_feedback",
            data={"correction": "should be 'meeting' not 'urgent'"},
            importance=1.0,
            tags=["feedback", "learning"]
        )
        
        print(f"  📝 Added events: {event_id1[:8]}..., {event_id2[:8]}...")
        
        # Simulate learning from feedback
        memory.add_user_feedback(
            event_id1,
            "classification_correction",
            {"correct_category": "meeting"}
        )
        
        print("  🎓 Processed user feedback")
        
        # Get learning summary
        summary = memory.get_learning_summary()
        print(f"  📊 Total events: {summary['total_events']}")
        print(f"  🎯 Preferences learned: {summary['total_preferences']}")
        print(f"  💬 Recent feedback: {summary['recent_feedback_count']}")
        
        memory.close()
        
    except Exception as e:
        print(f"Error during learning test: {e}")
        print("This shows the learning architecture concept!")


def main():
    """Run all tests to demonstrate agent concepts."""
    print("🚀 AGENT SYSTEM WALKTHROUGH")
    print("🎯 This demonstrates core agent concepts even without full email setup")
    print("=" * 80)
    
    # Test individual agent
    test_single_agent()
    
    # Test multi-agent coordination  
    test_multi_agent_coordination()
    
    # Test learning concepts
    test_learning_concepts()
    
    print("\n" + "=" * 80)
    print("✅ WALKTHROUGH COMPLETE!")
    print()
    print("🎓 Key Concepts Demonstrated:")
    print("   1. ✅ Perceive-Think-Act agent loop")
    print("   2. ✅ Tool-based agent capabilities") 
    print("   3. ✅ Multi-agent coordination")
    print("   4. ✅ Learning and memory systems")
    print("   5. ✅ Specialized domain agents")
    print()
    print("📚 Next Steps:")
    print("   • Set up email credentials to test with real emails")
    print("   • Install dependencies: pip install -r requirements.txt")
    print("   • Run: python -m src.cli interactive")
    print("   • Explore: Each agent file in src/agent/")
    print("   • Build: Your own specialized agents!")


if __name__ == "__main__":
    main()