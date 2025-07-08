"""
Multiprocessing-enabled analyzer - FAST with FULL data extraction
"""

import os
import multiprocessing as mp
from queue import Empty
import re
from datetime import datetime
from core.database import DatabaseManager
from core.parsers import LogParser
from reports.html_generator import HTMLReportGenerator
from config.patterns import DEFAULT_DB_NAME, TABLES

class MultiprocessingYeastarLogAnalyzer:
    def __init__(self, db_path=DEFAULT_DB_NAME, max_workers=None):
        self.db_path = db_path
        self.log_file = None
        self.max_workers = max_workers or max(1, mp.cpu_count() - 1)
        
        # Initialize components
        self.db = DatabaseManager(db_path)
        self.parser = LogParser()
        self.report_gen = HTMLReportGenerator(self.db)
        
        # Initialize database
        self.db.init_database()
        self._optimize_database()
    
    def parse_log_file(self, log_file_path, chunk_size=10000):
        """Parse log file using multiprocessing - FAST with FULL extraction"""
        if not os.path.exists(log_file_path):
            print(f"❌ Log file not found: {log_file_path}")
            return False
        
        self.log_file = log_file_path
        print(f"📖 Parsing log file: {log_file_path}")
        
        try:
            # Read file exactly like original
            with open(log_file_path, 'r', encoding='utf-8', errors='ignore') as f:
                content = f.read()
            
            lines = content.split('\n')
            total_lines = len(lines)
            print(f"📋 Total lines: {total_lines:,}")
            
            # Create result queue for batched database operations
            result_queue = mp.Queue(maxsize=100)
            
            # Start database writer process
            print("🔧 Starting database writer...")
            db_writer = mp.Process(
                target=self._batch_database_writer,
                args=(result_queue, self.db_path)
            )
            db_writer.start()
            
            # Create chunks and process with Pool
            chunks = []
            for i in range(0, total_lines, chunk_size):
                end_idx = min(i + chunk_size, total_lines)
                chunk_lines = lines[i:end_idx]
                chunks.append((i, chunk_lines))
            
            print(f"📦 Processing {len(chunks)} chunks with {self.max_workers} workers...")
            
            # Process chunks with multiprocessing Pool
            with mp.Pool(processes=self.max_workers) as pool:
                results = pool.starmap(self._extract_all_data_from_chunk, chunks)
            
            # Send all results to database writer
            for result in results:
                if result:
                    result_queue.put(result)
            
            # Signal database writer to stop
            result_queue.put(None)
            print("⏳ Waiting for database writer to complete...")
            db_writer.join()
            
            print(f"✅ Multiprocessing parsing complete!")
            return True
            
        except Exception as e:
            print(f"❌ Error parsing log file: {e}")
            return False
    
    @staticmethod
    def _extract_all_data_from_chunk(start_idx, lines):
        """Extract ALL data types from chunk - NO database operations here"""
        parser = LogParser()
        
        # Collect all data in lists (no database operations!)
        log_entries = []
        call_records = []
        sip_messages = []
        reg_events = []
        sys_events = []
        
        i = 0
        while i < len(lines):
            line = lines[i].strip()
            if not line:
                i += 1
                continue
            
            try:
                # Parse basic log entry
                entry = parser.parse_log_entry(line)
                if entry:
                    log_entries.append(entry)
                    
                    # Extract CDR records
                    if 'INSERT INTO cdr' in entry['message']:
                        call_record = parser.parse_cdr_entry(entry['message'])
                        if call_record:
                            call_records.append(call_record)
                    
                    # Extract SIP messages
                    message = entry['message']
                    
                    if 'Transmitting SIP' in message:
                        sip_data = MultiprocessingYeastarLogAnalyzer._extract_sip_transmit(entry)
                        if sip_data:
                            sip_messages.append(sip_data)
                    
                    elif 'Received SIP' in message:
                        sip_data = MultiprocessingYeastarLogAnalyzer._extract_sip_receive(entry)
                        if sip_data:
                            sip_messages.append(sip_data)
                    
                    # Extract Registration Events
                    elif 'REGISTER' in message or 'register' in message.lower():
                        reg_data = MultiprocessingYeastarLogAnalyzer._extract_registration_event(entry)
                        if reg_data:
                            reg_events.append(reg_data)
                    
                    # Extract System Events
                    if entry['level'] in ['ERROR', 'WARNING']:
                        sys_data = MultiprocessingYeastarLogAnalyzer._extract_system_event(entry)
                        if sys_data:
                            sys_events.append(sys_data)
                
            except Exception as e:
                pass  # Skip problematic lines
            
            i += 1
        
        return {
            'chunk_id': start_idx,
            'log_entries': log_entries,
            'call_records': call_records,
            'sip_messages': sip_messages,
            'reg_events': reg_events,
            'sys_events': sys_events
        }
    
    def _batch_database_writer(self, result_queue, db_path):
        """FAST batch database writer"""
        db = DatabaseManager(db_path)
        
        total_entries = 0
        total_calls = 0
        total_sip = 0
        total_reg = 0
        total_sys = 0
        
        print("🔧 Database writer started")
        
        while True:
            try:
                result = result_queue.get(timeout=30)
                if result is None:
                    break
                
                # BATCH insert everything at once
                if result['log_entries']:
                    self._batch_insert_log_entries(db, result['log_entries'])
                    total_entries += len(result['log_entries'])
                
                if result['call_records']:
                    self._batch_insert_call_records(db, result['call_records'])
                    total_calls += len(result['call_records'])
                
                if result['sip_messages']:
                    self._batch_insert_sip_messages(db, result['sip_messages'])
                    total_sip += len(result['sip_messages'])
                
                if result['reg_events']:
                    self._batch_insert_reg_events(db, result['reg_events'])
                    total_reg += len(result['reg_events'])
                
                if result['sys_events']:
                    self._batch_insert_sys_events(db, result['sys_events'])
                    total_sys += len(result['sys_events'])
                
                print(f"💾 Chunk {result['chunk_id']}: +{len(result['log_entries'])} entries, +{len(result['sip_messages'])} SIP, +{len(result['reg_events'])} reg")
                    
            except Empty:
                continue
            except Exception as e:
                print(f"❌ Database writer error: {e}")
        
        print(f"✅ Database writer complete:")
        print(f"   📋 Log entries: {total_entries:,}")
        print(f"   📊 Call records: {total_calls:,}")
        print(f"   🌐 SIP messages: {total_sip:,}")
        print(f"   🔐 Registration events: {total_reg:,}")
        print(f"   ⚠️ System events: {total_sys:,}")
    
    def _batch_insert_log_entries(self, db, entries):
        """FAST batch insert log entries"""
        if not entries:
            return
        
        conn = db.get_connection()
        cursor = conn.cursor()
        
        try:
            cursor.executemany(f'''
                INSERT INTO {TABLES['LOG_ENTRIES']}
                (timestamp, level, thread_id, module, line_number, message, log_type)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            ''', [(e['timestamp'], e['level'], e['thread_id'], e['module'], 
                   e['line_number'], e['message'], e['log_type']) for e in entries])
            
            conn.commit()
        finally:
            conn.close()
    
    def _batch_insert_call_records(self, db, records):
        """FAST batch insert call records"""
        if not records:
            return
        
        conn = db.get_connection()
        cursor = conn.cursor()
        
        try:
            cursor.executemany(f'''
                INSERT INTO {TABLES['CALL_RECORDS']}
                (call_datetime, timestamp_unix, uid, caller_id, source_number, source_name,
                 destination_number, destination_name, context, channel, destination_channel,
                 trunk, last_app, last_data, duration, ring_duration, talk_duration,
                 disposition, call_type, unique_id, parsed_data)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', [(r['call_datetime'], r['timestamp_unix'], r['uid'], r['caller_id'],
                   r['source_number'], r['source_name'], r['destination_number'],
                   r['destination_name'], r['context'], r['channel'], 
                   r['destination_channel'], r['trunk'], r['last_app'], r['last_data'],
                   r['duration'], r['ring_duration'], r['talk_duration'],
                   r['disposition'], r['call_type'], r['unique_id'], 
                   r['parsed_data']) for r in records])
            
            conn.commit()
        finally:
            conn.close()
    
    def _batch_insert_sip_messages(self, db, messages):
        """FAST batch insert SIP messages"""
        if not messages:
            return
        
        conn = db.get_connection()
        cursor = conn.cursor()
        
        try:
            cursor.executemany(f'''
                INSERT INTO {TABLES['SIP_MESSAGES']}
                (timestamp, direction, message_type, method, response_code, response_text,
                 bytes_size, remote_host, remote_port, headers, body, call_id, from_user, to_user, via_branch)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', [(m['timestamp'], m['direction'], m['message_type'], m['method'],
                   m['response_code'], m['response_text'], m['bytes_size'],
                   m['remote_host'], m['remote_port'], m['headers'], m['body'],
                   m['call_id'], m['from_user'], m['to_user'], m['via_branch']) for m in messages])
            
            conn.commit()
        finally:
            conn.close()
    
    def _batch_insert_reg_events(self, db, events):
        """FAST batch insert registration events"""
        if not events:
            return
        
        conn = db.get_connection()
        cursor = conn.cursor()
        
        try:
            cursor.executemany(f'''
                INSERT INTO {TABLES['REGISTRATION_EVENTS']}
                (timestamp, event_type, attempt_number, server_uri, client_uri,
                 response_code, response_text, username, realm, nonce, registration_duration)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', [(e['timestamp'], e['event_type'], e['attempt_number'], e['server_uri'],
                   e['client_uri'], e['response_code'], e['response_text'], e['username'],
                   e['realm'], e['nonce'], e['registration_duration']) for e in events])
            
            conn.commit()
        finally:
            conn.close()
    
    def _batch_insert_sys_events(self, db, events):
        """FAST batch insert system events"""
        if not events:
            return
        
        conn = db.get_connection()
        cursor = conn.cursor()
        
        try:
            cursor.executemany(f'''
                INSERT INTO {TABLES['SYSTEM_EVENTS']}
                (timestamp, event_type, category, description, error_code, details)
                VALUES (?, ?, ?, ?, ?, ?)
            ''', [(e['timestamp'], e['event_type'], e['category'], e['description'],
                   e['error_code'], e['details']) for e in events])
            
            conn.commit()
        finally:
            conn.close()
    
    @staticmethod
    def _extract_sip_transmit(entry):
        """Extract SIP transmit message data"""
        message = entry['message']
        match = re.search(r'Transmitting SIP (\w+) \((\d+) bytes\) to ([^:]+):(\d+)', message)
        if not match:
            return None
        
        msg_type, bytes_size, remote_host, remote_port = match.groups()
        
        return {
            'timestamp': entry['timestamp'],
            'direction': 'TRANSMIT',
            'message_type': 'REQUEST',
            'method': 'Via:',
            'response_code': None,
            'response_text': None,
            'bytes_size': int(bytes_size),
            'remote_host': remote_host,
            'remote_port': int(remote_port),
            'headers': None,
            'body': None,
            'call_id': None,
            'from_user': None,
            'to_user': None,
            'via_branch': None
        }
    
    @staticmethod
    def _extract_sip_receive(entry):
        """Extract SIP receive message data"""
        message = entry['message']
        match = re.search(r'Received SIP (\w+) \((\d+) bytes\) from ([^:]+):(\d+)', message)
        if not match:
            return None
        
        msg_type, bytes_size, remote_host, remote_port = match.groups()
        
        return {
            'timestamp': entry['timestamp'],
            'direction': 'RECEIVE',
            'message_type': 'RESPONSE',
            'method': 'Via:',
            'response_code': None,
            'response_text': None,
            'bytes_size': int(bytes_size),
            'remote_host': remote_host,
            'remote_port': int(remote_port),
            'headers': None,
            'body': None,
            'call_id': None,
            'from_user': None,
            'to_user': None,
            'via_branch': None
        }
    
    @staticmethod
    def _extract_registration_event(entry):
        """Extract registration event data"""
        message = entry['message']
        
        if 'REGISTER attempt' in message or 'register attempt' in message.lower():
            event_type = 'ATTEMPT'
        elif 'REGISTER response' in message or 'register response' in message.lower():
            event_type = 'RESPONSE'
        elif 'registration successful' in message.lower():
            event_type = 'SUCCESS'
        elif 'registration failed' in message.lower():
            event_type = 'FAILURE'
        else:
            if any(word in message.lower() for word in ['success', 'ok', '200']):
                event_type = 'SUCCESS'
            elif any(word in message.lower() for word in ['fail', 'error', 'timeout', 'unauthorized']):
                event_type = 'FAILURE'
            else:
                event_type = 'ATTEMPT'
        
        server_match = re.search(r'sip:([^@]+@)?([^:;]+):(\d+)', message)
        server_uri = server_match.group(0) if server_match else None
        
        client_match = re.search(r'sip:([^@]+@[^:;]+):(\d+)', message)
        client_uri = client_match.group(0) if client_match else None
        
        return {
            'timestamp': entry['timestamp'],
            'event_type': event_type,
            'attempt_number': None,
            'server_uri': server_uri,
            'client_uri': client_uri,
            'response_code': None,
            'response_text': None,
            'username': None,
            'realm': None,
            'nonce': None,
            'registration_duration': None
        }
    
    @staticmethod
    def _extract_system_event(entry):
        """Extract system event data"""
        message = entry['message']
        level = entry['level']
        
        if 'mysql' in message.lower() or 'database' in message.lower():
            category = 'DATABASE'
        elif 'sip' in message.lower():
            category = 'SIP'
        elif 'config' in message.lower():
            category = 'CONFIG'
        elif 'thread' in message.lower():
            category = 'SYSTEM'
        else:
            category = 'GENERAL'
        
        error_code_match = re.search(r'error[:\s]*(\d+)', message.lower())
        error_code = int(error_code_match.group(1)) if error_code_match else None
        
        return {
            'timestamp': entry['timestamp'],
            'event_type': level,
            'category': category,
            'description': message,
            'error_code': error_code,
            'details': None
        }
    
    def _optimize_database(self):
        """Apply SQLite performance optimizations"""
        conn = self.db.get_connection()
        try:
            conn.execute("PRAGMA journal_mode=WAL")
            conn.execute("PRAGMA synchronous=NORMAL")
            conn.execute("PRAGMA cache_size=10000")
            conn.execute("PRAGMA temp_store=MEMORY")
            conn.commit()
            print("🔧 Database optimized")
        except Exception as e:
            print(f"⚠️ Database optimization warning: {e}")
        finally:
            conn.close()
    
    def generate_html_report(self, output_file="pbx_analysis_report.html"):
        """Generate comprehensive HTML report"""
        return self.report_gen.generate_report(output_file, self.log_file)