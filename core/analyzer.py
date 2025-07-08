"""
Main analyzer class - now much simpler and focused
"""

import os
from datetime import datetime
from core.database import DatabaseManager
from core.parsers import LogParser
from reports.html_generator import HTMLReportGenerator
from config.patterns import DEFAULT_DB_NAME

class YeastarLogAnalyzer:
    def __init__(self, db_path=DEFAULT_DB_NAME):
        self.db_path = db_path
        self.log_file = None
        
        # Initialize components
        self.db = DatabaseManager(db_path)
        self.parser = LogParser()
        self.report_gen = HTMLReportGenerator(self.db)
        
        # Initialize database
        self.db.init_database()
    
    def parse_log_file(self, log_file_path):
        """Parse the main log file and extract different types of events"""
        if not os.path.exists(log_file_path):
            print(f"❌ Log file not found: {log_file_path}")
            return False
        
        self.log_file = log_file_path
        print(f"📖 Parsing log file: {log_file_path}")
        
        try:
            with open(log_file_path, 'r', encoding='utf-8', errors='ignore') as f:
                content = f.read()
            
            lines = content.split('\n')
            
            parsed_entries = 0
            call_records = 0
            
            i = 0
            while i < len(lines):
                line = lines[i].strip()
                if not line:
                    i += 1
                    continue
                
                # Parse regular log entry
                entry = self.parser.parse_log_entry(line)
                if entry:
                    self.db.store_log_entry(entry)
                    parsed_entries += 1
                    
                    # Check for CDR entries
                    if 'INSERT INTO cdr' in entry['message']:
                        call_record = self.parser.parse_cdr_entry(entry['message'])
                        if call_record:
                            self.db.store_call_record(call_record)
                            call_records += 1
                
                i += 1
            
            print(f"✅ Parsing complete:")
            print(f"   📋 Log entries: {parsed_entries:,}")
            print(f"   📊 Call records: {call_records:,}")
            
            return True
            
        except Exception as e:
            print(f"❌ Error parsing log file: {e}")
            return False
    
    def generate_html_report(self, output_file="pbx_analysis_report.html"):
        """Generate comprehensive HTML report"""
        return self.report_gen.generate_report(output_file, self.log_file)