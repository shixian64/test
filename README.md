# Android Log Analyzer Project

This repository contains a small toolkit for inspecting Android logcat files.
It includes a reusable Python library, a command line interface and a simple
Electron based GUI.

## Usage

### Command line
Install the package in editable mode and run the analyzer:

```bash
pip install -e .
android-log-analyzer path/to/logcat.log
```

You can also provide a directory instead of a single file. The analyzer
will recursively scan for `.log`, `.txt`, `.gz` and `.zip` files.

To also save the results as JSON, specify an output file:

```bash
android-log-analyzer path/to/logcat.log --json-output report.json
```

### GUI
To start the GUI you need `node` and the Python `eel` package.
From the `log_analyzer_gui` directory run:

```bash
npm install
npm start
```

## Running tests

The analyser has a small unit test suite:

```bash
python -m unittest android_log_analyzer.test_log_analyzer
```
