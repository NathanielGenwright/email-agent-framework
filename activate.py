#!/usr/bin/env python3
"""
Email Agent System Activator

This script activates and manages the email agent system for production use.
"""

import os
import sys
import json
import subprocess
import signal
import time
from pathlib import Path
from datetime import datetime
import threading


class EmailAgentActivator:
    """System activator for email agents."""
    
    def __init__(self):
        self.install_dir = Path.home() / ".email-agent"
        self.config_file = self.install_dir / "config.json"
        self.pid_file = self.install_dir / "email-agent.pid"
        self.log_file = self.install_dir / "logs" / "email-agent.log"
        self.running = False
        
    def activate(self):
        """Activate the email agent system."""
        print("🚀 Email Agent System Activator")
        print("=" * 50)
        
        try:
            self.check_installation()
            self.validate_configuration()
            self.start_agents()
            
            print("✅ Email Agent System activated successfully!")
            print(f"📊 Status: Running")
            print(f"📁 Install Directory: {self.install_dir}")
            print(f"📝 Log File: {self.log_file}")
            print(f"🔧 Config File: {self.config_file}")
            
            return True
            
        except Exception as e:
            print(f"❌ Activation failed: {e}")
            return False
    
    def check_installation(self):
        """Check if system is properly installed."""
        print("🔍 Checking installation...")
        
        if not self.install_dir.exists():
            raise Exception(f"Email agent not installed. Run install.py first.")
        
        if not self.config_file.exists():
            raise Exception(f"Configuration file not found: {self.config_file}")
        
        src_dir = self.install_dir / "src"
        if not src_dir.exists():
            raise Exception(f"Source code not found: {src_dir}")
        
        print("✅ Installation verified")
    
    def validate_configuration(self):
        """Validate configuration settings."""
        print("⚙️  Validating configuration...")
        
        with open(self.config_file, 'r') as f:
            config = json.load(f)
        
        # Check email configuration
        email_config = config.get('email', {})
        if not email_config.get('address'):
            raise Exception("Email address not configured. Please edit config.json")
        
        if not email_config.get('password'):
            print("⚠️  Warning: Email password not configured")
            print("   Set EMAIL_PASSWORD environment variable or edit config.json")
        
        # Check AI configuration (optional)
        ai_config = config.get('ai', {})
        if not ai_config.get('openai_api_key') and not ai_config.get('anthropic_api_key'):
            print("⚠️  Warning: No AI API keys configured")
            print("   AI response generation will be limited")
        
        print("✅ Configuration validated")
        return config
    
    def start_agents(self):
        """Start the email agent system."""
        print("🤖 Starting email agents...")
        
        # Check if already running
        if self.is_running():
            print("⚠️  Email agents already running")
            return
        
        # Create log directory
        self.log_file.parent.mkdir(exist_ok=True)
        
        # Start the main system
        try:
            # Change to install directory
            os.chdir(self.install_dir)
            
            # Set up environment
            env = os.environ.copy()
            env['PYTHONPATH'] = str(self.install_dir)
            
            # Start the system
            with open(self.log_file, 'a') as log:
                log.write(f"\n=== Email Agent System Started: {datetime.now()} ===\n")
                
                process = subprocess.Popen([
                    sys.executable, "-m", "src.main"
                ], 
                stdout=log, 
                stderr=log,
                env=env,
                preexec_fn=os.setsid  # Create new process group
                )
                
                # Save PID
                with open(self.pid_file, 'w') as f:
                    f.write(str(process.pid))
                
                # Wait a moment to check if it started successfully
                time.sleep(2)
                if process.poll() is None:
                    print("✅ Email agents started successfully")
                    print(f"   PID: {process.pid}")
                    print(f"   Logs: {self.log_file}")
                else:
                    raise Exception("Process failed to start")
                
        except Exception as e:
            raise Exception(f"Failed to start agents: {e}")
    
    def stop_agents(self):
        """Stop the email agent system."""
        print("🛑 Stopping email agents...")
        
        if not self.is_running():
            print("⚠️  Email agents not running")
            return True
        
        try:
            with open(self.pid_file, 'r') as f:
                pid = int(f.read().strip())
            
            # Terminate the process group
            os.killpg(os.getpgid(pid), signal.SIGTERM)
            
            # Wait for graceful shutdown
            for _ in range(10):
                if not self.is_running():
                    break
                time.sleep(1)
            else:
                # Force kill if still running
                os.killpg(os.getpgid(pid), signal.SIGKILL)
            
            # Remove PID file
            if self.pid_file.exists():
                self.pid_file.unlink()
            
            print("✅ Email agents stopped")
            return True
            
        except Exception as e:
            print(f"❌ Error stopping agents: {e}")
            return False
    
    def restart_agents(self):
        """Restart the email agent system."""
        print("🔄 Restarting email agents...")
        self.stop_agents()
        time.sleep(2)
        return self.activate()
    
    def is_running(self):
        """Check if the system is running."""
        if not self.pid_file.exists():
            return False
        
        try:
            with open(self.pid_file, 'r') as f:
                pid = int(f.read().strip())
            
            # Check if process exists
            os.kill(pid, 0)
            return True
            
        except (ValueError, OSError):
            # PID file corrupted or process doesn't exist
            if self.pid_file.exists():
                self.pid_file.unlink()
            return False
    
    def get_status(self):
        """Get system status."""
        print("📊 Email Agent System Status")
        print("=" * 40)
        
        # Installation status
        if self.install_dir.exists():
            print("✅ Installation: Found")
            print(f"   Location: {self.install_dir}")
        else:
            print("❌ Installation: Not found")
            return
        
        # Configuration status
        if self.config_file.exists():
            print("✅ Configuration: Found")
            try:
                with open(self.config_file, 'r') as f:
                    config = json.load(f)
                    email_configured = bool(config.get('email', {}).get('address'))
                    ai_configured = bool(config.get('ai', {}).get('openai_api_key') or 
                                       config.get('ai', {}).get('anthropic_api_key'))
                    
                    print(f"   Email configured: {'✅' if email_configured else '❌'}")
                    print(f"   AI configured: {'✅' if ai_configured else '⚠️'}")
            except Exception as e:
                print(f"   Error reading config: {e}")
        else:
            print("❌ Configuration: Not found")
        
        # Running status
        if self.is_running():
            print("✅ Status: Running")
            try:
                with open(self.pid_file, 'r') as f:
                    pid = f.read().strip()
                    print(f"   PID: {pid}")
            except:
                pass
        else:
            print("❌ Status: Not running")
        
        # Log file status
        if self.log_file.exists():
            print("✅ Logs: Available")
            print(f"   Location: {self.log_file}")
            print(f"   Size: {self.log_file.stat().st_size} bytes")
        else:
            print("⚠️  Logs: No log file found")
    
    def show_logs(self, lines=50):
        """Show recent log entries."""
        if not self.log_file.exists():
            print("❌ No log file found")
            return
        
        print(f"📝 Recent log entries (last {lines} lines):")
        print("=" * 50)
        
        try:
            with open(self.log_file, 'r') as f:
                log_lines = f.readlines()
                for line in log_lines[-lines:]:
                    print(line.rstrip())
        except Exception as e:
            print(f"Error reading log file: {e}")


def main():
    """Main activation function."""
    activator = EmailAgentActivator()
    
    if len(sys.argv) < 2:
        print("Usage: python activate.py [start|stop|restart|status|logs]")
        sys.exit(1)
    
    command = sys.argv[1].lower()
    
    if command == "start":
        activator.activate()
    elif command == "stop":
        activator.stop_agents()
    elif command == "restart":
        activator.restart_agents()
    elif command == "status":
        activator.get_status()
    elif command == "logs":
        lines = int(sys.argv[2]) if len(sys.argv) > 2 else 50
        activator.show_logs(lines)
    else:
        print(f"Unknown command: {command}")
        print("Available commands: start, stop, restart, status, logs")
        sys.exit(1)


if __name__ == "__main__":
    main()