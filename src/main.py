"""
Main entry point for the Email Agent System.

This file demonstrates how to initialize and run the complete agent system.
"""

import logging
import sys
from pathlib import Path

# Add src to path for imports
sys.path.append(str(Path(__file__).parent))

from agent.email_master_agent import EmailMasterAgent
from config.settings import settings

# Configure logging
logging.basicConfig(
    level=getattr(logging, settings.log_level),
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

logger = logging.getLogger(__name__)


def main():
    """Main function to demonstrate the email agent system."""
    logger.info("Starting Email Agent System")
    
    try:
        # Initialize the master agent
        master_agent = EmailMasterAgent()
        
        # Display system information
        print("=" * 60)
        print("Email Agent System - AI-Powered Email Management")
        print("=" * 60)
        
        status = master_agent.get_comprehensive_status()
        print(f"Master Agent: {status['master_agent']['name']}")
        print(f"Sub-agents: {len(status['sub_agents'])}")
        print(f"System Health: {status['system_health']['overall_status']}")
        print()
        
        # Run a demonstration cycle
        print("Running demonstration email processing cycle...")
        result = master_agent.run_cycle()
        
        if result["success"]:
            print("✓ Email processing completed successfully")
            
            # Show some results if available
            if "analysis_results" in result:
                analysis = result["analysis_results"]
                print(f"  • Processed {analysis.get('total_emails', 0)} emails")
                print(f"  • Classifications: {len(analysis.get('classification_results', []))}")
                print(f"  • Response suggestions: {len(analysis.get('response_candidates', []))}")
                print(f"  • Organization actions: {len(analysis.get('organization_suggestions', []))}")
        else:
            print(f"✗ Email processing failed: {result.get('error', 'Unknown error')}")
        
        print()
        print("For interactive use, run: python -m src.cli interactive")
        print("For help, run: python -m src.cli --help")
        
    except Exception as e:
        logger.error(f"System startup failed: {e}")
        print(f"Error: {e}")
        return 1
    
    return 0


if __name__ == "__main__":
    sys.exit(main())