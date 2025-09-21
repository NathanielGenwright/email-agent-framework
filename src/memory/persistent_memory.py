"""
Persistent Memory System - demonstrates agent learning and adaptation.

This system shows how agents can learn from user feedback and improve over time.
It implements both short-term context and long-term learning storage.
"""

import json
import sqlite3
import logging
from typing import Any, Dict, List, Optional, Tuple
from datetime import datetime, timedelta
from dataclasses import dataclass, asdict
from pathlib import Path

logger = logging.getLogger(__name__)


@dataclass
class MemoryEvent:
    """Represents a single memory event."""
    id: str
    timestamp: datetime
    event_type: str
    data: Dict[str, Any]
    importance: float  # 0.0 - 1.0
    tags: List[str]
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "id": self.id,
            "timestamp": self.timestamp.isoformat(),
            "event_type": self.event_type,
            "data": self.data,
            "importance": self.importance,
            "tags": self.tags
        }


@dataclass
class UserPreference:
    """Represents a learned user preference."""
    category: str
    preference_key: str
    preference_value: Any
    confidence: float  # 0.0 - 1.0
    learned_from: List[str]  # Event IDs that contributed to this preference
    last_updated: datetime
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "category": self.category,
            "preference_key": self.preference_key,
            "preference_value": self.preference_value,
            "confidence": self.confidence,
            "learned_from": self.learned_from,
            "last_updated": self.last_updated.isoformat()
        }


class PersistentMemory:
    """
    Advanced memory system that demonstrates agent learning capabilities.
    
    Features:
    1. Persistent storage across sessions
    2. User preference learning
    3. Pattern recognition
    4. Importance-based retention
    5. Context-aware retrieval
    """
    
    def __init__(self, db_path: str = "email_agent_memory.db"):
        self.db_path = db_path
        self.connection = None
        self._initialize_database()
        
        # In-memory caches for performance
        self.recent_events: List[MemoryEvent] = []
        self.user_preferences: Dict[str, UserPreference] = {}
        self.pattern_cache: Dict[str, Any] = {}
        
        self._load_recent_data()
    
    def _initialize_database(self):
        """Initialize SQLite database with required tables."""
        self.connection = sqlite3.connect(self.db_path)
        cursor = self.connection.cursor()
        
        # Events table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS memory_events (
                id TEXT PRIMARY KEY,
                timestamp DATETIME,
                event_type TEXT,
                data TEXT,
                importance REAL,
                tags TEXT
            )
        """)
        
        # User preferences table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS user_preferences (
                category TEXT,
                preference_key TEXT,
                preference_value TEXT,
                confidence REAL,
                learned_from TEXT,
                last_updated DATETIME,
                PRIMARY KEY (category, preference_key)
            )
        """)
        
        # Patterns table for learned behaviors
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS learned_patterns (
                pattern_id TEXT PRIMARY KEY,
                pattern_type TEXT,
                pattern_data TEXT,
                confidence REAL,
                usage_count INTEGER,
                last_used DATETIME
            )
        """)
        
        # Feedback table for learning
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS user_feedback (
                feedback_id TEXT PRIMARY KEY,
                event_id TEXT,
                feedback_type TEXT,
                feedback_value TEXT,
                timestamp DATETIME
            )
        """)
        
        self.connection.commit()
        logger.info("Memory database initialized")
    
    def _load_recent_data(self):
        """Load recent data into memory for quick access."""
        cursor = self.connection.cursor()
        
        # Load recent events (last 7 days)
        week_ago = datetime.now() - timedelta(days=7)
        cursor.execute("""
            SELECT id, timestamp, event_type, data, importance, tags
            FROM memory_events
            WHERE timestamp > ?
            ORDER BY timestamp DESC
            LIMIT 1000
        """, (week_ago.isoformat(),))
        
        for row in cursor.fetchall():
            event = MemoryEvent(
                id=row[0],
                timestamp=datetime.fromisoformat(row[1]),
                event_type=row[2],
                data=json.loads(row[3]),
                importance=row[4],
                tags=json.loads(row[5])
            )
            self.recent_events.append(event)
        
        # Load user preferences
        cursor.execute("""
            SELECT category, preference_key, preference_value, 
                   confidence, learned_from, last_updated
            FROM user_preferences
        """)
        
        for row in cursor.fetchall():
            pref = UserPreference(
                category=row[0],
                preference_key=row[1],
                preference_value=json.loads(row[2]),
                confidence=row[3],
                learned_from=json.loads(row[4]),
                last_updated=datetime.fromisoformat(row[5])
            )
            key = f"{pref.category}.{pref.preference_key}"
            self.user_preferences[key] = pref
        
        logger.info(f"Loaded {len(self.recent_events)} recent events and {len(self.user_preferences)} preferences")
    
    def add_event(self, event_type: str, data: Dict[str, Any], 
                  importance: float = 0.5, tags: List[str] = None) -> str:
        """Add a new memory event."""
        event_id = f"{event_type}_{datetime.now().strftime('%Y%m%d_%H%M%S_%f')}"
        timestamp = datetime.now()
        tags = tags or []
        
        event = MemoryEvent(
            id=event_id,
            timestamp=timestamp,
            event_type=event_type,
            data=data,
            importance=importance,
            tags=tags
        )
        
        # Add to in-memory cache
        self.recent_events.append(event)
        
        # Keep only recent events in memory
        if len(self.recent_events) > 1000:
            self.recent_events = self.recent_events[-1000:]
        
        # Store in database
        cursor = self.connection.cursor()
        cursor.execute("""
            INSERT INTO memory_events (id, timestamp, event_type, data, importance, tags)
            VALUES (?, ?, ?, ?, ?, ?)
        """, (
            event_id,
            timestamp.isoformat(),
            event_type,
            json.dumps(data),
            importance,
            json.dumps(tags)
        ))
        self.connection.commit()
        
        logger.debug(f"Added memory event: {event_type}")
        return event_id
    
    def add_user_feedback(self, event_id: str, feedback_type: str, 
                         feedback_value: Any) -> None:
        """Record user feedback for learning."""
        feedback_id = f"feedback_{datetime.now().strftime('%Y%m%d_%H%M%S_%f')}"
        
        cursor = self.connection.cursor()
        cursor.execute("""
            INSERT INTO user_feedback (feedback_id, event_id, feedback_type, 
                                     feedback_value, timestamp)
            VALUES (?, ?, ?, ?, ?)
        """, (
            feedback_id,
            event_id,
            feedback_type,
            json.dumps(feedback_value),
            datetime.now().isoformat()
        ))
        self.connection.commit()
        
        # Trigger learning from feedback
        self._learn_from_feedback(event_id, feedback_type, feedback_value)
        
        logger.info(f"Recorded user feedback: {feedback_type} for event {event_id}")
    
    def _learn_from_feedback(self, event_id: str, feedback_type: str, 
                           feedback_value: Any) -> None:
        """Learn and update preferences based on user feedback."""
        # Find the original event
        event = self.get_event(event_id)
        if not event:
            return
        
        # Extract learning patterns based on feedback type
        if feedback_type == "classification_correction":
            # User corrected email classification
            self._update_classification_preference(event, feedback_value)
        
        elif feedback_type == "response_approval":
            # User approved/rejected generated response
            self._update_response_preference(event, feedback_value)
        
        elif feedback_type == "organization_preference":
            # User changed organization behavior
            self._update_organization_preference(event, feedback_value)
        
        elif feedback_type == "priority_adjustment":
            # User changed priority assessment
            self._update_priority_preference(event, feedback_value)
    
    def _update_classification_preference(self, event: MemoryEvent, 
                                        correction: Dict[str, Any]) -> None:
        """Learn from email classification corrections."""
        original_classification = event.data.get("classification_result")
        corrected_classification = correction.get("correct_category")
        
        if original_classification and corrected_classification:
            # Learn sender-based preferences
            sender = event.data.get("email_sender", "")
            if sender:
                self._update_preference(
                    category="classification",
                    preference_key=f"sender_category_{sender}",
                    preference_value=corrected_classification,
                    event_id=event.id,
                    confidence_boost=0.3
                )
            
            # Learn keyword-based preferences
            keywords = event.data.get("email_keywords", [])
            for keyword in keywords:
                self._update_preference(
                    category="classification",
                    preference_key=f"keyword_category_{keyword}",
                    preference_value=corrected_classification,
                    event_id=event.id,
                    confidence_boost=0.2
                )
    
    def _update_response_preference(self, event: MemoryEvent, 
                                  approval: Dict[str, Any]) -> None:
        """Learn from response approval/rejection."""
        approved = approval.get("approved", False)
        response_style = event.data.get("response_style", "")
        intent = event.data.get("intent", "")
        
        if intent and response_style:
            preference_value = {"style": response_style, "approved": approved}
            self._update_preference(
                category="response",
                preference_key=f"intent_style_{intent}",
                preference_value=preference_value,
                event_id=event.id,
                confidence_boost=0.4 if approved else -0.2
            )
    
    def _update_organization_preference(self, event: MemoryEvent, 
                                      preference: Dict[str, Any]) -> None:
        """Learn from organization behavior preferences."""
        org_action = preference.get("action")
        sender = event.data.get("email_sender", "")
        
        if org_action and sender:
            self._update_preference(
                category="organization",
                preference_key=f"sender_action_{sender}",
                preference_value=org_action,
                event_id=event.id,
                confidence_boost=0.3
            )
    
    def _update_priority_preference(self, event: MemoryEvent, 
                                  priority_adjustment: Dict[str, Any]) -> None:
        """Learn from priority adjustments."""
        original_priority = event.data.get("calculated_priority", 0)
        adjusted_priority = priority_adjustment.get("correct_priority", 0)
        
        # Learn sender priority patterns
        sender = event.data.get("email_sender", "")
        if sender and abs(original_priority - adjusted_priority) > 1:
            self._update_preference(
                category="priority",
                preference_key=f"sender_priority_{sender}",
                preference_value=adjusted_priority,
                event_id=event.id,
                confidence_boost=0.4
            )
    
    def _update_preference(self, category: str, preference_key: str, 
                          preference_value: Any, event_id: str, 
                          confidence_boost: float = 0.1) -> None:
        """Update or create a user preference."""
        full_key = f"{category}.{preference_key}"
        
        if full_key in self.user_preferences:
            # Update existing preference
            pref = self.user_preferences[full_key]
            pref.preference_value = preference_value
            pref.confidence = min(1.0, pref.confidence + confidence_boost)
            pref.learned_from.append(event_id)
            pref.last_updated = datetime.now()
        else:
            # Create new preference
            pref = UserPreference(
                category=category,
                preference_key=preference_key,
                preference_value=preference_value,
                confidence=max(0.0, 0.5 + confidence_boost),
                learned_from=[event_id],
                last_updated=datetime.now()
            )
            self.user_preferences[full_key] = pref
        
        # Save to database
        cursor = self.connection.cursor()
        cursor.execute("""
            INSERT OR REPLACE INTO user_preferences 
            (category, preference_key, preference_value, confidence, 
             learned_from, last_updated)
            VALUES (?, ?, ?, ?, ?, ?)
        """, (
            category,
            preference_key,
            json.dumps(preference_value),
            pref.confidence,
            json.dumps(pref.learned_from),
            pref.last_updated.isoformat()
        ))
        self.connection.commit()
        
        logger.info(f"Updated preference: {full_key} (confidence: {pref.confidence:.2f})")
    
    def get_preference(self, category: str, preference_key: str, 
                      default: Any = None) -> Tuple[Any, float]:
        """Get a user preference with confidence level."""
        full_key = f"{category}.{preference_key}"
        
        if full_key in self.user_preferences:
            pref = self.user_preferences[full_key]
            return pref.preference_value, pref.confidence
        
        return default, 0.0
    
    def get_event(self, event_id: str) -> Optional[MemoryEvent]:
        """Retrieve a specific event by ID."""
        # Check in-memory cache first
        for event in self.recent_events:
            if event.id == event_id:
                return event
        
        # Query database
        cursor = self.connection.cursor()
        cursor.execute("""
            SELECT id, timestamp, event_type, data, importance, tags
            FROM memory_events
            WHERE id = ?
        """, (event_id,))
        
        row = cursor.fetchone()
        if row:
            return MemoryEvent(
                id=row[0],
                timestamp=datetime.fromisoformat(row[1]),
                event_type=row[2],
                data=json.loads(row[3]),
                importance=row[4],
                tags=json.loads(row[5])
            )
        
        return None
    
    def search_events(self, event_type: str = None, tags: List[str] = None,
                     since: datetime = None, limit: int = 100) -> List[MemoryEvent]:
        """Search for events matching criteria."""
        conditions = []
        params = []
        
        if event_type:
            conditions.append("event_type = ?")
            params.append(event_type)
        
        if since:
            conditions.append("timestamp >= ?")
            params.append(since.isoformat())
        
        query = "SELECT id, timestamp, event_type, data, importance, tags FROM memory_events"
        if conditions:
            query += " WHERE " + " AND ".join(conditions)
        
        query += " ORDER BY timestamp DESC LIMIT ?"
        params.append(limit)
        
        cursor = self.connection.cursor()
        cursor.execute(query, params)
        
        events = []
        for row in cursor.fetchall():
            event = MemoryEvent(
                id=row[0],
                timestamp=datetime.fromisoformat(row[1]),
                event_type=row[2],
                data=json.loads(row[3]),
                importance=row[4],
                tags=json.loads(row[5])
            )
            
            # Filter by tags if specified
            if tags and not any(tag in event.tags for tag in tags):
                continue
            
            events.append(event)
        
        return events
    
    def get_learning_summary(self) -> Dict[str, Any]:
        """Get summary of learned patterns and preferences."""
        return {
            "total_events": len(self.recent_events),
            "total_preferences": len(self.user_preferences),
            "preferences_by_category": self._group_preferences_by_category(),
            "learning_metrics": self._calculate_learning_metrics(),
            "recent_feedback_count": self._count_recent_feedback()
        }
    
    def _group_preferences_by_category(self) -> Dict[str, int]:
        """Group preferences by category."""
        categories = {}
        for pref in self.user_preferences.values():
            categories[pref.category] = categories.get(pref.category, 0) + 1
        return categories
    
    def _calculate_learning_metrics(self) -> Dict[str, float]:
        """Calculate learning effectiveness metrics."""
        if not self.user_preferences:
            return {"average_confidence": 0.0, "high_confidence_percentage": 0.0}
        
        confidences = [pref.confidence for pref in self.user_preferences.values()]
        avg_confidence = sum(confidences) / len(confidences)
        high_confidence_count = sum(1 for c in confidences if c > 0.7)
        high_confidence_percentage = high_confidence_count / len(confidences) * 100
        
        return {
            "average_confidence": avg_confidence,
            "high_confidence_percentage": high_confidence_percentage
        }
    
    def _count_recent_feedback(self) -> int:
        """Count feedback received in the last 7 days."""
        week_ago = datetime.now() - timedelta(days=7)
        cursor = self.connection.cursor()
        cursor.execute("""
            SELECT COUNT(*) FROM user_feedback 
            WHERE timestamp > ?
        """, (week_ago.isoformat(),))
        
        return cursor.fetchone()[0]
    
    def close(self):
        """Close database connection."""
        if self.connection:
            self.connection.close()


# Global memory instance
memory = PersistentMemory()