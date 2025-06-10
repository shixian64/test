"""Tests for configuration management."""
import json
import tempfile
import unittest
from pathlib import Path

from android_log_analyzer.config import ConfigManager


class TestConfigManager(unittest.TestCase):
    """Test cases for ConfigManager."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.temp_dir = Path(tempfile.mkdtemp())
        self.config_file = self.temp_dir / "test_config.json"
    
    def tearDown(self):
        """Clean up test fixtures."""
        if self.config_file.exists():
            self.config_file.unlink()
        if self.temp_dir.exists():
            self.temp_dir.rmdir()
    
    def test_default_config_loading(self):
        """Test that default configuration is loaded correctly."""
        config = ConfigManager()
        
        # Test some default values
        self.assertEqual(config.get("output.json_indent"), 2)
        self.assertEqual(config.get("analysis.max_file_size_mb"), 100)
        self.assertEqual(config.get("platforms.default"), "google")
    
    def test_config_get_set(self):
        """Test get and set operations."""
        config = ConfigManager()
        
        # Test setting new value
        config.set("test.new_value", 42)
        self.assertEqual(config.get("test.new_value"), 42)
        
        # Test getting non-existent key with default
        self.assertEqual(config.get("non.existent.key", "default"), "default")
        self.assertIsNone(config.get("non.existent.key"))


if __name__ == '__main__':
    unittest.main()
