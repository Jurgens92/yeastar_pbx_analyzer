"""
Database operations and schema management
"""

import sqlite3
from config.patterns import TABLES

class DatabaseManager:
    def __init__(self, db_path):
        self.db_path = db_path
        
    def init_database(self):
        """Initialize SQLite database with required tables"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Create all tables
        self._create_log_entries_table(cursor)
        self._create_sip_messages_table(cursor)
        self._create_call_records_table(cursor)
        self._create_registration_events_table(cursor)
        self._create_system_events_table(cursor)
        self._create_call_statistics_table(cursor)
        
        conn.commit()
        conn.close()
        print(f"Database initialized: {self.db_path}")
    
    def _create_log_entries_table(self, cursor):
        """Create log entries table"""
        cursor.execute(f'''
            CREATE TABLE IF NOT EXISTS {TABLES['LOG_ENTRIES']} (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                timestamp TEXT,
                level TEXT,
                thread_id INTEGER,
                module TEXT,
                line_number INTEGER,
                message TEXT,
                log_type TEXT,
                parsed_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
    
    def _create_sip_messages_table(self, cursor):
        """Create SIP messages table"""
        cursor.execute(f'''
            CREATE TABLE IF NOT EXISTS {TABLES['SIP_MESSAGES']} (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                timestamp TEXT,
                direction TEXT,
                message_type TEXT,
                method TEXT,
                response_code INTEGER,
                response_text TEXT,
                bytes_size INTEGER,
                remote_host TEXT,
                remote_port INTEGER,
                headers TEXT,
                body TEXT,
                call_id TEXT,
                from_user TEXT,
                to_user TEXT,
                via_branch TEXT
            )
        ''')
    
    def _create_call_records_table(self, cursor):
        """Create call records table"""
        cursor.execute(f'''
            CREATE TABLE IF NOT EXISTS {TABLES['CALL_RECORDS']} (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                call_datetime TEXT,
                timestamp_unix INTEGER,
                uid TEXT,
                caller_id TEXT,
                source_number TEXT,
                source_name TEXT,
                destination_number TEXT,
                destination_name TEXT,
                context TEXT,
                channel TEXT,
                destination_channel TEXT,
                trunk TEXT,
                last_app TEXT,
                last_data TEXT,
                duration INTEGER,
                ring_duration INTEGER,
                talk_duration INTEGER,
                disposition TEXT,
                call_type TEXT,
                unique_id TEXT,
                recording_file TEXT,
                recording_path TEXT,
                amount REAL,
                call_flow TEXT,
                call_flow_number TEXT,
                parsed_data TEXT
            )
        ''')
    
    def _create_registration_events_table(self, cursor):
        """Create registration events table"""
        cursor.execute(f'''
            CREATE TABLE IF NOT EXISTS {TABLES['REGISTRATION_EVENTS']} (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                timestamp TEXT,
                event_type TEXT,
                attempt_number INTEGER,
                server_uri TEXT,
                client_uri TEXT,
                response_code INTEGER,
                response_text TEXT,
                username TEXT,
                realm TEXT,
                nonce TEXT,
                registration_duration INTEGER
            )
        ''')
    
    def _create_system_events_table(self, cursor):
        """Create system events table"""
        cursor.execute(f'''
            CREATE TABLE IF NOT EXISTS {TABLES['SYSTEM_EVENTS']} (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                timestamp TEXT,
                event_type TEXT,
                category TEXT,
                description TEXT,
                error_code INTEGER,
                details TEXT
            )
        ''')
    
    def _create_call_statistics_table(self, cursor):
        """Create call statistics table"""
        cursor.execute(f'''
            CREATE TABLE IF NOT EXISTS {TABLES['CALL_STATISTICS']} (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                date TEXT,
                hour INTEGER,
                total_calls INTEGER,
                answered_calls INTEGER,
                missed_calls INTEGER,
                busy_calls INTEGER,
                failed_calls INTEGER,
                avg_duration REAL,
                max_duration INTEGER,
                total_duration INTEGER,
                unique_callers INTEGER,
                peak_concurrent_calls INTEGER,
                calculated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
    
    def get_connection(self):
        """Get database connection"""
        return sqlite3.connect(self.db_path)
    
    def store_log_entry(self, entry):
        """Store parsed log entry in database"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        cursor.execute(f'''
            INSERT INTO {TABLES['LOG_ENTRIES']}
            (timestamp, level, thread_id, module, line_number, message, log_type)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        ''', (entry['timestamp'], entry['level'], entry['thread_id'], 
              entry['module'], entry['line_number'], entry['message'], entry['log_type']))
        
        conn.commit()
        conn.close()
    
    # Add other storage methods here...
    def store_call_record(self, record):
        """Store call record in database"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        cursor.execute(f'''
            INSERT INTO {TABLES['CALL_RECORDS']}
            (call_datetime, timestamp_unix, uid, caller_id, source_number, source_name,
             destination_number, destination_name, context, channel, destination_channel,
             trunk, last_app, last_data, duration, ring_duration, talk_duration,
             disposition, call_type, unique_id, parsed_data)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (record['call_datetime'], record['timestamp_unix'], record['uid'],
              record['caller_id'], record['source_number'], record['source_name'],
              record['destination_number'], record['destination_name'], record['context'],
              record['channel'], record['destination_channel'], record['trunk'],
              record['last_app'], record['last_data'], record['duration'],
              record['ring_duration'], record['talk_duration'], record['disposition'],
              record['call_type'], record['unique_id'], record['parsed_data']))
        
        conn.commit()
        conn.close()