# 🚀 Email Agent System - Deployment Guide

## Complete Installation and Activation System

Your email agent system now includes a complete installation and activation framework for production deployment with real email inboxes.

## 📦 Installation Process

### 1. Install the System
```bash
# Make the installer executable
chmod +x email-agent

# Run the installer
python3 install.py
# OR
./email-agent install
```

**What this does:**
- ✅ Creates installation directory (`~/.email-agent`)
- ✅ Installs all dependencies
- ✅ Copies source code and documentation
- ✅ Creates default configuration files
- ✅ Sets up logging and data directories
- ✅ Creates system service (if run as root)

### 2. Configure Email Access
```bash
# Edit the configuration file
nano ~/.email-agent/config.json

# Or edit the environment file
nano ~/.email-agent/.env
```

**Required Settings:**
```json
{
  "email": {
    "address": "your.email@gmail.com",
    "password": "your-app-password",
    "provider": "gmail"
  },
  "ai": {
    "openai_api_key": "your-openai-key",
    "anthropic_api_key": "your-anthropic-key"
  }
}
```

### 3. Activate the System
```bash
# Start the email agents
python3 activate.py start
# OR
./email-agent activate
```

## 🎮 System Management

### Basic Commands
```bash
./email-agent status      # Check system status
./email-agent start       # Start the agents
./email-agent stop        # Stop the agents  
./email-agent restart     # Restart the agents
./email-agent logs        # View recent logs
./email-agent interactive # Interactive CLI mode
```

### Advanced Management
```bash
# View specific number of log lines
./email-agent logs 100

# Run demonstrations
./email-agent demo

# Get help
./email-agent help
```

## ⚙️ Configuration Options

### Email Provider Setup

**Gmail Configuration:**
```json
{
  "email": {
    "provider": "gmail",
    "address": "your.email@gmail.com", 
    "password": "your-16-char-app-password",
    "imap_server": "imap.gmail.com",
    "imap_port": 993
  }
}
```

**Outlook Configuration:**
```json
{
  "email": {
    "provider": "outlook",
    "address": "your.email@outlook.com",
    "password": "your-password",
    "imap_server": "outlook.office365.com", 
    "imap_port": 993
  }
}
```

### Agent Behavior Settings
```json
{
  "agents": {
    "auto_classify": true,        # Automatically classify emails
    "auto_organize": true,        # Automatically organize inbox
    "auto_generate_responses": true,  # Generate response suggestions
    "auto_send_responses": false, # Require approval before sending
    "batch_size": 20             # Process emails in batches
  }
}
```

### AI Integration
```json
{
  "ai": {
    "openai_api_key": "sk-...",
    "anthropic_api_key": "sk-ant-...",
    "default_model": "gpt-3.5-turbo"
  }
}
```

## 🔐 Gmail Setup Instructions

### 1. Enable 2-Factor Authentication
1. Go to your Google Account settings
2. Security → 2-Step Verification
3. Turn on 2-Step Verification

### 2. Generate App Password
1. Google Account → Security → 2-Step Verification
2. Scroll to "App passwords"
3. Select app: "Mail"
4. Select device: "Other (custom name)"
5. Enter: "Email Agent System"
6. Copy the 16-character password

### 3. Configure IMAP Access
1. Gmail Settings → Forwarding and POP/IMAP
2. Enable IMAP access
3. Save changes

## 📊 System Monitoring

### Status Dashboard
```bash
./email-agent status
```

**Example Output:**
```
📊 Email Agent System Status
========================================
✅ Installation: Found
   Location: /Users/username/.email-agent
✅ Configuration: Found
   Email configured: ✅
   AI configured: ✅
✅ Status: Running
   PID: 12345
✅ Logs: Available
   Location: /Users/username/.email-agent/logs/email-agent.log
   Size: 2048 bytes
```

### Log Monitoring
```bash
# View recent logs
./email-agent logs

# View more log lines
./email-agent logs 200

# Follow logs in real-time
tail -f ~/.email-agent/logs/email-agent.log
```

## 🤖 Agent Capabilities

### EmailClassifier Agent
- **Categorizes emails**: urgent, work, personal, newsletters
- **Calculates priority**: 1-10 scale based on content
- **Extracts action items**: tasks and deadlines
- **Analyzes sentiment**: positive, negative, neutral

### EmailResponder Agent  
- **Generates responses**: AI-powered contextual replies
- **Analyzes intent**: meeting requests, information requests
- **Manages templates**: common response patterns
- **Requires approval**: all responses reviewed before sending

### InboxOrganizer Agent
- **Applies labels**: smart categorization
- **Creates folders**: organized structure
- **Archives emails**: based on age and type
- **Detects duplicates**: cleanup recommendations

### EmailMasterAgent
- **Coordinates agents**: parallel processing
- **Manages workflow**: end-to-end automation
- **Monitors performance**: tracks metrics
- **Learns preferences**: adapts to user feedback

## 🔧 Troubleshooting

### Common Issues

**"Permission denied" errors:**
```bash
# Fix file permissions
chmod +x email-agent
chmod +x install.py
chmod +x activate.py
```

**"Module not found" errors:**
```bash
# Install dependencies
pip3 install -r requirements.txt
```

**"Authentication failed" errors:**
- Verify email credentials
- Use app-specific password for Gmail
- Check IMAP is enabled

**"Cannot connect to email server":**
- Check internet connection
- Verify server settings
- Check firewall settings

### Reset Installation
```bash
# Stop agents
./email-agent stop

# Remove installation
rm -rf ~/.email-agent

# Reinstall
./email-agent install
```

## 🚀 Production Deployment

### System Service (Linux)
If installed as root, the system creates a systemd service:

```bash
# Enable service to start on boot
sudo systemctl enable email-agent

# Start service
sudo systemctl start email-agent

# Check service status
sudo systemctl status email-agent
```

### Docker Deployment
```dockerfile
FROM python:3.11-slim

WORKDIR /app
COPY . .

RUN pip install -r requirements.txt
RUN python install.py

CMD ["python", "activate.py", "start"]
```

### Cloud Deployment
The system can be deployed on:
- **AWS EC2**: Use the systemd service
- **Google Cloud**: Container or Compute Engine
- **Azure**: Virtual Machine or Container Instance
- **DigitalOcean**: Droplet with systemd

## 📈 Performance Optimization

### Configuration Tuning
```json
{
  "agents": {
    "batch_size": 50,           # Larger batches for high volume
    "parallel_processing": true  # Enable parallel agents
  },
  "system": {
    "data_retention_days": 30,  # Reduce for storage
    "backup_enabled": false     # Disable for performance
  }
}
```

### Resource Monitoring
```bash
# Check system resources
htop

# Monitor email agent process
ps aux | grep email-agent

# Check disk usage
du -sh ~/.email-agent
```

## 🎯 Success Metrics

**Your system is working when you see:**
- ✅ Email classification running automatically
- ✅ Response suggestions generated for new emails
- ✅ Inbox organization happening in background
- ✅ Learning from your feedback and preferences
- ✅ Logs showing successful agent cycles

**Ready for Production Email Management! 🚀📧**