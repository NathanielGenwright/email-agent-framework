# Email Agent System

A comprehensive AI-powered email management system built to demonstrate agent concepts, multi-agent orchestration, and machine learning integration.

## 🎯 Project Overview

This project creates an intelligent email management agent that:
- **Classifies emails** automatically using pattern recognition
- **Generates responses** using AI/LLM integration  
- **Organizes inbox** with smart rules and automation
- **Learns from feedback** to improve over time
- **Coordinates multiple sub-agents** for complex workflows

## 🧠 Understanding Agents vs Bots

### Bots
- React to specific commands or triggers
- Follow predetermined scripts/decision trees
- Limited adaptability and context understanding
- Example: Simple chatbot with predefined responses

### Agents
- Autonomous systems that can plan, reason, and take actions
- Goal-oriented with ability to break down complex tasks
- Use tools, make decisions, and adapt strategies
- Maintain context and state across interactions
- Example: This email management system

## 🏗️ Agent Architecture

### Core Agent Framework

Every agent follows the **Perceive-Think-Act** loop:

1. **Perceive**: Gather information from environment (emails, APIs, databases)
2. **Think**: Analyze data, plan actions, make decisions  
3. **Act**: Execute tasks using available tools

```python
class BaseAgent:
    def perceive(self) -> Dict[str, Any]:
        # Gather environmental information
    
    def think(self, perception: Dict[str, Any]) -> List[Dict[str, Any]]:
        # Reason about perception and plan actions
    
    def act(self, actions: List[Dict[str, Any]]) -> List[ToolResult]:
        # Execute planned actions using tools
```

### Multi-Agent System

```
EmailMasterAgent (Orchestrator)
├── EmailClassifier (Specialist)
│   ├── Categorizes emails by type
│   ├── Calculates priority scores
│   └── Extracts action items
├── EmailResponder (Specialist)  
│   ├── Analyzes email intent
│   ├── Generates AI responses
│   └── Manages response templates
└── InboxOrganizer (Specialist)
    ├── Applies smart labels
    ├── Creates folder structure
    └── Archives old emails
```

## 🚀 Quick Start

### 1. One-Command Installation

```bash
# Clone the repository
git clone https://github.com/NathanielGenwright/email-agent-framework.git
cd email-agent-framework

# Install everything with one command
./quick-start.sh
```

### 2. Configure Email Access

```bash
# Edit configuration with your email credentials
nano ~/.email-agent/.env

# Add your settings:
# EMAIL_ADDRESS=your.email@gmail.com
# EMAIL_PASSWORD=your-app-password
# OPENAI_API_KEY=your-api-key (optional)
```

### 3. Activate the Agents

```bash
# Start the email agent system
./email-agent activate

# Check system status
./email-agent status

# View live activity
./email-agent logs
```

### 4. Manage the System

```bash
./email-agent start       # Start agents
./email-agent stop        # Stop agents  
./email-agent restart     # Restart system
./email-agent interactive # Interactive mode
./email-agent demo        # Run demonstrations
```

## 🛠️ Agent Components

### 1. Email Classification Agent

**Purpose**: Automatically categorize and prioritize emails

**Capabilities**:
- Pattern-based classification (urgent, work, personal, etc.)
- Priority scoring (0-10 scale)
- Sentiment analysis
- Action item extraction

**Example Usage**:
```python
classifier = EmailClassifier()
result = classifier.run_cycle()
summary = classifier.get_classification_summary()
```

### 2. Email Response Agent

**Purpose**: Generate contextually appropriate email responses

**Capabilities**:
- Intent analysis (meeting request, information request, etc.)
- AI-powered response generation
- Template management
- Response prioritization

**Example Usage**:
```python
responder = EmailResponder()
pending_responses = responder.get_pending_responses()
responder.send_response(email_id, approved=True)
```

### 3. Inbox Organization Agent

**Purpose**: Maintain organized email structure

**Capabilities**:
- Smart label application
- Folder structure creation
- Archive management
- Duplicate detection

**Example Usage**:
```python
organizer = InboxOrganizer()
organizer.run_cycle()
report = organizer.get_organization_report()
```

### 4. Master Orchestration Agent

**Purpose**: Coordinate all sub-agents and manage workflows

**Capabilities**:
- Multi-agent coordination
- Workflow orchestration
- Performance monitoring
- Learning integration

**Example Usage**:
```python
master_agent = EmailMasterAgent()
result = master_agent.run_cycle()
status = master_agent.get_comprehensive_status()
```

## 🧠 Learning and Memory System

### Persistent Memory

The system includes a sophisticated memory system that:
- Stores user interactions and feedback
- Learns preferences over time
- Adapts agent behavior based on patterns
- Maintains context across sessions

### User Feedback Integration

```python
# Provide feedback to improve classification
master_agent.process_user_feedback(
    email_id="123",
    feedback_type="classification_correction", 
    feedback_data={"correct_category": "work"}
)

# Approve/reject response suggestions
master_agent.process_user_feedback(
    email_id="456",
    feedback_type="response_approval",
    feedback_data={"approved": True}
)
```

### Learning Examples

The system learns:
- **Sender patterns**: "Emails from john@company.com are usually urgent"
- **Keyword associations**: "Meeting + tomorrow = high priority"
- **Response preferences**: "User prefers formal tone for client emails"
- **Organization rules**: "Newsletters should auto-archive after 7 days"

## 📊 Performance Monitoring

### Real-time Metrics

```python
from monitoring.performance_monitor import performance_monitor

# Track operation performance
performance_monitor.start_operation("classify_batch", "EmailClassifier", "classification")
# ... do work ...
performance_monitor.end_operation("classify_batch", success=True)

# Get performance report
report = performance_monitor.get_performance_report(time_window="medium")
```

### Key Performance Indicators

- **Classification Accuracy**: How often classifications are correct
- **Response Approval Rate**: Percentage of generated responses approved by user
- **Organization Effectiveness**: How well organization actions are maintained
- **Execution Speed**: Average time for agent operations
- **Memory Efficiency**: Agent memory usage patterns

## 🔧 Building Your Own Agents

### 1. Define Agent Purpose

```python
class MyCustomAgent(BaseAgent):
    def __init__(self):
        super().__init__(
            name="MyAgent",
            description="Specialized agent for custom task"
        )
        self._register_tools()
```

### 2. Implement Tools

```python
def _register_tools(self):
    def my_custom_tool(input_data):
        # Tool implementation
        return processed_result
    
    self.register_tool(Tool(
        name="my_tool",
        description="Does something specific",
        function=my_custom_tool
    ))
```

### 3. Implement Agent Logic

```python
def perceive(self) -> Dict[str, Any]:
    # Gather relevant environmental data
    return {"data": collected_information}

def think(self, perception: Dict[str, Any]) -> List[Dict[str, Any]]:
    # Plan actions based on perception
    return [{"type": "action", "params": {}}]

def act(self, actions: List[Dict[str, Any]]) -> List[ToolResult]:
    # Execute planned actions
    results = []
    for action in actions:
        result = self.use_tool(action["type"], **action["params"])
        results.append(result)
    return results
```

## 🚀 Production Deployment

### System Requirements
- **Python 3.8+** (tested on 3.9-3.11)
- **Email Access** (Gmail, Outlook, or IMAP)
- **2GB RAM** minimum, 4GB recommended
- **Linux/macOS/Windows** support

### Gmail Setup (Recommended)
1. **Enable 2FA** in Google Account settings
2. **Generate App Password**: Google Account → Security → App passwords
3. **Use App Password** in configuration (not your regular password)

### Production Installation
```bash
# For production deployment
sudo python3 install.py    # Install as system service
./email-agent activate     # Start agents
./email-agent status       # Verify running

# For development
./quick-start.sh           # User installation
```

### Monitoring & Maintenance
```bash
./email-agent status       # System health check
./email-agent logs 100     # View recent activity  
./email-agent restart      # Restart if needed
```

## 💼 Monetization Strategies

### 1. SaaS Platform ✅
- **Ready**: Complete multi-tenant architecture
- **Market**: Email management service ($10-50/month)
- **Features**: AI classification, auto-responses, learning

### 2. Custom Agent Development ✅  
- **Ready**: Reusable framework and patterns
- **Market**: Enterprise automation consulting
- **Value**: $5k-50k per custom implementation

### 3. Training and Education ✅
- **Ready**: Complete curriculum and examples
- **Market**: Developer education and certification
- **Value**: $500-2000 per course/workshop

### 4. Agent Marketplace ✅
- **Ready**: Modular components and templates
- **Market**: Developer tools and templates
- **Value**: $50-500 per template/tool

## 🔍 Advanced Features

### Multi-Agent Coordination

```python
# Parallel processing
with ThreadPoolExecutor(max_workers=3) as executor:
    classification_future = executor.submit(classifier.run_cycle)
    response_future = executor.submit(responder.run_cycle)
    organization_future = executor.submit(organizer.run_cycle)
    
    # Collect results
    results = [future.result() for future in as_completed([...])]
```

### AI Integration

```python
# OpenAI integration for response generation
client = OpenAI(api_key=settings.openai_api_key)
response = client.chat.completions.create(
    model="gpt-3.5-turbo",
    messages=[
        {"role": "system", "content": "You are an email assistant..."},
        {"role": "user", "content": f"Generate response for: {email.body}"}
    ]
)
```

### Learning and Adaptation

```python
# Pattern learning from user feedback
def learn_from_feedback(self, event_id: str, feedback_type: str, feedback_value: Any):
    # Extract patterns from feedback
    # Update agent behavior
    # Store learned preferences
```

## 🧪 Testing and Development

### Running Tests

```bash
# Run all tests
pytest tests/

# Run with coverage
pytest --cov=src tests/

# Run specific test category
pytest tests/test_agents.py -v
```

### Development Mode

```bash
# Enable verbose logging
python -m src.cli --verbose process

# Dry run mode (no actual changes)
python -m src.cli process --dry-run

# Interactive debugging
python -m src.cli interactive
```

## 📚 Learning Resources

### Understanding Agents
1. Read through `src/agent/base.py` for core concepts
2. Study `src/agent/email_classifier.py` for specialization patterns
3. Examine `src/agent/email_master_agent.py` for orchestration

### Memory and Learning
1. Explore `src/memory/persistent_memory.py` for learning mechanisms
2. Understand feedback processing and preference storage
3. Study pattern recognition and adaptation algorithms

### Performance Optimization
1. Review `src/monitoring/performance_monitor.py` 
2. Learn about metrics collection and analysis
3. Understand bottleneck identification

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Implement your agent or improvement
4. Add comprehensive tests
5. Update documentation
6. Submit a pull request

## 📄 License

MIT License - see LICENSE file for details.

## 🆘 Support

- Create issues for bugs or feature requests
- Join discussions for architecture questions
- Contribute examples and use cases

---

**Built with ❤️ to demonstrate the power of intelligent agent systems**