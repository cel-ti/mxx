"""Test cases for JSON and TOML utilities."""

import tempfile
from pathlib import Path
from mxx.utils.json import load_json, save_json, touch_json
from mxx.utils.toml import load_toml, save_toml, touch_toml


class TestJsonUtilities:
    """Test JSON utility functions."""
    
    def test_save_and_load_json(self):
        """Test saving and loading JSON files."""
        with tempfile.TemporaryDirectory() as tmpdir:
            filepath = Path(tmpdir) / "test.json"
            
            data = {"name": "test", "value": 42, "nested": {"key": "value"}}
            save_json(data, filepath)
            
            loaded = load_json(filepath)
            assert loaded == data
    
    def test_json_formatting(self):
        """Test that JSON is saved with proper formatting."""
        with tempfile.TemporaryDirectory() as tmpdir:
            filepath = Path(tmpdir) / "test.json"
            
            data = {"key": "value"}
            save_json(data, filepath)
            
            content = filepath.read_text(encoding='utf-8')
            # Should be indented (contains newlines)
            assert '\n' in content
            assert '  ' in content  # 2-space indent
    
    def test_json_unicode(self):
        """Test that non-ASCII characters are preserved."""
        with tempfile.TemporaryDirectory() as tmpdir:
            filepath = Path(tmpdir) / "test.json"
            
            data = {"message": "Hello 世界 🌍"}
            save_json(data, filepath)
            
            loaded = load_json(filepath)
            assert loaded == data
    
    def test_touch_json_creates_file(self):
        """Test that touch_json creates a new file."""
        with tempfile.TemporaryDirectory() as tmpdir:
            filepath = Path(tmpdir) / "new.json"
            
            assert not filepath.exists()
            touch_json(filepath)
            assert filepath.exists()
            
            loaded = load_json(filepath)
            assert loaded == {}
    
    def test_touch_json_with_default(self):
        """Test touch_json with custom default data."""
        with tempfile.TemporaryDirectory() as tmpdir:
            filepath = Path(tmpdir) / "new.json"
            
            default_data = {"initialized": True, "version": "1.0"}
            touch_json(filepath, default=default_data)
            
            loaded = load_json(filepath)
            assert loaded == default_data
    
    def test_touch_json_does_not_overwrite(self):
        """Test that touch_json doesn't overwrite existing files."""
        with tempfile.TemporaryDirectory() as tmpdir:
            filepath = Path(tmpdir) / "existing.json"
            
            original_data = {"existing": "data"}
            save_json(original_data, filepath)
            
            touch_json(filepath, default={"new": "data"})
            
            loaded = load_json(filepath)
            assert loaded == original_data


class TestTomlUtilities:
    """Test TOML utility functions."""
    
    def test_save_and_load_toml(self):
        """Test saving and loading TOML files."""
        with tempfile.TemporaryDirectory() as tmpdir:
            filepath = Path(tmpdir) / "test.toml"
            
            data = {
                "title": "Test Config",
                "server": {
                    "host": "localhost",
                    "port": 8080
                }
            }
            save_toml(data, filepath)
            
            loaded = load_toml(filepath)
            assert loaded == data
    
    def test_toml_data_types(self):
        """Test that TOML handles various data types."""
        with tempfile.TemporaryDirectory() as tmpdir:
            filepath = Path(tmpdir) / "test.toml"
            
            data = {
                "string": "value",
                "integer": 42,
                "float": 3.14,
                "boolean": True,
                "array": [1, 2, 3],
                "nested": {
                    "key": "value"
                }
            }
            save_toml(data, filepath)
            
            loaded = load_toml(filepath)
            assert loaded == data
    
    def test_touch_toml_creates_file(self):
        """Test that touch_toml creates a new file."""
        with tempfile.TemporaryDirectory() as tmpdir:
            filepath = Path(tmpdir) / "new.toml"
            
            assert not filepath.exists()
            touch_toml(filepath)
            assert filepath.exists()
            
            loaded = load_toml(filepath)
            assert loaded == {}
    
    def test_touch_toml_with_default(self):
        """Test touch_toml with custom default data."""
        with tempfile.TemporaryDirectory() as tmpdir:
            filepath = Path(tmpdir) / "new.toml"
            
            default_data = {"version": "1.0", "debug": False}
            touch_toml(filepath, default=default_data)
            
            loaded = load_toml(filepath)
            assert loaded == default_data
    
    def test_touch_toml_does_not_overwrite(self):
        """Test that touch_toml doesn't overwrite existing files."""
        with tempfile.TemporaryDirectory() as tmpdir:
            filepath = Path(tmpdir) / "existing.toml"
            
            original_data = {"existing": "data"}
            save_toml(original_data, filepath)
            
            touch_toml(filepath, default={"new": "data"})
            
            loaded = load_toml(filepath)
            assert loaded == original_data
    
    def test_toml_with_dots_in_keys(self):
        """Test TOML with dots in key names."""
        with tempfile.TemporaryDirectory() as tmpdir:
            filepath = Path(tmpdir) / "test.toml"
            
            # Keys with dots need special handling in TOML
            data = {
                "section": {
                    "some.key.name": "value"
                }
            }
            save_toml(data, filepath)
            
            loaded = load_toml(filepath)
            assert loaded == data
