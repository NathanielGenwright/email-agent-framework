#!/usr/bin/env python3
"""
Email Agent System Installer

This script installs and configures the complete email agent system
for production use with real email inboxes.
"""

import os
import sys
import subprocess
import shutil
from pathlib import Path
import json


class EmailAgentInstaller:
    """Complete installation system for email agents."""
    
    def __init__(self):
        self.project_root = Path(__file__).parent
        self.install_dir = Path.home() / ".email-agent"
        self.config_file = self.install_dir / "config.json"
        self.service_file = Path("/etc/systemd/system/email-agent.service")
        
    def install(self):
        """Complete installation process."""
        print("🚀 Email Agent System Installer")
        print("=" * 50)
        
        try:
            self.check_requirements()
            self.create_directories()
            self.install_dependencies()
            self.copy_files()
            self.setup_configuration()
            self.create_service()
            self.setup_permissions()
            
            print("\n✅ Installation completed successfully!")
            print(f"📁 Installed to: {self.install_dir}")
            print(f"⚙️  Configuration: {self.config_file}")
            print("\n🎯 Next steps:")
            print("1. Edit the configuration file with your email credentials")
            print("2. Run: email-agent activate")
            print("3. Check status: email-agent status")
            
        except Exception as e:
            print(f"❌ Installation failed: {e}")
            return False
        
        return True
    
    def check_requirements(self):
        """Check system requirements."""
        print("🔍 Checking requirements...")
        
        # Check Python version
        if sys.version_info < (3, 8):
            raise Exception("Python 3.8 or higher required")
        
        # Check if running as root for system service
        if os.geteuid() == 0:
            print("✅ Running as root - can install system service")
        else:
            print("⚠️  Not running as root - will install for current user only")
    
    def create_directories(self):
        """Create necessary directories."""
        print("📁 Creating directories...")
        
        directories = [
            self.install_dir,
            self.install_dir / "src",
            self.install_dir / "logs",
            self.install_dir / "data",
            self.install_dir / "backups"
        ]
        
        for directory in directories:
            directory.mkdir(parents=True, exist_ok=True)
            print(f"   Created: {directory}")
    
    def install_dependencies(self):
        """Install Python dependencies."""
        print("📦 Installing dependencies...")
        
        requirements_file = self.project_root / "requirements.txt"
        if requirements_file.exists():
            subprocess.run([
                sys.executable, "-m", "pip", "install", "-r", str(requirements_file)
            ], check=True)
            print("✅ Dependencies installed")
        else:
            # Install core dependencies
            core_deps = [
                "pydantic>=2.0.0",
                "rich>=13.0.0", 
                "click>=8.1.0",
                "python-dotenv>=1.0.0",
                "sqlalchemy>=2.0.0"
            ]
            
            for dep in core_deps:
                subprocess.run([sys.executable, "-m", "pip", "install", dep], check=True)
            
            print("✅ Core dependencies installed")
    
    def copy_files(self):
        """Copy application files."""
        print("📋 Copying application files...")
        
        # Copy source code
        src_dest = self.install_dir / "src"
        if (self.project_root / "src").exists():
            shutil.copytree(self.project_root / "src", src_dest, dirs_exist_ok=True)
            print("   ✅ Source code copied")
        
        # Copy examples and docs
        for folder in ["examples", "docs"]:
            src_folder = self.project_root / folder
            dest_folder = self.install_dir / folder
            if src_folder.exists():
                shutil.copytree(src_folder, dest_folder, dirs_exist_ok=True)
                print(f"   ✅ {folder} copied")
        
        # Copy key files
        key_files = ["README.md", "LICENSE", ".env.example"]
        for file in key_files:
            src_file = self.project_root / file
            dest_file = self.install_dir / file
            if src_file.exists():
                shutil.copy2(src_file, dest_file)
                print(f"   ✅ {file} copied")
    
    def setup_configuration(self):
        """Create default configuration."""
        print("⚙️  Setting up configuration...")
        
        config = {
            "email": {
                "provider": "gmail",
                "address": "",
                "password": "",
                "imap_server": "imap.gmail.com",
                "imap_port": 993,
                "smtp_server": "smtp.gmail.com",
                "smtp_port": 587
            },
            "agents": {
                "auto_classify": True,
                "auto_organize": True,
                "auto_generate_responses": True,
                "auto_send_responses": False,
                "batch_size": 20
            },
            "ai": {
                "openai_api_key": "",
                "anthropic_api_key": "",
                "default_model": "gpt-3.5-turbo"
            },
            "system": {
                "log_level": "INFO",
                "data_retention_days": 90,
                "backup_enabled": True,
                "monitoring_enabled": True
            }
        }
        
        with open(self.config_file, "w") as f:
            json.dump(config, f, indent=2)
        
        print(f"✅ Configuration created: {self.config_file}")
        
        # Create environment file
        env_file = self.install_dir / ".env"
        env_content = f"""# Email Agent Configuration
EMAIL_ADDRESS=
EMAIL_PASSWORD=
OPENAI_API_KEY=
ANTHROPIC_API_KEY=
DATABASE_URL=sqlite:///{self.install_dir}/data/email_agent.db
LOG_LEVEL=INFO
"""
        
        with open(env_file, "w") as f:
            f.write(env_content)
        
        print("✅ Environment file created")
    
    def create_service(self):
        """Create systemd service file."""
        if os.geteuid() != 0:
            print("⚠️  Skipping service creation (not running as root)")
            return
        
        print("🔧 Creating system service...")
        
        service_content = f"""[Unit]
Description=Email Agent System
After=network.target

[Service]
Type=simple
User=email-agent
WorkingDirectory={self.install_dir}
Environment=PYTHONPATH={self.install_dir}
ExecStart={sys.executable} -m src.main
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
"""
        
        try:
            with open(self.service_file, "w") as f:
                f.write(service_content)
            
            # Reload systemd
            subprocess.run(["systemctl", "daemon-reload"], check=True)
            print("✅ System service created")
            
        except Exception as e:
            print(f"⚠️  Could not create system service: {e}")
    
    def setup_permissions(self):
        """Set up file permissions."""
        print("🔐 Setting up permissions...")
        
        # Make main executable
        main_script = self.install_dir / "src" / "main.py"
        if main_script.exists():
            main_script.chmod(0o755)
        
        # Create user if running as root
        if os.geteuid() == 0:
            try:
                subprocess.run([
                    "useradd", "-r", "-s", "/bin/false", "-d", str(self.install_dir), "email-agent"
                ], check=False)  # Don't fail if user exists
                
                subprocess.run([
                    "chown", "-R", "email-agent:email-agent", str(self.install_dir)
                ], check=True)
                
                print("✅ Permissions configured")
                
            except Exception as e:
                print(f"⚠️  Permission setup warning: {e}")


def main():
    """Main installation function."""
    installer = EmailAgentInstaller()
    
    print("This will install the Email Agent System on your computer.")
    response = input("Continue? (y/N): ").lower().strip()
    
    if response == 'y':
        success = installer.install()
        if success:
            print("\n🎉 Email Agent System installed successfully!")
            print("\n📖 Quick Start:")
            print("1. Edit your email credentials in the config file")
            print("2. Run the activation script to start the agents")
            print("3. Monitor the system through the CLI interface")
        else:
            print("\n❌ Installation failed. Please check the errors above.")
            sys.exit(1)
    else:
        print("Installation cancelled.")


if __name__ == "__main__":
    main()