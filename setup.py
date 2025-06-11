from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setup(
    name="android_log_analyzer",
    version="0.2.0",
    author="Android Log Analyzer Team",
    author_email="team@example.com",
    description="A toolkit for analyzing Android logcat files",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/example/android-log-analyzer",
    packages=find_packages(),
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Topic :: Software Development :: Debuggers",
        "Topic :: System :: Logging",
    ],
    python_requires=">=3.7",
    install_requires=[
        # Core dependencies are minimal - only standard library used
    ],
    extras_require={
        "dev": [
            "pytest>=6.0",
            "pytest-cov>=2.0",
            "black>=21.0",
            "flake8>=3.8",
            "mypy>=0.800",
        ],
        "gui": [
            "eel>=0.12.0",
        ],
    },
    entry_points={
        "console_scripts": [
            "android-log-analyzer=android_log_analyzer.log_analyzer:main",
        ]
    },
    include_package_data=True,
    zip_safe=False,
)
