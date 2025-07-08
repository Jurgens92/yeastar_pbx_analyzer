"""
Interactive menu system for the PBX analyzer
"""

import os
import sqlite3
import webbrowser
import multiprocessing as mp
from core.analyzer import YeastarLogAnalyzer
from core.multiprocessing_analyzer import MultiprocessingYeastarLogAnalyzer
from ui.search_interface import SearchInterface
from reports.csv_exporter import CSVExporter

class MainMenu:
    def __init__(self):
        self.analyzer = YeastarLogAnalyzer()
        self.mp_analyzer = MultiprocessingYeastarLogAnalyzer()
        self.search_interface = SearchInterface(self.analyzer)
        self.csv_exporter = CSVExporter(self.analyzer)
        
    def run(self):
        """Main menu loop"""
        while True:
            self.display_menu()
            
            try:
                choice = input("Enter your choice (1-9): ").strip()
                
                if choice == '1':
                    self.parse_log_file()
                elif choice == '2':
                    self.generate_html_report()
                elif choice == '3':
                    self.search_interface.search_call_records()
                elif choice == '4':
                    self.search_interface.view_call_statistics()
                elif choice == '5':
                    self.search_interface.view_registration_events()
                elif choice == '6':
                    self.search_interface.view_system_events()
                elif choice == '7':
                    self.database_management()
                elif choice == '8':
                    self.settings_menu()
                elif choice == '9':
                    print("\n👋 Goodbye!")
                    break
                else:
                    print("❌ Invalid choice. Please enter 1-9.")
            
            except KeyboardInterrupt:
                print("\n\n👋 Goodbye!")
                break
            except Exception as e:
                print(f"❌ Error: {e}")
    
    def display_menu(self):
        """Display the main menu"""
        cpu_count = mp.cpu_count()
        print("\n" + "="*60)
        print("📞 YEASTAR PBX LOG ANALYSIS TOOL")
        print("="*60)
        print("1. 📖 Parse Log File")
        print("2. 📊 Generate HTML Report")
        print("3. 🔍 Search Call Records")
        print("4. 📈 View Call Statistics")
        print("5. 🔐 View Registration Events")
        print("6. ⚠️  View System Events")
        print("7. 🗄️  Database Management")
        print("8. ⚙️  Settings")
        print("9. ❌ Exit")
        print("-"*60)
        print(f"💻 System: {cpu_count} CPU cores available")
    
    def parse_log_file(self):
        """Handle log file parsing with processing method choice"""
        print("\n📖 PARSE LOG FILE")
        log_file = input("Enter path to log file (e.g., pbxlog.0): ").strip()
        
        if not log_file or not os.path.exists(log_file):
            print("❌ File not found or invalid path")
            return
        
        # Check file size to recommend processing method
        file_size_mb = os.path.getsize(log_file) / (1024 * 1024)
        print(f"📁 File size: {file_size_mb:.1f} MB")
        
        # Recommend processing method based on file size
        if file_size_mb > 50:
            print("🚀 Large file detected - multiprocessing recommended!")
            default_choice = "m"
        else:
            print("📄 Small file - single processing is fine")
            default_choice = "s"
        
        print("\nProcessing options:")
        print("  s) Single-threaded (traditional)")
        print(f"  m) Multi-processing ({mp.cpu_count()} cores)")
        print("  a) Auto-choose based on file size")
        
        choice = input(f"Choose processing method (s/m/a, default: {default_choice}): ").strip().lower()
        
        if choice == '' or choice == 'a':
            choice = default_choice
        
        if choice == 'm':
            print(f"\n🚀 Using multiprocessing with {self.mp_analyzer.max_workers} workers...")
            # Ask for chunk size
            chunk_input = input(f"Chunk size (lines per chunk, default: 5000): ").strip()
            try:
                chunk_size = int(chunk_input) if chunk_input else 5000
            except ValueError:
                chunk_size = 5000
            
            success = self.mp_analyzer.parse_log_file(log_file, chunk_size)
            
        else:  # single processing
            print("\n📝 Using single-threaded processing...")
            success = self.analyzer.parse_log_file(log_file)
        
        if success:
            print("✅ Parsing completed successfully!")
        else:
            print("❌ Parsing failed!")
    
    def generate_html_report(self):
        """Handle HTML report generation"""
        print("\n📊 GENERATING HTML REPORT")
        
        # Check if we have data
        conn = sqlite3.connect(self.analyzer.db_path)
        result = conn.execute("SELECT COUNT(*) FROM log_entries").fetchone()
        conn.close()
        
        if result[0] == 0:
            print("❌ No data found. Please parse a log file first.")
            return
        
        output_file = input("Enter output filename (default: pbx_analysis_report.html): ").strip()
        if not output_file:
            output_file = "pbx_analysis_report.html"
        
        try:
            # Use the analyzer that has data (check both)
            if hasattr(self.mp_analyzer, 'log_file') and self.mp_analyzer.log_file:
                report_path = self.mp_analyzer.generate_html_report(output_file)
            else:
                report_path = self.analyzer.generate_html_report(output_file)
            
            # Ask if user wants to open the report
            open_report = input("Open report in browser? (y/n): ").strip().lower()
            if open_report == 'y':
                try:
                    webbrowser.open(f"file://{os.path.abspath(report_path)}")
                except Exception as e:
                    print(f"Could not open browser: {e}")
                    print(f"Manually open: {os.path.abspath(report_path)}")
        
        except Exception as e:
            print(f"❌ Error generating report: {e}")
    
    def database_management(self):
        """Database management submenu"""
        while True:
            print("\n🗄️ DATABASE MANAGEMENT")
            print("1. View database info")
            print("2. Export data to CSV")
            print("3. Clear all data")
            print("4. Vacuum database")
            print("5. Back to main menu")
            
            choice = input("Enter choice (1-5): ").strip()
            
            if choice == '1':
                self.view_database_info()
            elif choice == '2':
                self.csv_exporter.export_all_data()
            elif choice == '3':
                self.clear_all_data()
            elif choice == '4':
                self.vacuum_database()
            elif choice == '5':
                break
            else:
                print("❌ Invalid choice. Please enter 1-5.")
    
    def view_database_info(self):
        """Display database information"""
        conn = sqlite3.connect(self.analyzer.db_path)
        
        try:
            tables = ['log_entries', 'call_records', 'sip_messages', 'registration_events', 'system_events']
            
            print(f"\n🗄️ Database: {self.analyzer.db_path}")
            if os.path.exists(self.analyzer.db_path):
                db_size = os.path.getsize(self.analyzer.db_path)
                print(f"Size: {db_size / 1024 / 1024:.2f} MB")
            
            print("\nTable Statistics:")
            for table in tables:
                count = conn.execute(f"SELECT COUNT(*) FROM {table}").fetchone()[0]
                print(f"  {table}: {count:,} records")
        
        except Exception as e:
            print(f"❌ Error getting database info: {e}")
        
        finally:
            conn.close()
    
    def clear_all_data(self):
        """Clear all data from database"""
        confirm = input("⚠️ Are you sure you want to clear ALL data? (type 'YES' to confirm): ")
        if confirm == 'YES':
            conn = sqlite3.connect(self.analyzer.db_path)
            try:
                tables = ['log_entries', 'call_records', 'sip_messages', 'registration_events', 'system_events', 'call_statistics']
                for table in tables:
                    conn.execute(f"DELETE FROM {table}")
                conn.commit()
                print("✅ All data cleared")
            except Exception as e:
                print(f"❌ Error clearing data: {e}")
            finally:
                conn.close()
        else:
            print("❌ Operation cancelled")
    
    def vacuum_database(self):
        """Vacuum the database"""
        try:
            conn = sqlite3.connect(self.analyzer.db_path)
            conn.execute("VACUUM")
            conn.close()
            print("✅ Database vacuumed")
        except Exception as e:
            print(f"❌ Error vacuuming database: {e}")
    
    def settings_menu(self):
        """Settings submenu"""
        while True:
            print("\n⚙️ SETTINGS")
            print(f"Current database: {self.analyzer.db_path}")
            print(f"Multiprocessing workers: {self.mp_analyzer.max_workers}")
            print()
            print("1. Change database path")
            print("2. Change multiprocessing worker count")
            print("3. View parsing patterns")
            print("4. Test log parsing on sample")
            print("5. Back to main menu")
            
            choice = input("Enter choice (1-5): ").strip()
            
            if choice == '1':
                self.change_database_path()
            elif choice == '2':
                self.change_worker_count()
            elif choice == '3':
                self.view_parsing_patterns()
            elif choice == '4':
                self.test_log_parsing()
            elif choice == '5':
                break
            else:
                print("❌ Invalid choice. Please enter 1-5.")
    
    def change_database_path(self):
        """Change database path"""
        new_db = input(f"Enter new database path (current: {self.analyzer.db_path}): ").strip()
        if new_db:
            self.analyzer.db_path = new_db
            self.analyzer.db.db_path = new_db
            self.analyzer.db.init_database()
            
            self.mp_analyzer.db_path = new_db
            self.mp_analyzer.db.db_path = new_db
            self.mp_analyzer.db.init_database()
            
            print(f"✅ Database path changed to: {new_db}")
    
    def change_worker_count(self):
        """Change multiprocessing worker count"""
        max_workers = mp.cpu_count()
        current = self.mp_analyzer.max_workers
        
        print(f"Current workers: {current}")
        print(f"Available CPU cores: {max_workers}")
        
        new_count = input(f"Enter new worker count (1-{max_workers}, current: {current}): ").strip()
        
        try:
            new_count = int(new_count)
            if 1 <= new_count <= max_workers:
                self.mp_analyzer.max_workers = new_count
                print(f"✅ Worker count changed to: {new_count}")
            else:
                print(f"❌ Invalid count. Must be between 1 and {max_workers}")
        except ValueError:
            print("❌ Invalid number")
    
    def view_parsing_patterns(self):
        """View current parsing patterns"""
        print("\n🔍 Current Parsing Patterns:")
        for name, pattern in self.analyzer.parser.patterns.items():
            print(f"  {name}: {pattern}")
    
    def test_log_parsing(self):
        """Test parsing on a sample line"""
        sample_line = input("Enter a sample log line to test parsing: ").strip()
        if sample_line:
            entry = self.analyzer.parser.parse_log_entry(sample_line)
            if entry:
                print("✅ Parsed successfully:")
                for key, value in entry.items():
                    print(f"  {key}: {value}")
            else:
                print("❌ Failed to parse line")