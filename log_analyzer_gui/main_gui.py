import eel
import os
import time
import tempfile # For saving content to a temporary file
import sys
import platform # To help determine executable name for Python

# --- Path adjustments for packaged app ---
script_root_dir = os.path.dirname(os.path.realpath(__file__))
# In packaged app (by electron-builder), main_gui.py and android_log_analyzer/ are siblings.
# In dev, the original android_log_analyzer is one level up from log_analyzer_gui.

# A common way to check if running packaged is to see if 'app.asar' is in the path of the app.
# However, electron-is-dev sets an ENV var that Python can check if passed through.
# For this setup, we rely on electron-builder placing files as per 'extraResources'.
# 'main_gui.py' will be at 'resources/app/main_gui.py'
# 'log_analyzer.py' will be at 'resources/app/android_log_analyzer/log_analyzer.py'

# The directory containing main_gui.py (which is 'resources/app/')
# This becomes the base for finding the 'android_log_analyzer' subdirectory.
base_path_for_module = script_root_dir

# Add this base_path_for_module to sys.path so that 'android_log_analyzer' package can be found.
# If main_gui.py is 'resources/app/main_gui.py', then 'resources/app' is added.
sys.path.insert(0, base_path_for_module)

try:
    # Now, Python should be able to find the 'android_log_analyzer' package
    # (because 'android_log_analyzer/__init__.py' makes it a package, and it's a subdir)
    from android_log_analyzer.log_analyzer import read_log_file, get_structured_report_data, ISSUE_PATTERNS
    from android_log_analyzer.advanced_parser import AdvancedLogParser
    from android_log_analyzer.sprd_analyzer import SPRDLogAnalyzer
    print("Successfully imported 'log_analyzer' components and advanced analyzers.")
except ImportError as e:
    print(f"Error importing 'log_analyzer': {e}. Check paths and structure.")
    print(f"Current sys.path: {sys.path}")
    print(f"Expected module location: {os.path.join(base_path_for_module, 'android_log_analyzer')}")
    # Define dummy functions if import fails, so UI can still be tested partially
    def read_log_file(filepath, patterns): return [{"type": "ImportError", "trigger_line": str(e)}]
    def get_structured_report_data(issues): 
        return {
            "summary_counts": {"ImportError": 1}, 
            "detailed_issues": [{"type": "ImportError", "trigger_line_str": f"Import Error: {e}. Check logs."}]
        }
    ISSUE_PATTERNS = {}
# --- End of path addition ---


web_folder = os.path.join(script_root_dir, 'web') # 'web' folder is sibling to main_gui.py in dev, and copied by 'files' in build
eel.init(web_folder)

def is_complex_log_package(filename):
    """Check if the file is a complex log package (zip/tar) that needs advanced analysis"""
    return (filename.lower().endswith(('.zip', '.tar', '.tar.gz', '.tgz')) or
            'ylog' in filename.lower() or
            any(keyword in filename.lower() for keyword in ['sprd', 'unisoc', 'log_package']))

@eel.expose
def start_analysis_py(filename, file_content_string):
    print(f"Python: Received file '{filename}'. Content length: {len(file_content_string)} bytes.")

    temp_file_path = ""
    try:
        # Determine file extension for proper handling
        file_extension = os.path.splitext(filename)[1].lower()
        if file_extension in ['.zip', '.tar', '.gz']:
            # Handle binary files differently
            suffix = file_extension
            mode = 'wb'
            file_content = file_content_string.encode('utf-8') if isinstance(file_content_string, str) else file_content_string
        else:
            suffix = ".log"
            mode = 'w+'
            file_content = file_content_string

        try:
            # Try to use a 'temp_files' subdir relative to script_root_dir
            app_temp_dir = os.path.join(script_root_dir, "temp_files")
            os.makedirs(app_temp_dir, exist_ok=True)
            with tempfile.NamedTemporaryFile(mode=mode, delete=False,
                                           encoding='utf-8' if mode.startswith('w') else None,
                                           errors='ignore' if mode.startswith('w') else None,
                                           dir=app_temp_dir, suffix=suffix) as tmp_file:
                tmp_file.write(file_content)
                temp_file_path = tmp_file.name
        except Exception as e_custom_temp:
            print(f"Could not use custom temp dir '{app_temp_dir}': {e_custom_temp}. Falling back to default temp dir.")
            with tempfile.NamedTemporaryFile(mode=mode, delete=False,
                                           encoding='utf-8' if mode.startswith('w') else None,
                                           errors='ignore' if mode.startswith('w') else None,
                                           suffix=suffix) as tmp_file:
                tmp_file.write(file_content)
                temp_file_path = tmp_file.name

        print(f"Python: Content written to temporary file: {temp_file_path}")

        # Check if this needs advanced analysis
        if is_complex_log_package(filename):
            print(f"Python: Detected complex log package, using advanced analysis")
            return perform_advanced_analysis(filename, temp_file_path)
        else:
            print(f"Python: Using standard analysis")
            return perform_standard_analysis(filename, temp_file_path, file_content_string)

    except Exception as e:
        print(f"Python: Error during analysis of {filename}: {e}")
        import traceback
        traceback.print_exc()
        return {"status": "error", "message": f"Error during analysis: {str(e)}"}
    finally:
        if temp_file_path and os.path.exists(temp_file_path):
            os.remove(temp_file_path)
            print(f"Python: Temporary file {temp_file_path} removed.")

def perform_standard_analysis(filename, temp_file_path, file_content_string):
    """Perform standard single-file analysis"""
    detected_issues = read_log_file(temp_file_path, ISSUE_PATTERNS)

    if not file_content_string.strip() and not detected_issues:
         return {"status": "error", "message": f"File '{filename}' is empty or contains only whitespace."}

    structured_report_output = get_structured_report_data(detected_issues)

    message = f"Analysis of {filename} complete."
    if not detected_issues:
        message = f"Analysis of {filename} complete. No issues detected."
    else:
        total_issues_found = sum(structured_report_output.get("summary_counts", {}).values())
        message = f"Analysis of {filename} complete. Issues found: {total_issues_found}"

    print(f"Python: {message}")

    return {
        "status": "success",
        "message": message,
        "analysis_data": structured_report_output
    }

def perform_advanced_analysis(filename, temp_file_path):
    """Perform advanced analysis for complex log packages"""
    try:
        # Determine which analyzer to use
        if 'ylog' in filename.lower() or any(keyword in filename.lower() for keyword in ['sprd', 'unisoc']):
            analyzer = SPRDLogAnalyzer()
            analysis_result = analyzer.analyze_sprd_package(Path(temp_file_path))
        else:
            analyzer = AdvancedLogParser()
            analysis_result = analyzer.analyze_log_package(Path(temp_file_path))

        # Calculate total issues
        total_issues = 0
        if 'subsystem_analysis' in analysis_result:
            for subsystem_data in analysis_result['subsystem_analysis'].values():
                total_issues += len(subsystem_data.get('issues', []))
        elif 'detailed_issues' in analysis_result:
            total_issues = len(analysis_result['detailed_issues'])

        # Add critical issues count
        critical_issues = len(analysis_result.get('critical_issues', []))

        message = f"Advanced analysis of {filename} complete. "
        if total_issues == 0:
            message += "No issues detected."
        else:
            message += f"Issues found: {total_issues}"
            if critical_issues > 0:
                message += f" (including {critical_issues} critical)"

        print(f"Python: {message}")

        return {
            "status": "success",
            "message": message,
            "analysis_data": analysis_result
        }

    except Exception as e:
        print(f"Python: Error in advanced analysis: {e}")
        import traceback
        traceback.print_exc()

        # Fallback to standard analysis
        print(f"Python: Falling back to standard analysis")
        return perform_standard_analysis(filename, temp_file_path, "")

if __name__ == '__main__':
    try:
        eel.start('main.html', size=(800, 700), block=True, port=8000)
    except OSError as e: 
        if "Address already in use" in str(e) or "EADDRINUSE" in str(e): # Check for EADDRINUSE too
            print(f"Error: Port 8000 is already in use. Please close the other application or specify a different port.")
        else:
            print(f"Could not start Eel (OS Error): {e}")
    except Exception as e: 
        print(f"Could not start Eel: {e}")
        import traceback
        traceback.print_exc()
