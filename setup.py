from setuptools import setup, find_packages

setup(
    name="android_log_analyzer",
    version="0.1.0",
    packages=find_packages(),
    entry_points={
        "console_scripts": [
            "android-log-analyzer=android_log_analyzer.log_analyzer:main",
        ]
    },
)
