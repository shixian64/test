"""
SPRD/Unisoc Platform Specific Log Analyzer

This module provides specialized analysis for SPRD (Spreadtrum/Unisoc) platform logs,
including ylog format and platform-specific issue detection.
"""
import json
import logging
import re
from pathlib import Path
from typing import Any, Dict, List, Optional, Set, Tuple

from .advanced_parser import AdvancedLogParser, LogSubsystem
from .log_analyzer import LogEntry

logger = logging.getLogger(__name__)


class SPRDLogAnalyzer(AdvancedLogParser):
    """Specialized analyzer for SPRD platform logs"""
    
    # SPRD-specific issue patterns
    SPRD_ISSUE_PATTERNS = {
        'modem_crash': {
            'patterns': [
                r'modem.*crash',
                r'cp.*assert',
                r'modem.*reset',
                r'cp.*exception',
                r'modem.*panic'
            ],
            'severity': 'critical',
            'category': 'modem'
        },
        'audio_underrun': {
            'patterns': [
                r'audio.*underrun',
                r'pcm.*underrun',
                r'audio.*xrun',
                r'alsa.*underrun'
            ],
            'severity': 'medium',
            'category': 'audio'
        },
        'connectivity_failure': {
            'patterns': [
                r'wifi.*disconnect',
                r'bt.*connection.*fail',
                r'wcn.*error',
                r'wifi.*scan.*fail'
            ],
            'severity': 'medium',
            'category': 'connectivity'
        },
        'sensor_timeout': {
            'patterns': [
                r'sensor.*timeout',
                r'sensorhub.*error',
                r'sensor.*not.*respond'
            ],
            'severity': 'low',
            'category': 'sensor'
        },
        'thermal_throttling': {
            'patterns': [
                r'thermal.*throttling',
                r'temperature.*high',
                r'cpu.*throttle',
                r'thermal.*shutdown'
            ],
            'severity': 'high',
            'category': 'thermal'
        },
        'power_management': {
            'patterns': [
                r'suspend.*fail',
                r'resume.*fail',
                r'power.*collapse.*fail',
                r'wakelock.*timeout'
            ],
            'severity': 'medium',
            'category': 'power'
        }
    }
    
    # SPRD log file specific parsers
    SPRD_PARSERS = {
        'ylog': '_parse_ylog_file',
        'modem': '_parse_modem_log',
        'audio': '_parse_audio_log',
        'connectivity': '_parse_connectivity_log',
        'sensor': '_parse_sensor_log'
    }
    
    def __init__(self, config=None):
        super().__init__(config)
        self.platform_info = {}
        self.ylog_metadata = {}
    
    def analyze_sprd_package(self, package_path: Path) -> Dict[str, Any]:
        """
        Analyze SPRD ylog package with platform-specific enhancements
        
        Args:
            package_path: Path to ylog package
            
        Returns:
            Enhanced analysis results with SPRD-specific insights
        """
        logger.info(f"Starting SPRD-specific analysis of: {package_path}")
        
        # First run standard analysis
        results = self.analyze_log_package(package_path)
        
        # Add SPRD-specific analysis
        results['sprd_analysis'] = {
            'platform_info': self._extract_platform_info(),
            'ylog_metadata': self._parse_ylog_metadata(),
            'modem_analysis': self._analyze_modem_subsystem(),
            'connectivity_analysis': self._analyze_connectivity_subsystem(),
            'audio_analysis': self._analyze_audio_subsystem(),
            'thermal_analysis': self._analyze_thermal_issues(),
            'power_analysis': self._analyze_power_issues(),
            'platform_recommendations': self._generate_platform_recommendations()
        }
        
        # Enhance timeline with SPRD-specific events
        results['timeline'] = self._enhance_timeline_with_sprd_events(results['timeline'])
        
        return results
    
    def _extract_platform_info(self) -> Dict[str, Any]:
        """Extract SPRD platform information from logs"""
        platform_info = {
            'chipset': 'unknown',
            'android_version': 'unknown',
            'build_version': 'unknown',
            'modem_version': 'unknown',
            'bootloader_version': 'unknown'
        }
        
        # Look for platform info in system logs
        if 'android' in self.subsystems:
            for file_path in self.subsystems['android'].files:
                if 'android_main' in str(file_path) or 'android_system' in str(file_path):
                    info = self._parse_platform_info_from_file(file_path)
                    platform_info.update(info)
        
        return platform_info
    
    def _parse_platform_info_from_file(self, file_path: Path) -> Dict[str, str]:
        """Parse platform information from a specific file"""
        info = {}
        
        try:
            with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                content = f.read(10000)  # Read first 10KB for platform info
                
                # Extract chipset info
                chipset_match = re.search(r'ro\.board\.platform[=:]\s*(\w+)', content)
                if chipset_match:
                    info['chipset'] = chipset_match.group(1)
                
                # Extract Android version
                android_match = re.search(r'ro\.build\.version\.release[=:]\s*([\d\.]+)', content)
                if android_match:
                    info['android_version'] = android_match.group(1)
                
                # Extract build version
                build_match = re.search(r'ro\.build\.display\.id[=:]\s*([^\s]+)', content)
                if build_match:
                    info['build_version'] = build_match.group(1)
                    
        except Exception as e:
            logger.debug(f"Error parsing platform info from {file_path}: {e}")
        
        return info
    
    def _parse_ylog_metadata(self) -> Dict[str, Any]:
        """Parse ylog.conf and other metadata files"""
        metadata = {
            'log_start_time': None,
            'log_end_time': None,
            'trigger_reason': 'unknown',
            'log_duration': None,
            'enabled_subsystems': []
        }
        
        # Look for ylog.conf files
        for subsystem in self.subsystems.values():
            for file_path in subsystem.files:
                if 'ylog.conf' in str(file_path):
                    conf_data = self._parse_ylog_conf(file_path)
                    metadata.update(conf_data)
        
        return metadata
    
    def _parse_ylog_conf(self, conf_path: Path) -> Dict[str, Any]:
        """Parse ylog configuration file"""
        conf_data = {}
        
        try:
            with open(conf_path, 'r', encoding='utf-8', errors='ignore') as f:
                for line in f:
                    line = line.strip()
                    if '=' in line and not line.startswith('#'):
                        key, value = line.split('=', 1)
                        conf_data[key.strip()] = value.strip()
        except Exception as e:
            logger.debug(f"Error parsing ylog.conf {conf_path}: {e}")
        
        return conf_data
    
    def _analyze_modem_subsystem(self) -> Dict[str, Any]:
        """Analyze modem-specific issues"""
        modem_analysis = {
            'crashes': [],
            'resets': [],
            'assert_failures': [],
            'signal_quality': [],
            'network_issues': []
        }
        
        if 'modem' not in self.subsystems:
            return modem_analysis
        
        for file_path in self.subsystems['modem'].files:
            try:
                issues = self._analyze_modem_file(file_path)
                for category, issue_list in issues.items():
                    if category in modem_analysis:
                        modem_analysis[category].extend(issue_list)
            except Exception as e:
                logger.error(f"Error analyzing modem file {file_path}: {e}")
        
        return modem_analysis
    
    def _analyze_modem_file(self, file_path: Path) -> Dict[str, List[Dict[str, Any]]]:
        """Analyze individual modem log file"""
        issues = {
            'crashes': [],
            'resets': [],
            'assert_failures': [],
            'signal_quality': [],
            'network_issues': []
        }
        
        try:
            with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                for line_num, line in enumerate(f, 1):
                    line = line.strip()
                    
                    # Check for modem crashes
                    if re.search(r'modem.*crash|cp.*assert|modem.*panic', line, re.IGNORECASE):
                        issues['crashes'].append({
                            'line_number': line_num,
                            'content': line,
                            'file': str(file_path),
                            'type': 'modem_crash'
                        })
                    
                    # Check for resets
                    elif re.search(r'modem.*reset|cp.*reset', line, re.IGNORECASE):
                        issues['resets'].append({
                            'line_number': line_num,
                            'content': line,
                            'file': str(file_path),
                            'type': 'modem_reset'
                        })
                    
                    # Check for signal quality issues
                    elif re.search(r'signal.*weak|rssi.*low|no.*signal', line, re.IGNORECASE):
                        issues['signal_quality'].append({
                            'line_number': line_num,
                            'content': line,
                            'file': str(file_path),
                            'type': 'signal_issue'
                        })
                        
        except Exception as e:
            logger.error(f"Error reading modem file {file_path}: {e}")
        
        return issues
    
    def _analyze_connectivity_subsystem(self) -> Dict[str, Any]:
        """Analyze WiFi/BT/FM connectivity issues"""
        connectivity_analysis = {
            'wifi_disconnects': [],
            'bt_failures': [],
            'scan_failures': [],
            'connection_timeouts': []
        }
        
        if 'connectivity' not in self.subsystems:
            return connectivity_analysis
        
        for file_path in self.subsystems['connectivity'].files:
            try:
                issues = self._analyze_connectivity_file(file_path)
                for category, issue_list in issues.items():
                    if category in connectivity_analysis:
                        connectivity_analysis[category].extend(issue_list)
            except Exception as e:
                logger.error(f"Error analyzing connectivity file {file_path}: {e}")
        
        return connectivity_analysis
    
    def _analyze_connectivity_file(self, file_path: Path) -> Dict[str, List[Dict[str, Any]]]:
        """Analyze individual connectivity log file"""
        issues = {
            'wifi_disconnects': [],
            'bt_failures': [],
            'scan_failures': [],
            'connection_timeouts': []
        }
        
        try:
            with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                for line_num, line in enumerate(f, 1):
                    line = line.strip()
                    
                    # WiFi disconnection patterns
                    if re.search(r'wifi.*disconnect|wlan.*disconnect', line, re.IGNORECASE):
                        issues['wifi_disconnects'].append({
                            'line_number': line_num,
                            'content': line,
                            'file': str(file_path),
                            'type': 'wifi_disconnect'
                        })
                    
                    # Bluetooth failures
                    elif re.search(r'bt.*fail|bluetooth.*error', line, re.IGNORECASE):
                        issues['bt_failures'].append({
                            'line_number': line_num,
                            'content': line,
                            'file': str(file_path),
                            'type': 'bt_failure'
                        })
                        
        except Exception as e:
            logger.error(f"Error reading connectivity file {file_path}: {e}")
        
        return issues
    
    def _analyze_audio_subsystem(self) -> Dict[str, Any]:
        """Analyze audio-specific issues"""
        audio_analysis = {
            'underruns': [],
            'codec_errors': [],
            'routing_issues': [],
            'volume_issues': []
        }
        
        if 'audio' not in self.subsystems:
            return audio_analysis
        
        for file_path in self.subsystems['audio'].files:
            try:
                issues = self._analyze_audio_file(file_path)
                for category, issue_list in issues.items():
                    if category in audio_analysis:
                        audio_analysis[category].extend(issue_list)
            except Exception as e:
                logger.error(f"Error analyzing audio file {file_path}: {e}")
        
        return audio_analysis
    
    def _analyze_audio_file(self, file_path: Path) -> Dict[str, List[Dict[str, Any]]]:
        """Analyze individual audio log file"""
        issues = {
            'underruns': [],
            'codec_errors': [],
            'routing_issues': [],
            'volume_issues': []
        }
        
        try:
            with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                for line_num, line in enumerate(f, 1):
                    line = line.strip()
                    
                    # Audio underrun detection
                    if re.search(r'underrun|xrun', line, re.IGNORECASE):
                        issues['underruns'].append({
                            'line_number': line_num,
                            'content': line,
                            'file': str(file_path),
                            'type': 'audio_underrun'
                        })
                        
        except Exception as e:
            logger.error(f"Error reading audio file {file_path}: {e}")
        
        return issues
    
    def _analyze_thermal_issues(self) -> Dict[str, Any]:
        """Analyze thermal management issues"""
        thermal_analysis = {
            'throttling_events': [],
            'temperature_warnings': [],
            'cooling_failures': []
        }
        
        # Search across all subsystems for thermal issues
        for subsystem in self.subsystems.values():
            for file_path in subsystem.files:
                try:
                    thermal_issues = self._find_thermal_issues_in_file(file_path)
                    for category, issue_list in thermal_issues.items():
                        if category in thermal_analysis:
                            thermal_analysis[category].extend(issue_list)
                except Exception as e:
                    logger.debug(f"Error checking thermal issues in {file_path}: {e}")
        
        return thermal_analysis
    
    def _find_thermal_issues_in_file(self, file_path: Path) -> Dict[str, List[Dict[str, Any]]]:
        """Find thermal-related issues in a file"""
        issues = {
            'throttling_events': [],
            'temperature_warnings': [],
            'cooling_failures': []
        }
        
        try:
            with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                for line_num, line in enumerate(f, 1):
                    if line_num > 10000:  # Limit search for performance
                        break
                        
                    line = line.strip()
                    
                    if re.search(r'thermal.*throttl|cpu.*throttl', line, re.IGNORECASE):
                        issues['throttling_events'].append({
                            'line_number': line_num,
                            'content': line,
                            'file': str(file_path),
                            'type': 'thermal_throttling'
                        })
                        
        except Exception as e:
            logger.debug(f"Error reading file for thermal analysis {file_path}: {e}")
        
        return issues
    
    def _analyze_power_issues(self) -> Dict[str, Any]:
        """Analyze power management issues"""
        power_analysis = {
            'suspend_failures': [],
            'wakelock_issues': [],
            'battery_issues': []
        }
        
        # Implementation similar to thermal analysis
        return power_analysis
    
    def _generate_platform_recommendations(self) -> List[str]:
        """Generate SPRD platform-specific recommendations"""
        recommendations = []
        
        # Check modem issues
        if 'modem' in self.subsystems:
            modem_files = len(self.subsystems['modem'].files)
            if modem_files > 0:
                recommendations.append("Review modem logs for baseband stability issues")
        
        # Check connectivity
        if 'connectivity' in self.subsystems:
            recommendations.append("Analyze WiFi/BT logs for connection stability")
        
        # Add more platform-specific recommendations
        recommendations.append("Check SPRD-specific thermal management")
        recommendations.append("Verify power management configuration")
        
        return recommendations
    
    def _enhance_timeline_with_sprd_events(self, timeline: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Add SPRD-specific events to timeline"""
        # This would add platform-specific event detection
        return timeline
