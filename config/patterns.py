"""
Configuration file for regex patterns and constants
"""

# Regex patterns for different log types
LOG_PATTERNS = {
    'log_entry': r'\[([^\]]+)\] ([A-Z]+)\[(\d+)\] ([^:]+):(\d+) (.*)',
    'sip_transmit': r'<--- Transmitting SIP request \((\d+) bytes\) to ([^:]+):(\d+) --->',
    'sip_receive': r'<--- Received SIP response \((\d+) bytes\) from ([^:]+):(\d+) --->',
    'register_attempt': r'Outbound REGISTER attempt (\d+) to \'([^\']+)\' with client \'([^\']+)\'',
    'register_response': r'Received REGISTER response (\d+)\(([^)]+)\)',
    'cdr_insert': r'INSERT INTO cdr.*VALUES \((.*)\)',
    'call_flow': r'Current callflow \[([^\]]+)\], callnote switch:\[(\d+)\]',
    'dial_event': r'lastapp.*Dial.*\'([^\']+)\'',
    'mysql_error': r'MySQL.*Error \((\d+)\): (.*)',
    'thread_timeout': r'Worker thread idle timeout reached'
}

# Database configuration
DEFAULT_DB_NAME = "pbx_analysis.db"

# Table names
TABLES = {
    'LOG_ENTRIES': 'log_entries',
    'SIP_MESSAGES': 'sip_messages',
    'CALL_RECORDS': 'call_records',
    'REGISTRATION_EVENTS': 'registration_events',
    'SYSTEM_EVENTS': 'system_events',
    'CALL_STATISTICS': 'call_statistics'
}

# Log type classifications
LOG_TYPES = {
    'SIP': 'SIP',
    'CDR': 'CDR',
    'REGISTRATION': 'REGISTRATION',
    'DATABASE': 'DATABASE',
    'SYSTEM': 'SYSTEM',
    'CONFIG': 'CONFIG',
    'GENERAL': 'GENERAL'
}