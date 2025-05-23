# Android Log Analyzer GUI

A user-friendly graphical interface for the Android Log Analyzer tool, built with Electron and Python (using the Eel library). This application allows users to easily select Android log files, analyze them for common issues, and view the results in a structured format.

## Features

*   **Graphical User Interface:** Easy-to-use interface for selecting log files and viewing analysis results.
*   **Core Analysis Engine:** Utilizes the same robust Python-based analysis logic from the [command-line version](../android_log_analyzer/README.md) to detect:
    *   Java Crashes
    *   Application Not Responding (ANR) errors
    *   Native Crash Hints
    *   Kernel Panics, Watchdog resets, and other critical system errors
*   **Structured Results Display:**
    *   Summary counts of detected issue types.
    *   A detailed, filterable list of all issues found.
    *   A modal view to inspect the full details of each specific issue.
*   **Cross-Platform:** Designed to be packaged for Linux (AppImage, .deb) and Windows (.exe). *(Builds should be verified)*

## Screenshots

*(Placeholder: Add screenshots of the application here once available.)*

1.  **Main Application Window (File Selection):**
    *   *(Description: Shows the initial view for selecting a log file.)*
    *   `[Screenshot_Main_Window.png]`

2.  **Analysis Results View (Summary and Table):**
    *   *(Description: Shows the results screen with summary statistics and the table of detected issues.)*
    *   `[Screenshot_Results_View.png]`

3.  **Issue Detail Modal:**
    *   *(Description: Shows the modal dialog displaying the full details of a selected issue.)*
    *   `[Screenshot_Detail_Modal.png]`

## Requirements

### For Using Packaged Application
*   **Linux:** AppImage or .deb package. No external dependencies required.
*   **Windows:** NSIS Installer (.exe). No external dependencies required.
    *(Note: Download packages from the project's Releases page - link would go here.)*

### For Running from Source (Development)
*   Python 3.7+
    *   `eel` library (`pip install eel`)
*   Node.js (which includes npm) LTS version recommended.
*   Access to the core `android_log_analyzer` module (expected to be in a sibling directory `../android_log_analyzer`).

## Installation and Usage

### Using Packaged Application
1.  Download the appropriate package for your system (e.g., `.AppImage` for Linux, `.exe` installer for Windows) from the project's releases.
2.  **Linux (AppImage):**
    *   Make the AppImage executable: `chmod +x Android_Log_Analyzer_GUI-x.y.z.AppImage`
    *   Run it: `./Android_Log_Analyzer_GUI-x.y.z.AppImage`
3.  **Windows (Installer):**
    *   Run the `.exe` installer and follow the on-screen instructions.
    *   Launch the application from the Start Menu or desktop shortcut.

### Running from Source (Development)
1.  **Clone the repository (or ensure you have both `log_analyzer_gui` and `android_log_analyzer` directories).**
    ```bash
    # git clone ... (if it were a git repo)
    # Ensure both project folders are present.
    ```
2.  **Navigate to the GUI project directory:**
    ```bash
    cd path/to/log_analyzer_gui
    ```
3.  **Install Node.js dependencies:**
    ```bash
    npm install
    ```
4.  **Install Python dependencies:**
    ```bash
    pip install eel
    ```
5.  **Run the application:**
    ```bash
    npm start
    ```
    This will launch the Electron application. The Python Eel server will be started automatically by the Electron main process.

## Building from Source

To create distributable packages (AppImage, deb, exe), use `electron-builder`.

1.  Ensure all development dependencies are installed (`npm install`).
2.  Run the build command from the `log_analyzer_gui` directory:
    ```bash
    npm run build
    ```
3.  The packaged applications will be located in the `log_analyzer_gui/dist` directory.

## Project Structure (Key Files)

*   `log_analyzer_gui/`: Root directory for the GUI application.
    *   `main_gui.py`: The Python backend script using Eel to bridge with JavaScript and the core analyzer.
    *   `electron_bootstrap.js`: The main Electron process script that creates the browser window and manages the Python subprocess.
    *   `package.json`: Defines Node.js dependencies, scripts (start, build), and `electron-builder` configuration.
    *   `web/`: Contains the frontend files (HTML, CSS, JavaScript).
        *   `main.html`: The main HTML page for the UI.
        *   `script.js`: Frontend JavaScript logic.
        *   `style.css`: CSS styles.
    *   `build_assets/`: Contains assets like icons used for packaging.
*   `../android_log_analyzer/`: (Assumed Sibling Directory) Contains the core Python log analysis logic.
    *   `log_analyzer.py`: The main script for parsing and analyzing logs.
    *   `__init__.py`: Makes this directory a Python package.

```
