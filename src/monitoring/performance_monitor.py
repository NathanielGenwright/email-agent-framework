"""
Performance Monitoring System for Email Agents.

This module demonstrates how to monitor agent performance, track metrics,
and identify areas for improvement in agent systems.
"""

import time
import json
import logging
from typing import Dict, List, Any, Optional
from datetime import datetime, timedelta
from dataclasses import dataclass, asdict
from collections import defaultdict, deque

logger = logging.getLogger(__name__)


@dataclass
class PerformanceMetric:
    """Represents a single performance metric measurement."""
    metric_name: str
    value: float
    timestamp: datetime
    agent_name: str
    context: Dict[str, Any]
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "metric_name": self.metric_name,
            "value": self.value,
            "timestamp": self.timestamp.isoformat(),
            "agent_name": self.agent_name,
            "context": self.context
        }


@dataclass
class AgentPerformanceSnapshot:
    """Snapshot of agent performance at a point in time."""
    agent_name: str
    timestamp: datetime
    metrics: Dict[str, float]
    memory_usage: Dict[str, int]
    tool_usage_stats: Dict[str, int]
    error_count: int
    success_rate: float
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "agent_name": self.agent_name,
            "timestamp": self.timestamp.isoformat(),
            "metrics": self.metrics,
            "memory_usage": self.memory_usage,
            "tool_usage_stats": self.tool_usage_stats,
            "error_count": self.error_count,
            "success_rate": self.success_rate
        }


class PerformanceMonitor:
    """
    Comprehensive performance monitoring system for email agents.
    
    Features:
    1. Real-time metric collection
    2. Performance trend analysis
    3. Anomaly detection
    4. Bottleneck identification
    5. Optimization recommendations
    """
    
    def __init__(self, buffer_size: int = 1000):
        self.buffer_size = buffer_size
        
        # Performance data storage
        self.metrics_buffer: deque = deque(maxlen=buffer_size)
        self.snapshots_buffer: deque = deque(maxlen=buffer_size)
        
        # Real-time tracking
        self.active_operations: Dict[str, Dict[str, Any]] = {}
        self.agent_stats: Dict[str, Dict[str, Any]] = defaultdict(lambda: {
            "total_operations": 0,
            "successful_operations": 0,
            "failed_operations": 0,
            "total_execution_time": 0.0,
            "tool_usage": defaultdict(int),
            "error_types": defaultdict(int)
        })
        
        # Performance thresholds for alerting
        self.thresholds = {
            "max_execution_time": 30.0,  # seconds
            "min_success_rate": 0.85,    # 85%
            "max_memory_usage": 100,     # MB
            "max_error_rate": 0.15       # 15%
        }
        
        # Trend analysis windows
        self.trend_windows = {
            "short": timedelta(minutes=5),
            "medium": timedelta(hours=1),
            "long": timedelta(hours=24)
        }
    
    def start_operation(self, operation_id: str, agent_name: str, 
                       operation_type: str, context: Dict[str, Any] = None) -> None:
        """Start tracking a new operation."""
        self.active_operations[operation_id] = {
            "agent_name": agent_name,
            "operation_type": operation_type,
            "start_time": time.time(),
            "context": context or {}
        }
        
        logger.debug(f"Started tracking operation {operation_id} for agent {agent_name}")
    
    def end_operation(self, operation_id: str, success: bool, 
                     result_data: Dict[str, Any] = None, 
                     error_info: str = None) -> None:
        """End tracking an operation and record metrics."""
        if operation_id not in self.active_operations:
            logger.warning(f"Operation {operation_id} not found in active operations")
            return
        
        operation = self.active_operations.pop(operation_id)
        end_time = time.time()
        execution_time = end_time - operation["start_time"]
        
        agent_name = operation["agent_name"]
        operation_type = operation["operation_type"]
        
        # Update agent statistics
        stats = self.agent_stats[agent_name]
        stats["total_operations"] += 1
        stats["total_execution_time"] += execution_time
        
        if success:
            stats["successful_operations"] += 1
        else:
            stats["failed_operations"] += 1
            if error_info:
                stats["error_types"][error_info] += 1
        
        # Record performance metric
        metric = PerformanceMetric(
            metric_name="operation_execution_time",
            value=execution_time,
            timestamp=datetime.now(),
            agent_name=agent_name,
            context={
                "operation_type": operation_type,
                "success": success,
                "result_data": result_data or {},
                "error_info": error_info
            }
        )
        
        self.metrics_buffer.append(metric)
        
        # Check for performance issues
        self._check_performance_thresholds(agent_name, execution_time, success)
        
        logger.debug(f"Completed operation {operation_id}: {execution_time:.2f}s, success={success}")
    
    def record_tool_usage(self, agent_name: str, tool_name: str, 
                         execution_time: float, success: bool) -> None:
        """Record tool usage statistics."""
        stats = self.agent_stats[agent_name]
        stats["tool_usage"][tool_name] += 1
        
        # Record tool-specific metric
        metric = PerformanceMetric(
            metric_name="tool_execution_time",
            value=execution_time,
            timestamp=datetime.now(),
            agent_name=agent_name,
            context={
                "tool_name": tool_name,
                "success": success
            }
        )
        
        self.metrics_buffer.append(metric)
    
    def record_memory_usage(self, agent_name: str, memory_stats: Dict[str, int]) -> None:
        """Record memory usage statistics."""
        total_memory = sum(memory_stats.values())
        
        metric = PerformanceMetric(
            metric_name="memory_usage",
            value=total_memory,
            timestamp=datetime.now(),
            agent_name=agent_name,
            context=memory_stats
        )
        
        self.metrics_buffer.append(metric)
        
        # Check memory threshold
        if total_memory > self.thresholds["max_memory_usage"]:
            logger.warning(f"High memory usage for agent {agent_name}: {total_memory}MB")
    
    def take_performance_snapshot(self, agent_name: str, 
                                additional_metrics: Dict[str, float] = None) -> AgentPerformanceSnapshot:
        """Take a comprehensive performance snapshot of an agent."""
        stats = self.agent_stats[agent_name]
        
        # Calculate success rate
        total_ops = stats["total_operations"]
        success_rate = (stats["successful_operations"] / total_ops) if total_ops > 0 else 1.0
        
        # Calculate average execution time
        avg_execution_time = (stats["total_execution_time"] / total_ops) if total_ops > 0 else 0.0
        
        # Get recent memory usage
        recent_memory = self._get_recent_memory_usage(agent_name)
        
        # Compile metrics
        metrics = {
            "total_operations": total_ops,
            "success_rate": success_rate,
            "average_execution_time": avg_execution_time,
            "operations_per_minute": self._calculate_operations_per_minute(agent_name)
        }
        
        if additional_metrics:
            metrics.update(additional_metrics)
        
        snapshot = AgentPerformanceSnapshot(
            agent_name=agent_name,
            timestamp=datetime.now(),
            metrics=metrics,
            memory_usage=recent_memory,
            tool_usage_stats=dict(stats["tool_usage"]),
            error_count=stats["failed_operations"],
            success_rate=success_rate
        )
        
        self.snapshots_buffer.append(snapshot)
        return snapshot
    
    def get_performance_report(self, agent_name: str = None, 
                             time_window: str = "medium") -> Dict[str, Any]:
        """Generate comprehensive performance report."""
        window_delta = self.trend_windows.get(time_window, self.trend_windows["medium"])
        cutoff_time = datetime.now() - window_delta
        
        # Filter metrics by time window and agent
        relevant_metrics = [
            metric for metric in self.metrics_buffer
            if metric.timestamp >= cutoff_time and 
            (agent_name is None or metric.agent_name == agent_name)
        ]
        
        # Filter snapshots
        relevant_snapshots = [
            snapshot for snapshot in self.snapshots_buffer
            if snapshot.timestamp >= cutoff_time and
            (agent_name is None or snapshot.agent_name == agent_name)
        ]
        
        # Calculate aggregated statistics
        report = {
            "time_window": time_window,
            "report_generated": datetime.now().isoformat(),
            "metrics_analyzed": len(relevant_metrics),
            "snapshots_analyzed": len(relevant_snapshots),
            "agent_performance": self._analyze_agent_performance(relevant_metrics, relevant_snapshots),
            "trends": self._analyze_trends(relevant_metrics),
            "bottlenecks": self._identify_bottlenecks(relevant_metrics),
            "recommendations": self._generate_recommendations(relevant_metrics, relevant_snapshots)
        }
        
        return report
    
    def _check_performance_thresholds(self, agent_name: str, execution_time: float, 
                                    success: bool) -> None:
        """Check if performance thresholds are exceeded."""
        # Check execution time
        if execution_time > self.thresholds["max_execution_time"]:
            logger.warning(f"Slow operation for agent {agent_name}: {execution_time:.2f}s")
        
        # Check success rate
        stats = self.agent_stats[agent_name]
        total_ops = stats["total_operations"]
        if total_ops >= 10:  # Only check after sufficient operations
            success_rate = stats["successful_operations"] / total_ops
            if success_rate < self.thresholds["min_success_rate"]:
                logger.warning(f"Low success rate for agent {agent_name}: {success_rate:.2f}")
    
    def _get_recent_memory_usage(self, agent_name: str) -> Dict[str, int]:
        """Get most recent memory usage for an agent."""
        recent_memory_metrics = [
            metric for metric in reversed(self.metrics_buffer)
            if (metric.agent_name == agent_name and 
                metric.metric_name == "memory_usage")
        ]
        
        if recent_memory_metrics:
            return recent_memory_metrics[0].context
        
        return {"total": 0}
    
    def _calculate_operations_per_minute(self, agent_name: str) -> float:
        """Calculate operations per minute for an agent."""
        now = datetime.now()
        minute_ago = now - timedelta(minutes=1)
        
        recent_operations = [
            metric for metric in self.metrics_buffer
            if (metric.agent_name == agent_name and 
                metric.timestamp >= minute_ago and
                metric.metric_name == "operation_execution_time")
        ]
        
        return len(recent_operations)
    
    def _analyze_agent_performance(self, metrics: List[PerformanceMetric], 
                                 snapshots: List[AgentPerformanceSnapshot]) -> Dict[str, Any]:
        """Analyze overall agent performance."""
        if not metrics and not snapshots:
            return {"status": "no_data"}
        
        # Group metrics by agent
        agent_metrics = defaultdict(list)
        for metric in metrics:
            agent_metrics[metric.agent_name].append(metric)
        
        performance_by_agent = {}
        
        for agent_name, agent_metric_list in agent_metrics.items():
            # Calculate performance statistics
            execution_times = [
                m.value for m in agent_metric_list 
                if m.metric_name == "operation_execution_time"
            ]
            
            if execution_times:
                performance_by_agent[agent_name] = {
                    "total_operations": len(execution_times),
                    "average_execution_time": sum(execution_times) / len(execution_times),
                    "min_execution_time": min(execution_times),
                    "max_execution_time": max(execution_times),
                    "success_rate": len([m for m in agent_metric_list 
                                       if m.context.get("success", False)]) / len(execution_times)
                }
        
        return performance_by_agent
    
    def _analyze_trends(self, metrics: List[PerformanceMetric]) -> Dict[str, Any]:
        """Analyze performance trends over time."""
        if len(metrics) < 10:
            return {"status": "insufficient_data"}
        
        # Sort metrics by timestamp
        sorted_metrics = sorted(metrics, key=lambda m: m.timestamp)
        
        # Split into two halves for trend analysis
        mid_point = len(sorted_metrics) // 2
        first_half = sorted_metrics[:mid_point]
        second_half = sorted_metrics[mid_point:]
        
        # Calculate average execution times
        first_avg = sum(m.value for m in first_half if m.metric_name == "operation_execution_time") / len(first_half)
        second_avg = sum(m.value for m in second_half if m.metric_name == "operation_execution_time") / len(second_half)
        
        trend_direction = "improving" if second_avg < first_avg else "degrading"
        trend_magnitude = abs(second_avg - first_avg) / first_avg if first_avg > 0 else 0
        
        return {
            "execution_time_trend": {
                "direction": trend_direction,
                "magnitude": trend_magnitude,
                "first_period_avg": first_avg,
                "second_period_avg": second_avg
            }
        }
    
    def _identify_bottlenecks(self, metrics: List[PerformanceMetric]) -> List[Dict[str, Any]]:
        """Identify performance bottlenecks."""
        bottlenecks = []
        
        # Group by tool usage
        tool_metrics = defaultdict(list)
        for metric in metrics:
            if metric.metric_name == "tool_execution_time":
                tool_name = metric.context.get("tool_name", "unknown")
                tool_metrics[tool_name].append(metric.value)
        
        # Find slow tools
        for tool_name, execution_times in tool_metrics.items():
            if execution_times:
                avg_time = sum(execution_times) / len(execution_times)
                if avg_time > 5.0:  # Tools taking more than 5 seconds on average
                    bottlenecks.append({
                        "type": "slow_tool",
                        "tool_name": tool_name,
                        "average_execution_time": avg_time,
                        "usage_count": len(execution_times)
                    })
        
        return bottlenecks
    
    def _generate_recommendations(self, metrics: List[PerformanceMetric], 
                                snapshots: List[AgentPerformanceSnapshot]) -> List[str]:
        """Generate optimization recommendations."""
        recommendations = []
        
        if not metrics:
            return ["Insufficient data for recommendations"]
        
        # Analyze execution times
        execution_times = [m.value for m in metrics if m.metric_name == "operation_execution_time"]
        if execution_times:
            avg_time = sum(execution_times) / len(execution_times)
            if avg_time > 10.0:
                recommendations.append("Consider optimizing slow operations or implementing caching")
        
        # Analyze tool usage
        tool_usage = defaultdict(int)
        for metric in metrics:
            if metric.metric_name == "tool_execution_time":
                tool_name = metric.context.get("tool_name", "unknown")
                tool_usage[tool_name] += 1
        
        if tool_usage:
            most_used_tool = max(tool_usage, key=tool_usage.get)
            recommendations.append(f"Most used tool is '{most_used_tool}' - consider optimizing it")
        
        # Analyze error patterns
        error_count = len([m for m in metrics if not m.context.get("success", True)])
        if error_count > len(metrics) * 0.1:  # More than 10% errors
            recommendations.append("High error rate detected - review error handling and robustness")
        
        return recommendations or ["Performance is within acceptable ranges"]
    
    def get_real_time_stats(self) -> Dict[str, Any]:
        """Get real-time performance statistics."""
        return {
            "active_operations": len(self.active_operations),
            "total_metrics_collected": len(self.metrics_buffer),
            "agents_monitored": len(self.agent_stats),
            "recent_operations": {
                agent: stats["total_operations"] 
                for agent, stats in self.agent_stats.items()
            }
        }


# Global performance monitor instance
performance_monitor = PerformanceMonitor()