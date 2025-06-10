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
    from android_log_analyzer.log_analyzer import read_log_file, get_structured_report_data, ISSUE_PATTERNS, smart_search_logs, prioritize_issues
    from android_log_analyzer.advanced_parser import AdvancedLogParser
    from android_log_analyzer.sprd_analyzer import SPRDLogAnalyzer
    from pathlib import Path

    # Try to import intelligent features
    try:
        from android_log_analyzer.intelligent.smart_search import SmartSearchEngine
        from android_log_analyzer.intelligent.priority_scorer import IssuePriorityScorer
        from android_log_analyzer.intelligent.report_generator import IntelligentReportGenerator
        INTELLIGENT_FEATURES_AVAILABLE = True
        print("Successfully imported 'log_analyzer' components, advanced analyzers, and intelligent features.")
    except ImportError as ie:
        INTELLIGENT_FEATURES_AVAILABLE = False
        print(f"Intelligent features not available: {ie}")
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

    # Enhance with intelligent features
    enhanced_analysis_data = enhance_analysis_with_intelligent_features(structured_report_output)

    return {
        "status": "success",
        "message": message,
        "analysis_data": enhanced_analysis_data
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

        # Enhance with intelligent features
        enhanced_analysis_result = enhance_analysis_with_intelligent_features(analysis_result)

        return {
            "status": "success",
            "message": message,
            "analysis_data": enhanced_analysis_result
        }

    except Exception as e:
        print(f"Python: Error in advanced analysis: {e}")
        import traceback
        traceback.print_exc()

        # Fallback to standard analysis
        print(f"Python: Falling back to standard analysis")
        return perform_standard_analysis(filename, temp_file_path, "")


@eel.expose
def smart_search_logs_py(query, log_files):
    """
    Perform intelligent search across log files

    Args:
        query: Search query string
        log_files: List of log file paths (currently not used in GUI)

    Returns:
        List of search results with relevance scoring
    """
    print(f"Python: Smart search request for query: '{query}'")

    if not INTELLIGENT_FEATURES_AVAILABLE:
        print("Python: Intelligent features not available, returning empty results")
        return []

    try:
        # For GUI, we'll search in the current analysis data
        # This is a simplified implementation - in a full version,
        # we would search across actual log files

        search_engine = SmartSearchEngine()

        # Mock search results for demonstration
        # In a real implementation, this would search actual log content
        mock_results = [
            {
                'file': 'current_analysis.log',
                'line_number': 1,
                'content': f'Mock search result for query: {query}',
                'relevance_score': 0.95,
                'match_type': 'semantic',
                'highlights': [[0, len(query)]]
            }
        ]

        print(f"Python: Smart search completed, found {len(mock_results)} results")
        return mock_results

    except Exception as e:
        print(f"Python: Error in smart search: {e}")
        return []


@eel.expose
def get_intelligent_features_status():
    """
    Get the status of intelligent features

    Returns:
        Dictionary with feature availability status
    """
    return {
        'available': INTELLIGENT_FEATURES_AVAILABLE,
        'features': {
            'smart_search': INTELLIGENT_FEATURES_AVAILABLE,
            'priority_scoring': INTELLIGENT_FEATURES_AVAILABLE,
            'report_generation': INTELLIGENT_FEATURES_AVAILABLE
        }
    }


def enhance_analysis_with_intelligent_features(analysis_data):
    """
    Enhance analysis data with intelligent features if available

    Args:
        analysis_data: Original analysis data

    Returns:
        Enhanced analysis data with intelligent features
    """
    if not INTELLIGENT_FEATURES_AVAILABLE:
        return analysis_data

    try:
        # Add priority scoring to issues
        if 'detailed_issues' in analysis_data:
            prioritized_issues = prioritize_issues(analysis_data['detailed_issues'])
            analysis_data['detailed_issues'] = prioritized_issues

        # Add intelligent features flag
        analysis_data['intelligent_features_enabled'] = True

        print("Python: Analysis enhanced with intelligent features")

    except Exception as e:
        print(f"Python: Error enhancing analysis with intelligent features: {e}")
        analysis_data['intelligent_features_enabled'] = False

    return analysis_data

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
