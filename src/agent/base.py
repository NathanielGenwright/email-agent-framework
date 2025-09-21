"""Base agent class that demonstrates the core agent concepts."""

import json
import logging
from abc import ABC, abstractmethod
from typing import Any, Dict, List, Optional, Callable
from datetime import datetime
from pydantic import BaseModel

logger = logging.getLogger(__name__)


class ToolResult(BaseModel):
    """Result from a tool execution."""
    success: bool
    result: Any
    error: Optional[str] = None
    metadata: Dict[str, Any] = {}


class Tool(BaseModel):
    """Represents a tool that an agent can use."""
    name: str
    description: str
    function: Callable
    parameters: Dict[str, Any] = {}


class AgentMemory:
    """Simple memory system for agents."""
    
    def __init__(self):
        self.short_term: List[Dict] = []
        self.long_term: Dict[str, Any] = {}
        self.context: Dict[str, Any] = {}
    
    def add_to_short_term(self, event: Dict):
        """Add event to short-term memory."""
        event["timestamp"] = datetime.now().isoformat()
        self.short_term.append(event)
        
        # Keep only last 100 events
        if len(self.short_term) > 100:
            self.short_term = self.short_term[-100:]
    
    def store_long_term(self, key: str, value: Any):
        """Store information in long-term memory."""
        self.long_term[key] = value
    
    def get_context(self, key: str) -> Any:
        """Get context information."""
        return self.context.get(key)
    
    def set_context(self, key: str, value: Any):
        """Set context information."""
        self.context[key] = value


class BaseAgent(ABC):
    """
    Base agent class that demonstrates core agent concepts.
    
    Agents follow the perceive-think-act loop:
    1. Perceive: Gather information from environment
    2. Think: Reason about the information and plan actions
    3. Act: Execute actions using available tools
    """
    
    def __init__(self, name: str, description: str):
        self.name = name
        self.description = description
        self.tools: Dict[str, Tool] = {}
        self.memory = AgentMemory()
        self.is_active = False
        
    def register_tool(self, tool: Tool):
        """Register a tool that this agent can use."""
        self.tools[tool.name] = tool
        logger.info(f"Agent {self.name} registered tool: {tool.name}")
    
    def get_available_tools(self) -> List[str]:
        """Get list of available tool names."""
        return list(self.tools.keys())
    
    def use_tool(self, tool_name: str, **kwargs) -> ToolResult:
        """Execute a tool with given parameters."""
        if tool_name not in self.tools:
            return ToolResult(
                success=False,
                result=None,
                error=f"Tool '{tool_name}' not found"
            )
        
        tool = self.tools[tool_name]
        
        try:
            logger.info(f"Agent {self.name} using tool: {tool_name}")
            result = tool.function(**kwargs)
            
            # Record tool usage in memory
            self.memory.add_to_short_term({
                "type": "tool_usage",
                "tool": tool_name,
                "parameters": kwargs,
                "success": True,
                "result": str(result)[:200]  # Truncate for memory
            })
            
            return ToolResult(
                success=True,
                result=result,
                metadata={"tool": tool_name, "agent": self.name}
            )
            
        except Exception as e:
            error_msg = str(e)
            logger.error(f"Tool {tool_name} failed: {error_msg}")
            
            self.memory.add_to_short_term({
                "type": "tool_error",
                "tool": tool_name,
                "parameters": kwargs,
                "error": error_msg
            })
            
            return ToolResult(
                success=False,
                result=None,
                error=error_msg
            )
    
    @abstractmethod
    def perceive(self) -> Dict[str, Any]:
        """
        Perceive: Gather information from the environment.
        Each agent implements this based on their domain.
        """
        pass
    
    @abstractmethod
    def think(self, perception: Dict[str, Any]) -> List[Dict[str, Any]]:
        """
        Think: Reason about the perception and plan actions.
        Returns a list of planned actions.
        """
        pass
    
    @abstractmethod
    def act(self, actions: List[Dict[str, Any]]) -> List[ToolResult]:
        """
        Act: Execute the planned actions using available tools.
        Returns results of all actions.
        """
        pass
    
    def run_cycle(self) -> Dict[str, Any]:
        """
        Execute one complete perceive-think-act cycle.
        This is the core agent loop.
        """
        try:
            logger.info(f"Agent {self.name} starting cycle")
            
            # 1. Perceive
            perception = self.perceive()
            self.memory.add_to_short_term({
                "type": "perception",
                "data": perception
            })
            
            # 2. Think
            planned_actions = self.think(perception)
            self.memory.add_to_short_term({
                "type": "planning",
                "actions": planned_actions
            })
            
            # 3. Act
            results = self.act(planned_actions)
            
            cycle_result = {
                "agent": self.name,
                "timestamp": datetime.now().isoformat(),
                "perception": perception,
                "planned_actions": planned_actions,
                "results": [r.dict() for r in results],
                "success": all(r.success for r in results)
            }
            
            logger.info(f"Agent {self.name} completed cycle")
            return cycle_result
            
        except Exception as e:
            error_msg = f"Agent {self.name} cycle failed: {str(e)}"
            logger.error(error_msg)
            return {
                "agent": self.name,
                "timestamp": datetime.now().isoformat(),
                "error": error_msg,
                "success": False
            }
    
    def get_status(self) -> Dict[str, Any]:
        """Get current agent status and memory summary."""
        return {
            "name": self.name,
            "description": self.description,
            "is_active": self.is_active,
            "available_tools": self.get_available_tools(),
            "memory_summary": {
                "short_term_events": len(self.memory.short_term),
                "long_term_keys": list(self.memory.long_term.keys()),
                "context_keys": list(self.memory.context.keys())
            }
        }