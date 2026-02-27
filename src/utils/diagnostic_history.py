"""
Diagnostic History & Database Module
Persistence layer for diagnostic records and analytics
"""

import sqlite3
import json
from datetime import datetime
from pathlib import Path
from typing import List, Dict, Optional
import pandas as pd
from src.utils.error_handlers import DatabaseError, retry_with_backoff
from src.utils.logger_setup import get_logger

logger = get_logger(__name__)


class DiagnosticHistory:
    """Manage diagnostic records and historical data"""
    
    def __init__(self, db_path: str = "data/diagnostics.db"):
        self.db_path = db_path
        self._init_db()
    
    def _init_db(self):
        """Initialize database schema if it doesn't exist"""
        Path(self.db_path).parent.mkdir(parents=True, exist_ok=True)
        
        try:
            with sqlite3.connect(self.db_path) as conn:
                conn.execute("""
                    CREATE TABLE IF NOT EXISTS diagnostics (
                        id TEXT PRIMARY KEY,
                        timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
                        vehicle_model TEXT NOT NULL,
                        dtc_codes TEXT,
                        symptoms TEXT,
                        operating_condition TEXT,
                        diagnosis TEXT,
                        confidence_score FLOAT,
                        action_plan TEXT,
                        safety_warning TEXT,
                        rag_evidence TEXT,
                        web_evidence TEXT,
                        resolution TEXT,
                        resolution_date DATETIME,
                        feedback_score INT,
                        user_id TEXT,
                        api_latency_ms FLOAT
                    )
                """)
                
                conn.execute("""
                    CREATE TABLE IF NOT EXISTS sensor_readings (
                        id TEXT PRIMARY KEY,
                        diagnostic_id TEXT NOT NULL,
                        rpm INT,
                        speed INT,
                        load INT,
                        temp INT,
                        timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
                        FOREIGN KEY (diagnostic_id) REFERENCES diagnostics(id)
                    )
                """)
                
                conn.execute("""
                    CREATE TABLE IF NOT EXISTS analytics (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        session_id TEXT,
                        timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
                        event_type TEXT,
                        vehicle_model TEXT,
                        dtc_count INT,
                        vision_calls INT,
                        agent_latency_ms FLOAT,
                        user_feedback INT,
                        error_message TEXT
                    )
                """)
                
                conn.commit()
                logger.info(f"Database initialized: {self.db_path}")
        
        except Exception as e:
            raise DatabaseError(f"Failed to initialize database: {str(e)}")
    
    @retry_with_backoff(max_attempts=3, exceptions=(DatabaseError,))
    def save_diagnosis(self, diagnosis_data: Dict) -> str:
        """
        Save completed diagnosis to database
        
        Args:
            diagnosis_data: Dictionary containing diagnosis information
        
        Returns:
            Diagnosis ID
        """
        diagnosis_id = diagnosis_data.get('id', str(datetime.now().timestamp()))
        
        try:
            with sqlite3.connect(self.db_path) as conn:
                conn.execute("""
                    INSERT OR REPLACE INTO diagnostics 
                    (id, vehicle_model, dtc_codes, symptoms, operating_condition,
                     diagnosis, confidence_score, action_plan, safety_warning,
                     rag_evidence, web_evidence, api_latency_ms)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """, (
                    diagnosis_id,
                    diagnosis_data.get('vehicle_model', ''),
                    diagnosis_data.get('dtc_codes', ''),
                    diagnosis_data.get('symptoms', ''),
                    diagnosis_data.get('operating_condition', ''),
                    diagnosis_data.get('diagnosis', ''),
                    diagnosis_data.get('confidence_score', 0.0),
                    json.dumps(diagnosis_data.get('action_plan', [])),
                    diagnosis_data.get('safety_warning', ''),
                    diagnosis_data.get('rag_evidence', ''),
                    diagnosis_data.get('web_evidence', ''),
                    diagnosis_data.get('api_latency_ms', 0.0),
                ))
                
                # Save sensor readings if available
                if 'sensor_readings' in diagnosis_data:
                    sensors = diagnosis_data['sensor_readings']
                    conn.execute("""
                        INSERT INTO sensor_readings (id, diagnostic_id, rpm, speed, load, temp)
                        VALUES (?, ?, ?, ?, ?, ?)
                    """, (
                        f"{diagnosis_id}_sensors",
                        diagnosis_id,
                        sensors.get('rpm'),
                        sensors.get('speed'),
                        sensors.get('load'),
                        sensors.get('temp'),
                    ))
                
                conn.commit()
                logger.info(f"Diagnosis saved with ID: {diagnosis_id}")
                return diagnosis_id
        
        except Exception as e:
            raise DatabaseError(f"Failed to save diagnosis: {str(e)}")
    
    def get_similar_cases(self, dtc_code: str, vehicle_model: str = "", limit: int = 5) -> pd.DataFrame:
        """
        Find similar historical cases for reference
        
        Args:
            dtc_code: DTC code to search for
            vehicle_model: Optional vehicle model filter
            limit: Number of results to return
        
        Returns:
            DataFrame of similar cases
        """
        try:
            with sqlite3.connect(self.db_path) as conn:
                query = """
                    SELECT id, timestamp, vehicle_model, dtc_codes, diagnosis, 
                           confidence_score, resolution
                    FROM diagnostics
                    WHERE dtc_codes LIKE ?
                """
                params = [f"%{dtc_code}%"]
                
                if vehicle_model:
                    query += " AND vehicle_model LIKE ?"
                    params.append(f"%{vehicle_model}%")
                
                query += " ORDER BY timestamp DESC LIMIT ?"
                params.append(limit)
                
                df = pd.read_sql_query(query, conn, params=params)
                logger.info(f"Found {len(df)} similar cases for DTC {dtc_code}")
                return df
        
        except Exception as e:
            logger.error(f"Failed to retrieve similar cases: {str(e)}")
            return pd.DataFrame()
    
    def update_resolution(self, diagnosis_id: str, resolution: str, feedback_score: int = None):
        """
        Update diagnosis with resolution details
        
        Args:
            diagnosis_id: ID of the diagnosis
            resolution: Description of the resolution
            feedback_score: User feedback score (1-5)
        """
        try:
            with sqlite3.connect(self.db_path) as conn:
                conn.execute("""
                    UPDATE diagnostics
                    SET resolution = ?, resolution_date = CURRENT_TIMESTAMP, feedback_score = ?
                    WHERE id = ?
                """, (resolution, feedback_score, diagnosis_id))
                conn.commit()
                logger.info(f"Updated resolution for diagnosis {diagnosis_id}")
        
        except Exception as e:
            raise DatabaseError(f"Failed to update resolution: {str(e)}")
    
    def log_analytics_event(self, session_data: Dict):
        """
        Log analytics event for monitoring and metrics
        
        Args:
            session_data: Dictionary of session metrics
        """
        try:
            with sqlite3.connect(self.db_path) as conn:
                conn.execute("""
                    INSERT INTO analytics 
                    (session_id, event_type, vehicle_model, dtc_count, 
                     vision_calls, agent_latency_ms, user_feedback, error_message)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                """, (
                    session_data.get('session_id'),
                    session_data.get('event_type', 'diagnostic'),
                    session_data.get('vehicle_model'),
                    session_data.get('dtc_count', 0),
                    session_data.get('vision_calls', 0),
                    session_data.get('agent_latency_ms', 0.0),
                    session_data.get('user_feedback'),
                    session_data.get('error_message'),
                ))
                conn.commit()
        
        except Exception as e:
            logger.error(f"Failed to log analytics: {str(e)}")
    
    def get_statistics(self) -> Dict:
        """Get database statistics"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                
                cursor.execute("SELECT COUNT(*) FROM diagnostics")
                total_diagnostics = cursor.fetchone()[0]
                
                cursor.execute("SELECT AVG(confidence_score) FROM diagnostics WHERE confidence_score > 0")
                avg_confidence = cursor.fetchone()[0] or 0
                
                cursor.execute("SELECT AVG(feedback_score) FROM diagnostics WHERE feedback_score IS NOT NULL")
                avg_feedback = cursor.fetchone()[0] or 0
                
                return {
                    'total_diagnostics': total_diagnostics,
                    'avg_confidence': round(avg_confidence, 2),
                    'avg_feedback': round(avg_feedback, 2) if avg_feedback else 'N/A',
                }
        
        except Exception as e:
            logger.error(f"Failed to get statistics: {str(e)}")
            return {}
    
    def cleanup_old_records(self, days_old: int = 90):
        """Delete records older than specified days"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                conn.execute("""
                    DELETE FROM diagnostics
                    WHERE datetime(timestamp) < datetime('now', '-' || ? || ' days')
                """, (days_old,))
                affected = conn.total_changes
                conn.commit()
                logger.info(f"Cleaned up {affected} old records")
        
        except Exception as e:
            logger.error(f"Failed to cleanup old records: {str(e)}")


# Initialize global history instance
diagnostic_history = DiagnosticHistory()
