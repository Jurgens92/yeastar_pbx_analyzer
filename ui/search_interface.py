"""
Search and view interface for PBX data
"""

import sqlite3

class SearchInterface:
    def __init__(self, analyzer):
        self.analyzer = analyzer
    
    def search_call_records(self):
        """Search and display call records"""
        print("\n🔍 SEARCH CALL RECORDS")
        print("Search options:")
        print("1. By caller number")
        print("2. By called number")
        print("3. By disposition")
        print("4. By date range")
        print("5. Recent calls")
        
        choice = input("Enter choice (1-5): ").strip()
        
        conn = sqlite3.connect(self.analyzer.db_path)
        
        try:
            if choice == '1':
                results = self._search_by_caller(conn)
            elif choice == '2':
                results = self._search_by_called(conn)
            elif choice == '3':
                results = self._search_by_disposition(conn)
            elif choice == '4':
                results = self._search_by_date_range(conn)
            elif choice == '5':
                results = self._get_recent_calls(conn)
            else:
                print("❌ Invalid choice")
                return
            
            self._display_call_results(results)
        
        except Exception as e:
            print(f"❌ Search error: {e}")
        
        finally:
            conn.close()
    
    def _search_by_caller(self, conn):
        """Search by caller number"""
        caller = input("Enter caller number: ").strip()
        return conn.execute('''
            SELECT call_datetime, source_number, destination_number, disposition, duration, trunk
            FROM call_records 
            WHERE source_number LIKE ?
            ORDER BY call_datetime DESC LIMIT 20
        ''', (f'%{caller}%',)).fetchall()
    
    def _search_by_called(self, conn):
        """Search by called number"""
        called = input("Enter called number: ").strip()
        return conn.execute('''
            SELECT call_datetime, source_number, destination_number, disposition, duration, trunk
            FROM call_records 
            WHERE destination_number LIKE ?
            ORDER BY call_datetime DESC LIMIT 20
        ''', (f'%{called}%',)).fetchall()
    
    def _search_by_disposition(self, conn):
        """Search by disposition"""
        disposition = input("Enter disposition (ANSWERED/NO ANSWER/BUSY/etc.): ").strip()
        return conn.execute('''
            SELECT call_datetime, source_number, destination_number, disposition, duration, trunk
            FROM call_records 
            WHERE disposition = ?
            ORDER BY call_datetime DESC LIMIT 20
        ''', (disposition,)).fetchall()
    
    def _search_by_date_range(self, conn):
        """Search by date range"""
        start_date = input("Enter start date (YYYY-MM-DD): ").strip()
        end_date = input("Enter end date (YYYY-MM-DD): ").strip()
        return conn.execute('''
            SELECT call_datetime, source_number, destination_number, disposition, duration, trunk
            FROM call_records 
            WHERE DATE(call_datetime) BETWEEN ? AND ?
            ORDER BY call_datetime DESC LIMIT 50
        ''', (start_date, end_date)).fetchall()
    
    def _get_recent_calls(self, conn):
        """Get recent calls"""
        return conn.execute('''
            SELECT call_datetime, source_number, destination_number, disposition, duration, trunk
            FROM call_records 
            ORDER BY call_datetime DESC LIMIT 20
        ''').fetchall()
    
    def _display_call_results(self, results):
        """Display call search results"""
        if results:
            print(f"\n📞 Found {len(results)} call records:")
            print("-" * 80)
            print(f"{'DateTime':<20} {'From':<15} {'To':<15} {'Status':<12} {'Duration':<8} {'Trunk':<10}")
            print("-" * 80)
            
            for record in results:
                datetime_str, source, dest, disp, duration, trunk = record
                print(f"{datetime_str:<20} {source:<15} {dest:<15} {disp:<12} {duration:<8} {trunk:<10}")
        else:
            print("❌ No records found")
    
    def view_call_statistics(self):
        """View call statistics"""
        print("\n📈 CALL STATISTICS")
        
        conn = sqlite3.connect(self.analyzer.db_path)
        
        try:
            # Overall statistics
            overall_stats = conn.execute('''
                SELECT 
                    COUNT(*) as total_calls,
                    SUM(CASE WHEN disposition = 'ANSWERED' THEN 1 ELSE 0 END) as answered,
                    SUM(CASE WHEN disposition = 'NO ANSWER' THEN 1 ELSE 0 END) as missed,
                    SUM(CASE WHEN disposition = 'BUSY' THEN 1 ELSE 0 END) as busy,
                    AVG(CASE WHEN disposition = 'ANSWERED' THEN duration END) as avg_duration,
                    MAX(duration) as max_duration,
                    COUNT(DISTINCT source_number) as unique_callers
                FROM call_records
            ''').fetchone()
            
            if overall_stats and overall_stats[0] > 0:
                total, answered, missed, busy, avg_dur, max_dur, unique = overall_stats
                
                print("\n📊 Overall Call Statistics:")
                print(f"Total Calls: {total:,}")
                print(f"Answered: {answered:,} ({answered/total*100:.1f}%)")
                print(f"Missed: {missed:,} ({missed/total*100:.1f}%)")
                print(f"Busy: {busy:,} ({busy/total*100:.1f}%)")
                print(f"Average Duration: {avg_dur or 0:.1f} seconds")
                print(f"Maximum Duration: {max_dur or 0:,} seconds")
                print(f"Unique Callers: {unique:,}")
                
                # Top callers
                self._show_top_callers(conn)
                
                # Busiest hours
                self._show_busiest_hours(conn)
            
            else:
                print("❌ No call statistics available")
        
        except Exception as e:
            print(f"❌ Error retrieving statistics: {e}")
        
        finally:
            conn.close()
    
    def _show_top_callers(self, conn):
        """Show top callers"""
        print("\n📞 Top 10 Callers:")
        top_callers = conn.execute('''
            SELECT source_number, COUNT(*) as call_count, 
                   SUM(CASE WHEN disposition = 'ANSWERED' THEN 1 ELSE 0 END) as answered_count
            FROM call_records 
            GROUP BY source_number 
            ORDER BY call_count DESC 
            LIMIT 10
        ''').fetchall()
        
        for caller, count, answered in top_callers:
            success_rate = (answered / count * 100) if count > 0 else 0
            print(f"  {caller:<15} {count:>4} calls ({success_rate:.1f}% answered)")
    
    def _show_busiest_hours(self, conn):
        """Show busiest hours"""
        print("\n🕐 Busiest Hours:")
        busy_hours = conn.execute('''
            SELECT CAST(strftime('%H', call_datetime) AS INTEGER) as hour, 
                   COUNT(*) as call_count
            FROM call_records 
            WHERE call_datetime != ''
            GROUP BY hour 
            ORDER BY call_count DESC 
            LIMIT 10
        ''').fetchall()
        
        for hour, count in busy_hours:
            print(f"  {hour:02d}:00 - {count:,} calls")
    
    def view_registration_events(self):
        """View registration events"""
        print("\n🔐 REGISTRATION EVENTS")
        
        conn = sqlite3.connect(self.analyzer.db_path)
        
        try:
            # Recent registration events
            recent_events = conn.execute('''
                SELECT timestamp, event_type, server_uri, client_uri, response_code, response_text
                FROM registration_events 
                ORDER BY timestamp DESC 
                LIMIT 20
            ''').fetchall()
            
            if recent_events:
                print("\nRecent Registration Events:")
                print("-" * 100)
                print(f"{'Timestamp':<20} {'Type':<10} {'Server':<25} {'Client':<25} {'Code':<6} {'Response'}")
                print("-" * 100)
                
                for event in recent_events:
                    timestamp, event_type, server, client, code, response = event
                    print(f"{timestamp:<20} {event_type:<10} {server or 'N/A':<25} {client or 'N/A':<25} {code or '':<6} {response or ''}")
            
            # Registration statistics
            reg_stats = conn.execute('''
                SELECT event_type, COUNT(*) as count
                FROM registration_events 
                GROUP BY event_type
            ''').fetchall()
            
            if reg_stats:
                print("\n📊 Registration Summary:")
                for event_type, count in reg_stats:
                    print(f"  {event_type}: {count:,}")
            
            if not recent_events and not reg_stats:
                print("❌ No registration events found")
        
        except Exception as e:
            print(f"❌ Error retrieving registration events: {e}")
        
        finally:
            conn.close()
    
    def view_system_events(self):
        """View system events"""
        print("\n⚠️ SYSTEM EVENTS")
        
        conn = sqlite3.connect(self.analyzer.db_path)
        
        try:
            # Recent system events
            recent_events = conn.execute('''
                SELECT timestamp, event_type, category, description, error_code
                FROM system_events 
                ORDER BY timestamp DESC 
                LIMIT 30
            ''').fetchall()
            
            if recent_events:
                print("\nRecent System Events:")
                print("-" * 120)
                print(f"{'Timestamp':<20} {'Type':<8} {'Category':<12} {'Description':<60} {'Code'}")
                print("-" * 120)
                
                for event in recent_events:
                    timestamp, event_type, category, description, error_code = event
                    desc_short = description[:60] + "..." if len(description) > 60 else description
                    print(f"{timestamp:<20} {event_type:<8} {category:<12} {desc_short:<60} {error_code or ''}")
            
            # Error summary
            error_summary = conn.execute('''
                SELECT category, COUNT(*) as count
                FROM system_events 
                WHERE event_type = 'ERROR'
                GROUP BY category 
                ORDER BY count DESC
            ''').fetchall()
            
            if error_summary:
                print("\n🚨 Error Summary by Category:")
                for category, count in error_summary:
                    print(f"  {category}: {count:,} errors")
            
            if not recent_events:
                print("❌ No system events found")
        
        except Exception as e:
            print(f"❌ Error retrieving system events: {e}")
        
        finally:
            conn.close()