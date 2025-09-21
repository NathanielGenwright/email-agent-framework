"""
Command Line Interface for the Email Agent System.

This CLI demonstrates how to interact with agents and provides a practical
interface for learning and testing agent capabilities.
"""

import click
import json
import logging
from datetime import datetime
from typing import Dict, Any
from rich.console import Console
from rich.table import Table
from rich.panel import Panel
from rich.progress import Progress, SpinnerColumn, TextColumn
from rich.prompt import Confirm, Prompt

from .agent.email_master_agent import EmailMasterAgent
from .agent.email_classifier import EmailClassifier
from .agent.email_responder import EmailResponder
from .agent.inbox_organizer import InboxOrganizer
from .memory.persistent_memory import memory
from .config.settings import settings

# Setup rich console for beautiful output
console = Console()

# Configure logging
logging.basicConfig(
    level=getattr(logging, settings.log_level),
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

logger = logging.getLogger(__name__)


@click.group()
@click.option('--verbose', '-v', is_flag=True, help='Enable verbose logging')
def cli(verbose):
    """Email Agent System - AI-powered email management."""
    if verbose:
        logging.getLogger().setLevel(logging.DEBUG)
    
    console.print(Panel.fit(
        "[bold blue]Email Agent System[/bold blue]\n"
        "AI-powered email management with learning capabilities",
        border_style="blue"
    ))


@cli.command()
def status():
    """Show system status and agent information."""
    console.print("[bold]System Status[/bold]")
    
    try:
        # Initialize master agent
        master_agent = EmailMasterAgent()
        
        # Get comprehensive status
        status_info = master_agent.get_comprehensive_status()
        
        # Display master agent status
        master_table = Table(title="Master Agent Status", show_header=True, header_style="bold magenta")
        master_table.add_column("Property", style="cyan")
        master_table.add_column("Value", style="white")
        
        master_status = status_info["master_agent"]
        master_table.add_row("Name", master_status["name"])
        master_table.add_row("Description", master_status["description"])
        master_table.add_row("Active", str(master_status["is_active"]))
        master_table.add_row("Available Tools", str(len(master_status["available_tools"])))
        
        console.print(master_table)
        console.print()
        
        # Display sub-agents status
        sub_agents_table = Table(title="Sub-Agents Status", show_header=True, header_style="bold green")
        sub_agents_table.add_column("Agent", style="cyan")
        sub_agents_table.add_column("Tools", style="white")
        sub_agents_table.add_column("Memory Events", style="white")
        
        for agent_name, agent_status in status_info["sub_agents"].items():
            memory_summary = agent_status["memory_summary"]
            sub_agents_table.add_row(
                agent_name.title(),
                str(len(agent_status["available_tools"])),
                str(memory_summary["short_term_events"])
            )
        
        console.print(sub_agents_table)
        console.print()
        
        # Display performance metrics
        metrics_table = Table(title="Performance Metrics", show_header=True, header_style="bold yellow")
        metrics_table.add_column("Metric", style="cyan")
        metrics_table.add_column("Value", style="white")
        
        for metric, value in status_info["performance_metrics"].items():
            metrics_table.add_row(metric.replace("_", " ").title(), str(value))
        
        console.print(metrics_table)
        console.print()
        
        # Display memory system info
        memory_info = status_info["memory_summary"]
        memory_table = Table(title="Learning System", show_header=True, header_style="bold red")
        memory_table.add_column("Component", style="cyan")
        memory_table.add_column("Count", style="white")
        
        memory_table.add_row("Total Events", str(memory_info["total_events"]))
        memory_table.add_row("User Preferences", str(memory_info["total_preferences"]))
        memory_table.add_row("Recent Feedback", str(memory_info["recent_feedback_count"]))
        
        console.print(memory_table)
        
    except Exception as e:
        console.print(f"[bold red]Error getting status: {e}[/bold red]")


@cli.command()
@click.option('--limit', default=10, help='Number of emails to process')
@click.option('--dry-run', is_flag=True, help='Show what would be done without executing')
def process(limit, dry_run):
    """Process recent emails using the email agent system."""
    console.print(f"[bold]Processing {limit} recent emails[/bold]")
    
    if dry_run:
        console.print("[yellow]DRY RUN MODE - No actions will be executed[/yellow]")
    
    try:
        master_agent = EmailMasterAgent()
        
        with Progress(
            SpinnerColumn(),
            TextColumn("[progress.description]{task.description}"),
            console=console
        ) as progress:
            
            # Step 1: Perception
            task1 = progress.add_task("Getting recent emails...", total=None)
            perception = master_agent.perceive()
            total_emails = perception.get("total_new_emails", 0)
            progress.update(task1, description=f"Found {total_emails} emails")
            
            if total_emails == 0:
                console.print("[yellow]No new emails to process[/yellow]")
                return
            
            # Step 2: Planning
            task2 = progress.add_task("Planning processing workflow...", total=None)
            actions = master_agent.think(perception)
            progress.update(task2, description=f"Planned {len(actions)} workflow actions")
            
            # Step 3: Execution
            if not dry_run:
                task3 = progress.add_task("Executing email processing...", total=None)
                results = master_agent.act(actions)
                progress.update(task3, description=f"Completed {len(results)} workflows")
                
                # Display results
                for i, result in enumerate(results):
                    if result.success:
                        workflow_data = result.result
                        console.print(f"\n[green]Workflow {i+1} completed successfully[/green]")
                        
                        # Show analysis results
                        if "analysis_results" in workflow_data:
                            analysis = workflow_data["analysis_results"]
                            console.print(f"  • Classified {len(analysis.get('classification_results', []))} emails")
                            console.print(f"  • Generated {len(analysis.get('response_candidates', []))} response suggestions")
                            console.print(f"  • Created {len(analysis.get('organization_suggestions', []))} organization suggestions")
                        
                        # Show execution results
                        if "execution_results" in workflow_data:
                            execution = workflow_data["execution_results"]
                            console.print(f"  • Successfully executed {execution.get('successful_actions', 0)} actions")
                            if execution.get('failed_actions', 0) > 0:
                                console.print(f"  • [red]Failed to execute {execution['failed_actions']} actions[/red]")
                    else:
                        console.print(f"[red]Workflow {i+1} failed[/red]")
            else:
                # Show what would be done in dry run
                console.print("\n[bold]Planned Actions (Dry Run):[/bold]")
                for action in actions:
                    console.print(f"  • {action['type']}: {len(action.get('emails', []))} emails")
                    for step in action.get('steps', []):
                        console.print(f"    - {step}")
        
    except Exception as e:
        console.print(f"[bold red]Error processing emails: {e}[/bold red]")
        logger.exception("Email processing failed")


@cli.command()
def classify():
    """Run email classification on recent emails."""
    console.print("[bold]Running Email Classification[/bold]")
    
    try:
        classifier = EmailClassifier()
        
        with Progress(
            SpinnerColumn(),
            TextColumn("[progress.description]{task.description}"),
            console=console
        ) as progress:
            
            task = progress.add_task("Classifying emails...", total=None)
            
            # Run classification cycle
            result = classifier.run_cycle()
            
            if result["success"]:
                # Display classification results
                console.print("\n[green]Classification completed successfully[/green]")
                
                # Show summary
                summary = classifier.get_classification_summary()
                
                categories_table = Table(title="Classification Results", show_header=True)
                categories_table.add_column("Category", style="cyan")
                categories_table.add_column("Count", style="white")
                
                for category, count in summary["category_distribution"].items():
                    categories_table.add_row(category.title(), str(count))
                
                console.print(categories_table)
                console.print(f"\nTotal emails classified: {summary['total_classified']}")
            else:
                console.print(f"[red]Classification failed: {result.get('error', 'Unknown error')}[/red]")
        
    except Exception as e:
        console.print(f"[bold red]Error running classification: {e}[/bold red]")


@cli.command()
def responses():
    """Show pending response suggestions."""
    console.print("[bold]Pending Response Suggestions[/bold]")
    
    try:
        responder = EmailResponder()
        pending = responder.get_pending_responses()
        
        if not pending:
            console.print("[yellow]No pending responses[/yellow]")
            return
        
        for i, response in enumerate(pending):
            console.print(f"\n[bold cyan]Response {i+1}[/bold cyan]")
            console.print(Panel(
                f"[bold]From:[/bold] {response['original_sender']}\n"
                f"[bold]Subject:[/bold] {response['original_subject']}\n"
                f"[bold]Intent:[/bold] {response['intent']}\n"
                f"[bold]Priority:[/bold] {response['priority']}\n\n"
                f"[bold]Suggested Response:[/bold]\n{response['suggested_response']}",
                title=f"Email ID: {response['email_id']}",
                border_style="blue"
            ))
            
            # Ask for user action
            if Confirm.ask("Send this response?"):
                success = responder.send_response(response['email_id'], approved=True)
                if success:
                    console.print("[green]Response sent![/green]")
                else:
                    console.print("[red]Failed to send response[/red]")
            elif Confirm.ask("Provide feedback on this response?"):
                feedback = Prompt.ask("Enter your feedback")
                # Process feedback (implement feedback processing)
                console.print("[green]Feedback recorded[/green]")
        
    except Exception as e:
        console.print(f"[bold red]Error getting responses: {e}[/bold red]")


@cli.command()
def organize():
    """Run inbox organization."""
    console.print("[bold]Running Inbox Organization[/bold]")
    
    try:
        organizer = InboxOrganizer()
        
        with Progress(
            SpinnerColumn(),
            TextColumn("[progress.description]{task.description}"),
            console=console
        ) as progress:
            
            task = progress.add_task("Organizing inbox...", total=None)
            
            # Run organization cycle
            result = organizer.run_cycle()
            
            if result["success"]:
                console.print("\n[green]Organization completed successfully[/green]")
                
                # Show organization report
                report = organizer.get_organization_report()
                
                console.print(f"Recent activities: {report['recent_activities']}")
                
                # Show health metrics if available
                health_metrics = report.get("health_metrics", {})
                if health_metrics:
                    metrics_table = Table(title="Organization Metrics")
                    metrics_table.add_column("Metric", style="cyan")
                    metrics_table.add_column("Value", style="white")
                    
                    for metric, value in health_metrics.items():
                        metrics_table.add_row(metric.replace("_", " ").title(), str(value))
                    
                    console.print(metrics_table)
            else:
                console.print(f"[red]Organization failed: {result.get('error', 'Unknown error')}[/red]")
        
    except Exception as e:
        console.print(f"[bold red]Error running organization: {e}[/bold red]")


@cli.command()
def memory():
    """Show memory and learning information."""
    console.print("[bold]Memory and Learning System[/bold]")
    
    try:
        learning_summary = memory.get_learning_summary()
        
        # Summary table
        summary_table = Table(title="Learning Summary", show_header=True)
        summary_table.add_column("Component", style="cyan")
        summary_table.add_column("Value", style="white")
        
        summary_table.add_row("Total Events", str(learning_summary["total_events"]))
        summary_table.add_row("Total Preferences", str(learning_summary["total_preferences"]))
        summary_table.add_row("Recent Feedback", str(learning_summary["recent_feedback_count"]))
        
        console.print(summary_table)
        console.print()
        
        # Preferences by category
        if learning_summary["preferences_by_category"]:
            prefs_table = Table(title="Learned Preferences by Category", show_header=True)
            prefs_table.add_column("Category", style="cyan")
            prefs_table.add_column("Count", style="white")
            
            for category, count in learning_summary["preferences_by_category"].items():
                prefs_table.add_row(category.title(), str(count))
            
            console.print(prefs_table)
            console.print()
        
        # Learning metrics
        metrics = learning_summary["learning_metrics"]
        console.print(f"[bold]Learning Effectiveness:[/bold]")
        console.print(f"  • Average Confidence: {metrics['average_confidence']:.2f}")
        console.print(f"  • High Confidence Preferences: {metrics['high_confidence_percentage']:.1f}%")
        
    except Exception as e:
        console.print(f"[bold red]Error accessing memory system: {e}[/bold red]")


@cli.command()
@click.argument('email_id')
@click.option('--feedback-type', type=click.Choice(['classification', 'response', 'organization', 'priority']))
@click.option('--feedback-data', help='JSON string with feedback data')
def feedback(email_id, feedback_type, feedback_data):
    """Provide feedback to help the agent learn."""
    console.print(f"[bold]Providing Feedback for Email {email_id}[/bold]")
    
    try:
        if not feedback_data:
            # Interactive feedback collection
            if feedback_type == "classification":
                correct_category = Prompt.ask("What is the correct category?")
                feedback_data = json.dumps({"correct_category": correct_category})
            elif feedback_type == "response":
                approved = Confirm.ask("Was the suggested response appropriate?")
                feedback_data = json.dumps({"approved": approved})
            elif feedback_type == "priority":
                correct_priority = int(Prompt.ask("What should the priority be (1-10)?"))
                feedback_data = json.dumps({"correct_priority": correct_priority})
            else:
                feedback_data = json.dumps({"feedback": Prompt.ask("Enter feedback")})
        
        # Parse feedback data
        try:
            feedback_dict = json.loads(feedback_data)
        except json.JSONDecodeError:
            console.print("[red]Invalid JSON in feedback data[/red]")
            return
        
        # Submit feedback
        master_agent = EmailMasterAgent()
        success = master_agent.process_user_feedback(
            email_id, 
            f"{feedback_type}_correction", 
            feedback_dict
        )
        
        if success:
            console.print("[green]Feedback recorded successfully![/green]")
            console.print("The agent will learn from this feedback to improve future performance.")
        else:
            console.print("[red]Failed to record feedback[/red]")
        
    except Exception as e:
        console.print(f"[bold red]Error processing feedback: {e}[/bold red]")


@cli.command()
def interactive():
    """Interactive mode for exploring agent capabilities."""
    console.print("[bold]Interactive Email Agent Mode[/bold]")
    console.print("Type 'help' for available commands, 'quit' to exit")
    
    master_agent = EmailMasterAgent()
    
    while True:
        try:
            command = Prompt.ask("\n[cyan]email-agent>[/cyan]").strip().lower()
            
            if command == "quit" or command == "exit":
                break
            elif command == "help":
                console.print("""
[bold]Available Commands:[/bold]
  status     - Show system status
  process    - Process recent emails
  classify   - Run classification
  respond    - Show response suggestions  
  organize   - Run organization
  memory     - Show learning information
  feedback   - Provide feedback (interactive)
  quit/exit  - Exit interactive mode
                """)
            elif command == "status":
                status_info = master_agent.get_comprehensive_status()
                console.print(f"System Health: {status_info['system_health']['overall_status']}")
                console.print(f"Emails Processed: {status_info['performance_metrics']['emails_processed']}")
                console.print(f"Active Sub-agents: {len(status_info['sub_agents'])}")
            
            elif command == "process":
                console.print("Running email processing...")
                result = master_agent.run_cycle()
                if result["success"]:
                    console.print("[green]Processing completed successfully[/green]")
                else:
                    console.print(f"[red]Processing failed: {result.get('error', 'Unknown error')}[/red]")
            
            elif command == "memory":
                summary = memory.get_learning_summary()
                console.print(f"Events: {summary['total_events']}, Preferences: {summary['total_preferences']}")
                console.print(f"Recent feedback: {summary['recent_feedback_count']}")
            
            else:
                console.print(f"[red]Unknown command: {command}[/red]")
                console.print("Type 'help' for available commands")
        
        except KeyboardInterrupt:
            break
        except Exception as e:
            console.print(f"[red]Error: {e}[/red]")
    
    console.print("\n[bold]Goodbye![/bold]")


if __name__ == "__main__":
    cli()