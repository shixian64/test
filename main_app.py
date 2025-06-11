#!/usr/bin/env python3
"""
Android Log Analyzer - Main Application Entry Point

This is the main entry point for the Windows executable version.
It provides both GUI and CLI interfaces.
"""

import sys
import os
import threading
import subprocess
from pathlib import Path
import json

# Try to import GUI components
GUI_AVAILABLE = True
try:
    import tkinter as tk
    from tkinter import ttk, filedialog, messagebox, scrolledtext
except ImportError:
    GUI_AVAILABLE = False
    print("Warning: GUI components not available. Running in CLI-only mode.")

# Add the current directory to Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

try:
    from android_log_analyzer import read_log_file, generate_report, get_structured_report_data
    from android_log_analyzer.config import ConfigManager
    from android_log_analyzer.utils import PerformanceMonitor
    ANALYZER_AVAILABLE = True
except ImportError as e:
    print(f"Warning: Could not import analyzer: {e}")
    ANALYZER_AVAILABLE = False


class AndroidLogAnalyzerGUI:
    """Simple GUI for Android Log Analyzer"""
    
    def __init__(self, root):
        self.root = root
        self.root.title("Android Log Analyzer v0.2.0")
        self.root.geometry("800x600")
        
        # Configure style
        style = ttk.Style()
        style.theme_use('clam')
        
        self.setup_ui()
        self.current_file = None
        self.analysis_results = None
        
    def setup_ui(self):
        """Setup the user interface"""
        # Main frame
        main_frame = ttk.Frame(self.root, padding="10")
        main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # Configure grid weights
        self.root.columnconfigure(0, weight=1)
        self.root.rowconfigure(0, weight=1)
        main_frame.columnconfigure(1, weight=1)
        main_frame.rowconfigure(2, weight=1)
        
        # Title
        title_label = ttk.Label(main_frame, text="Android Log Analyzer", 
                               font=('Arial', 16, 'bold'))
        title_label.grid(row=0, column=0, columnspan=3, pady=(0, 20))
        
        # File selection
        ttk.Label(main_frame, text="Log File:").grid(row=1, column=0, sticky=tk.W, pady=5)
        
        self.file_var = tk.StringVar()
        file_entry = ttk.Entry(main_frame, textvariable=self.file_var, width=50)
        file_entry.grid(row=1, column=1, sticky=(tk.W, tk.E), padx=(5, 5), pady=5)
        
        browse_btn = ttk.Button(main_frame, text="Browse", command=self.browse_file)
        browse_btn.grid(row=1, column=2, padx=(5, 0), pady=5)
        
        # Action buttons
        button_frame = ttk.Frame(main_frame)
        button_frame.grid(row=2, column=0, columnspan=3, sticky=(tk.W, tk.E), pady=10)
        
        analyze_btn = ttk.Button(button_frame, text="Analyze Log", 
                                command=self.analyze_log, style='Accent.TButton')
        analyze_btn.pack(side=tk.LEFT, padx=(0, 10))
        
        export_btn = ttk.Button(button_frame, text="Export JSON", 
                               command=self.export_json)
        export_btn.pack(side=tk.LEFT, padx=(0, 10))
        
        clear_btn = ttk.Button(button_frame, text="Clear", command=self.clear_results)
        clear_btn.pack(side=tk.LEFT)
        
        # Results area
        results_frame = ttk.LabelFrame(main_frame, text="Analysis Results", padding="5")
        results_frame.grid(row=3, column=0, columnspan=3, sticky=(tk.W, tk.E, tk.N, tk.S), pady=10)
        results_frame.columnconfigure(0, weight=1)
        results_frame.rowconfigure(0, weight=1)
        
        self.results_text = scrolledtext.ScrolledText(results_frame, wrap=tk.WORD, 
                                                     width=80, height=25)
        self.results_text.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # Status bar
        self.status_var = tk.StringVar()
        self.status_var.set("Ready")
        status_bar = ttk.Label(main_frame, textvariable=self.status_var, 
                              relief=tk.SUNKEN, anchor=tk.W)
        status_bar.grid(row=4, column=0, columnspan=3, sticky=(tk.W, tk.E), pady=(10, 0))
        
        # Menu bar
        self.setup_menu()
        
    def setup_menu(self):
        """Setup menu bar"""
        menubar = tk.Menu(self.root)
        self.root.config(menu=menubar)
        
        # File menu
        file_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="File", menu=file_menu)
        file_menu.add_command(label="Open Log File...", command=self.browse_file)
        file_menu.add_separator()
        file_menu.add_command(label="Export Results...", command=self.export_json)
        file_menu.add_separator()
        file_menu.add_command(label="Exit", command=self.root.quit)
        
        # Tools menu
        tools_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="Tools", menu=tools_menu)
        tools_menu.add_command(label="Open Command Line", command=self.open_cli)
        tools_menu.add_command(label="Settings", command=self.show_settings)
        
        # Help menu
        help_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="Help", menu=help_menu)
        help_menu.add_command(label="About", command=self.show_about)
        
    def browse_file(self):
        """Browse for log file"""
        filetypes = [
            ("Log files", "*.log *.txt"),
            ("Compressed files", "*.gz *.zip"),
            ("All files", "*.*")
        ]
        
        filename = filedialog.askopenfilename(
            title="Select Android Log File",
            filetypes=filetypes
        )
        
        if filename:
            self.file_var.set(filename)
            self.current_file = filename
            self.status_var.set(f"Selected: {os.path.basename(filename)}")
    
    def analyze_log(self):
        """Analyze the selected log file"""
        if not self.current_file or not os.path.exists(self.current_file):
            messagebox.showerror("Error", "Please select a valid log file first.")
            return
        
        if not ANALYZER_AVAILABLE:
            messagebox.showerror("Error", "Log analyzer is not available.")
            return
        
        # Run analysis in a separate thread to avoid blocking UI
        self.status_var.set("Analyzing...")
        self.results_text.delete(1.0, tk.END)
        self.results_text.insert(tk.END, "Analyzing log file, please wait...\n")
        
        thread = threading.Thread(target=self._run_analysis)
        thread.daemon = True
        thread.start()
    
    def _run_analysis(self):
        """Run the actual analysis (in background thread)"""
        try:
            # Perform analysis
            issues = read_log_file(self.current_file)
            self.analysis_results = get_structured_report_data(issues)
            
            # Update UI in main thread
            self.root.after(0, self._display_results, issues)
            
        except Exception as e:
            error_msg = f"Analysis failed: {str(e)}"
            self.root.after(0, self._display_error, error_msg)
    
    def _display_results(self, issues):
        """Display analysis results"""
        self.results_text.delete(1.0, tk.END)
        
        if not issues:
            self.results_text.insert(tk.END, "✅ No issues found in the log file.\n")
            self.status_var.set("Analysis complete - No issues found")
            return
        
        # Display summary
        summary = self.analysis_results.get("summary_counts", {})
        self.results_text.insert(tk.END, "📊 ANALYSIS SUMMARY\n")
        self.results_text.insert(tk.END, "=" * 50 + "\n")
        
        total_issues = sum(summary.values())
        self.results_text.insert(tk.END, f"Total Issues Found: {total_issues}\n\n")
        
        for issue_type, count in summary.items():
            self.results_text.insert(tk.END, f"  {issue_type}: {count}\n")
        
        self.results_text.insert(tk.END, "\n" + "=" * 50 + "\n\n")
        
        # Display detailed issues
        self.results_text.insert(tk.END, "🔍 DETAILED ISSUES\n")
        self.results_text.insert(tk.END, "=" * 50 + "\n\n")
        
        for i, issue in enumerate(issues, 1):
            issue_type = issue.get("type", "Unknown")
            trigger = issue.get("trigger_line_str", "No details available")
            
            self.results_text.insert(tk.END, f"Issue #{i}: {issue_type}\n")
            self.results_text.insert(tk.END, f"Details: {trigger}\n")
            
            # Add specific details based on issue type
            if issue_type == "ANR" and "process_name" in issue:
                self.results_text.insert(tk.END, f"Process: {issue['process_name']}\n")
            elif issue_type == "MemoryIssue" and "oom_reason" in issue:
                self.results_text.insert(tk.END, f"Reason: {issue['oom_reason']}\n")
            elif issue_type == "NativeCrashHint" and "signal_info" in issue:
                self.results_text.insert(tk.END, f"Signal: {issue['signal_info']}\n")
            
            self.results_text.insert(tk.END, "\n" + "-" * 40 + "\n\n")
        
        self.status_var.set(f"Analysis complete - {total_issues} issues found")
    
    def _display_error(self, error_msg):
        """Display error message"""
        self.results_text.delete(1.0, tk.END)
        self.results_text.insert(tk.END, f"❌ {error_msg}\n")
        self.status_var.set("Analysis failed")
    
    def export_json(self):
        """Export results to JSON"""
        if not self.analysis_results:
            messagebox.showwarning("Warning", "No analysis results to export.")
            return
        
        filename = filedialog.asksaveasfilename(
            title="Save Analysis Results",
            defaultextension=".json",
            filetypes=[("JSON files", "*.json"), ("All files", "*.*")]
        )
        
        if filename:
            try:
                with open(filename, 'w', encoding='utf-8') as f:
                    json.dump(self.analysis_results, f, indent=2, ensure_ascii=False)
                
                messagebox.showinfo("Success", f"Results exported to {filename}")
                self.status_var.set(f"Exported to {os.path.basename(filename)}")
                
            except Exception as e:
                messagebox.showerror("Error", f"Failed to export: {str(e)}")
    
    def clear_results(self):
        """Clear analysis results"""
        self.results_text.delete(1.0, tk.END)
        self.analysis_results = None
        self.status_var.set("Ready")
    
    def open_cli(self):
        """Open command line interface"""
        try:
            if sys.platform.startswith('win'):
                subprocess.Popen(['cmd', '/k', 'echo Android Log Analyzer CLI Mode'])
            else:
                subprocess.Popen(['gnome-terminal', '--', 'bash'])
        except Exception as e:
            messagebox.showerror("Error", f"Failed to open CLI: {str(e)}")
    
    def show_settings(self):
        """Show settings dialog"""
        messagebox.showinfo("Settings", "Settings functionality coming soon!")
    
    def show_about(self):
        """Show about dialog"""
        about_text = """Android Log Analyzer v0.2.0

A comprehensive toolkit for analyzing Android logcat files.

Features:
• Java crash detection
• ANR analysis  
• Native crash detection
• Memory issue analysis
• System error detection

© 2024 Android Log Analyzer Team"""
        
        messagebox.showinfo("About", about_text)


def main():
    """Main application entry point"""
    # Check if running with command line arguments
    if len(sys.argv) > 1:
        # CLI mode
        if not ANALYZER_AVAILABLE:
            print("Error: Log analyzer is not available.")
            sys.exit(1)

        # Import and run CLI
        from android_log_analyzer.log_analyzer import main as cli_main
        cli_main()
    else:
        # GUI mode
        if not GUI_AVAILABLE:
            print("GUI components not available.")
            print("Please install tkinter or run with command line arguments:")
            print(f"  {sys.argv[0]} <log_file>")
            sys.exit(1)

        if not ANALYZER_AVAILABLE:
            print("Error: Log analyzer is not available.")
            sys.exit(1)

        root = tk.Tk()
        app = AndroidLogAnalyzerGUI(root)

        # Center window on screen
        root.update_idletasks()
        x = (root.winfo_screenwidth() // 2) - (root.winfo_width() // 2)
        y = (root.winfo_screenheight() // 2) - (root.winfo_height() // 2)
        root.geometry(f"+{x}+{y}")

        try:
            root.mainloop()
        except KeyboardInterrupt:
            pass


if __name__ == "__main__":
    main()
