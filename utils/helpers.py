"""
Utility functions and helpers
"""

import os
import re
from datetime import datetime, timedelta

class DateTimeHelper:
    @staticmethod
    def parse_pbx_timestamp(timestamp_str):
        """Parse PBX timestamp string to datetime object"""
        try:
            # Handle different timestamp formats
            formats = [
                '%Y-%m-%d %H:%M:%S',
                '%Y-%m-%d %H:%M:%S.%f',
                '%m/%d/%Y %H:%M:%S',
                '%d/%m/%Y %H:%M:%S'
            ]
            
            for fmt in formats:
                try:
                    return datetime.strptime(timestamp_str, fmt)
                except ValueError:
                    continue
            
            return None
        except Exception:
            return None
    
    @staticmethod
    def format_duration(seconds):
        """Format duration in seconds to human-readable format"""
        if not seconds or seconds < 0:
            return "0s"
        
        hours = seconds // 3600
        minutes = (seconds % 3600) // 60
        secs = seconds % 60
        
        if hours > 0:
            return f"{hours}h {minutes}m {secs}s"
        elif minutes > 0:
            return f"{minutes}m {secs}s"
        else:
            return f"{secs}s"

class FileHelper:
    @staticmethod
    def ensure_directory(path):
        """Ensure directory exists, create if not"""
        directory = os.path.dirname(path)
        if directory and not os.path.exists(directory):
            os.makedirs(directory)
    
    @staticmethod
    def get_file_size_mb(filepath):
        """Get file size in MB"""
        try:
            size_bytes = os.path.getsize(filepath)
            return size_bytes / (1024 * 1024)
        except (OSError, FileNotFoundError):
            return 0
    
    @staticmethod
    def backup_file(filepath, backup_suffix=".bak"):
        """Create a backup of the file"""
        if os.path.exists(filepath):
            backup_path = filepath + backup_suffix
            try:
                import shutil
                shutil.copy2(filepath, backup_path)
                return backup_path
            except Exception as e:
                print(f"Warning: Could not create backup: {e}")
                return None
        return None

class DataValidator:
    @staticmethod
    def validate_phone_number(number):
        """Basic phone number validation"""
        if not number:
            return False
        
        # Remove common formatting characters
        clean_number = re.sub(r'[^\d+]', '', number)
        
        # Check if it's a reasonable length for a phone number
        return 3 <= len(clean_number) <= 15
    
    @staticmethod
    def validate_sip_uri(uri):
        """Basic SIP URI validation"""
        if not uri:
            return False
        
        # Simple SIP URI pattern
        sip_pattern = r'^sip:[^@]+@[^@]+$'
        return bool(re.match(sip_pattern, uri))
    
    @staticmethod
    def sanitize_filename(filename):
        """Sanitize filename by removing/replacing invalid characters"""
        # Replace invalid characters with underscores
        invalid_chars = r'[<>:"/\\|?*]'
        sanitized = re.sub(invalid_chars, '_', filename)
        
        # Remove multiple consecutive underscores
        sanitized = re.sub(r'_+', '_', sanitized)
        
        # Remove leading/trailing underscores and dots
        sanitized = sanitized.strip('_.')
        
        return sanitized or 'unnamed_file'

class ProgressTracker:
    def __init__(self, total, description="Processing"):
        self.total = total
        self.current = 0
        self.description = description
        self.start_time = datetime.now()
    
    def update(self, increment=1):
        """Update progress"""
        self.current += increment
        self.display()
    
    def display(self):
        """Display current progress"""
        if self.total > 0:
            percentage = (self.current / self.total) * 100
            elapsed = datetime.now() - self.start_time
            
            if self.current > 0:
                estimated_total = elapsed * (self.total / self.current)
                remaining = estimated_total - elapsed
                
                print(f"\r{self.description}: {self.current:,}/{self.total:,} "
                      f"({percentage:.1f}%) - "
                      f"Elapsed: {elapsed.seconds}s, "
                      f"Remaining: ~{remaining.seconds}s", end='', flush=True)
            else:
                print(f"\r{self.description}: {self.current:,}/{self.total:,} "
                      f"({percentage:.1f}%)", end='', flush=True)
    
    def finish(self):
        """Finish progress tracking"""
        self.current = self.total
        self.display()
        print()  # New line