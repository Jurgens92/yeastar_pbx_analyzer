"""
Log parsing functionality
"""

import re
import json
from datetime import datetime
from config.patterns import LOG_PATTERNS, LOG_TYPES

class LogParser:
    def __init__(self):
        self.patterns = LOG_PATTERNS
    
    def parse_log_entry(self, line):
        """Parse a single log entry"""
        match = re.match(self.patterns['log_entry'], line)
        if match:
            timestamp, level, thread_id, module, line_num, message = match.groups()
            return {
                'timestamp': timestamp,
                'level': level,
                'thread_id': int(thread_id),
                'module': module,
                'line_number': int(line_num),
                'message': message,
                'log_type': self.classify_log_type(message)
            }
        return None
    
    def classify_log_type(self, message):
        """Classify the type of log message"""
        if 'SIP' in message:
            return LOG_TYPES['SIP']
        elif 'cdr' in message.lower():
            return LOG_TYPES['CDR']
        elif 'REGISTER' in message:
            return LOG_TYPES['REGISTRATION']
        elif 'MySQL' in message:
            return LOG_TYPES['DATABASE']
        elif 'threadpool' in message:
            return LOG_TYPES['SYSTEM']
        elif 'config' in message.lower():
            return LOG_TYPES['CONFIG']
        else:
            return LOG_TYPES['GENERAL']
    
    def extract_sip_block(self, lines, start_index):
        """Extract a complete SIP message block"""
        sip_lines = [lines[start_index]]
        i = start_index + 1
        
        while i < len(lines) and lines[i].strip():
            line = lines[i].strip()
            sip_lines.append(line)
            i += 1
            
            if not line:
                break
            
            if re.match(self.patterns['log_entry'], line):
                i -= 1
                break
        
        return sip_lines, i - start_index
    
    # Add other parsing methods...
    def parse_cdr_entry(self, message):
        """Parse CDR INSERT statement"""
        match = re.search(self.patterns['cdr_insert'], message)
        if not match:
            return None
        
        values_str = match.group(1)
        
        try:
            # Simplified CSV parsing
            values = []
            current_value = ""
            in_quotes = False
            
            for char in values_str:
                if char == "'" and not in_quotes:
                    in_quotes = True
                elif char == "'" and in_quotes:
                    in_quotes = False
                elif char == ',' and not in_quotes:
                    values.append(current_value.strip("'"))
                    current_value = ""
                    continue
                
                if not (char == "'" and (not in_quotes or current_value == "")):
                    current_value += char
            
            if current_value:
                values.append(current_value.strip("'"))
            
            # Map to CDR fields
            if len(values) >= 20:
                return {
                    'call_datetime': values[0] if len(values) > 0 else '',
                    'timestamp_unix': int(values[1]) if len(values) > 1 and values[1].isdigit() else 0,
                    'uid': values[2] if len(values) > 2 else '',
                    'caller_id': values[3] if len(values) > 3 else '',
                    'source_number': values[4] if len(values) > 4 else '',
                    'source_name': values[5] if len(values) > 5 else '',
                    'destination_number': values[6] if len(values) > 6 else '',
                    'destination_name': values[7] if len(values) > 7 else '',
                    'context': values[8] if len(values) > 8 else '',
                    'channel': values[9] if len(values) > 9 else '',
                    'destination_channel': values[10] if len(values) > 10 else '',
                    'trunk': values[11] if len(values) > 11 else '',
                    'last_app': values[12] if len(values) > 12 else '',
                    'last_data': values[13] if len(values) > 13 else '',
                    'duration': int(values[14]) if len(values) > 14 and values[14].isdigit() else 0,
                    'ring_duration': int(values[15]) if len(values) > 15 and values[15].isdigit() else 0,
                    'talk_duration': int(values[16]) if len(values) > 16 and values[16].isdigit() else 0,
                    'disposition': values[17] if len(values) > 17 else '',
                    'call_type': values[19] if len(values) > 19 else '',
                    'unique_id': values[20] if len(values) > 20 else '',
                    'parsed_data': json.dumps(values)
                }
        
        except Exception as e:
            print(f"Error parsing CDR entry: {e}")
            return None
        
        return None