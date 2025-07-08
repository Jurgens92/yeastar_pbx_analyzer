#!/usr/bin/env python3
"""
Yeastar PBX Log Analysis Tool - Main Entry Point
"""

import sys
from ui.menu_system import MainMenu
from core.analyzer import YeastarLogAnalyzer

def print_banner():
    """Print application banner"""
    print("""
╔══════════════════════════════════════════════════════════════╗
║                    YEASTAR PBX LOG ANALYZER                  ║
║                                                              ║
║  • Parse PBX log files (pbxlog.0)                            ║
║  • Extract call records, SIP messages, registrations         ║
║  • SQLite database storage and analysis                      ║
║  • Generate comprehensive HTML reports                       ║
║  • Search and filter call data                               ║
║                                                              ║
╚══════════════════════════════════════════════════════════════╝
    """)

def main():
    print_banner()
    
    # Check for command line arguments
    if len(sys.argv) > 1:
        analyzer = YeastarLogAnalyzer()
        
        if sys.argv[1] == '--parse' and len(sys.argv) > 2:
            analyzer.parse_log_file(sys.argv[2])
        elif sys.argv[1] == '--report':
            output = sys.argv[2] if len(sys.argv) > 2 else "pbx_analysis_report.html"
            analyzer.generate_html_report(output)
        else:
            print("Usage:")
            print("  python main.py --parse <logfile>")
            print("  python main.py --report [output.html]")
    else:
        # Interactive mode
        menu = MainMenu()
        menu.run()

if __name__ == "__main__":
    main()
