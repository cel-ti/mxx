"""Test cases for file utilities."""

import tempfile
from pathlib import Path
from mxx.utils.file import (
    filter_files,
    load_config_file,
    save_config_file,
    create_zip_from_dict,
    load_zip_to_dict
)


class TestFilterFiles:
    """Test the filter_files function."""
    
    def test_filter_with_include_patterns(self):
        """Test filtering files with include patterns."""
        with tempfile.TemporaryDirectory() as tmpdir:
            tmppath = Path(tmpdir)
            
            # Create test files
            (tmppath / "config.toml").touch()
            (tmppath / "settings.json").touch()
            (tmppath / "data.txt").touch()
            
            # Filter for toml and json
            files = filter_files(tmppath, include_patterns=["*.toml", "*.json"])
            filenames = [f.name for f in files]
            
            assert "config.toml" in filenames
            assert "settings.json" in filenames
            assert "data.txt" not in filenames
    
    def test_filter_with_exclude_patterns(self):
        """Test filtering files with exclude patterns."""
        with tempfile.TemporaryDirectory() as tmpdir:
            tmppath = Path(tmpdir)
            
            # Create test files
            (tmppath / "config.toml").touch()
            (tmppath / "backup.bak").touch()
            (tmppath / "temp.tmp").touch()
            
            # Exclude backup files
            files = filter_files(tmppath, exclude_patterns=["*.bak", "*.tmp"])
            filenames = [f.name for f in files]
            
            assert "config.toml" in filenames
            assert "backup.bak" not in filenames
            assert "temp.tmp" not in filenames
    
    def test_filter_with_both_patterns(self):
        """Test filtering with both include and exclude patterns."""
        with tempfile.TemporaryDirectory() as tmpdir:
            tmppath = Path(tmpdir)
            
            # Create test files
            (tmppath / "config.toml").touch()
            (tmppath / "config.toml.bak").touch()
            (tmppath / "settings.json").touch()
            
            # Include config files but exclude backups
            files = filter_files(
                tmppath,
                include_patterns=["*.toml", "*.json"],
                exclude_patterns=["*.bak"]
            )
            filenames = [f.name for f in files]
            
            assert "config.toml" in filenames
            assert "settings.json" in filenames
            assert "config.toml.bak" not in filenames
    
    def test_filter_nonexistent_directory(self):
        """Test filtering nonexistent directory."""
        result = filter_files(Path("/nonexistent/path"))
        assert result == []
    
    def test_filter_recursive(self):
        """Test recursive file filtering."""
        with tempfile.TemporaryDirectory() as tmpdir:
            tmppath = Path(tmpdir)
            
            # Create nested structure
            (tmppath / "root.toml").touch()
            subdir = tmppath / "subdir"
            subdir.mkdir()
            (subdir / "nested.toml").touch()
            
            # Filter should find both files
            files = filter_files(tmppath, include_patterns=["*.toml"])
            assert len(files) == 2


class TestConfigFileOperations:
    """Test load and save config file operations."""
    
    def test_load_save_toml(self):
        """Test loading and saving TOML files."""
        with tempfile.TemporaryDirectory() as tmpdir:
            filepath = Path(tmpdir) / "config.toml"
            
            data = {"server": {"port": 8080, "host": "localhost"}}
            save_config_file(filepath, data)
            
            loaded = load_config_file(filepath)
            assert loaded == data
    
    def test_load_save_json(self):
        """Test loading and saving JSON files."""
        with tempfile.TemporaryDirectory() as tmpdir:
            filepath = Path(tmpdir) / "config.json"
            
            data = {"server": {"port": 8080, "host": "localhost"}}
            save_config_file(filepath, data)
            
            loaded = load_config_file(filepath)
            assert loaded == data
    
    def test_save_creates_directories(self):
        """Test that save creates parent directories."""
        with tempfile.TemporaryDirectory() as tmpdir:
            filepath = Path(tmpdir) / "nested" / "dir" / "config.json"
            
            data = {"key": "value"}
            save_config_file(filepath, data)
            
            assert filepath.exists()
            loaded = load_config_file(filepath)
            assert loaded == data
    
    def test_load_unsupported_format(self):
        """Test loading unsupported file format raises error."""
        with tempfile.TemporaryDirectory() as tmpdir:
            filepath = Path(tmpdir) / "config.txt"
            filepath.write_text("some text")
            
            try:
                load_config_file(filepath)
                assert False, "Should have raised ValueError"
            except ValueError as e:
                assert "Unsupported file type" in str(e)
    
    def test_save_unsupported_format(self):
        """Test saving unsupported file format raises error."""
        with tempfile.TemporaryDirectory() as tmpdir:
            filepath = Path(tmpdir) / "config.txt"
            
            try:
                save_config_file(filepath, {"key": "value"})
                assert False, "Should have raised ValueError"
            except ValueError as e:
                assert "Unsupported file type" in str(e)


class TestZipOperations:
    """Test zip file operations."""
    
    def test_create_and_load_zip(self):
        """Test creating and loading zip files."""
        with tempfile.TemporaryDirectory() as tmpdir:
            zip_path = Path(tmpdir) / "backup.zip"
            
            # Create zip with multiple files
            files_dict = {
                "config.toml": {"server": {"port": 8080}},
                "settings.json": {"theme": "dark", "language": "en"}
            }
            create_zip_from_dict(zip_path, files_dict)
            
            # Load and verify
            loaded = load_zip_to_dict(zip_path)
            assert loaded == files_dict
    
    def test_create_zip_nested_structure(self):
        """Test creating zip with nested file structure."""
        with tempfile.TemporaryDirectory() as tmpdir:
            zip_path = Path(tmpdir) / "backup.zip"
            
            files_dict = {
                "root.json": {"key": "value"},
                "subdir/nested.json": {"nested": "data"}
            }
            create_zip_from_dict(zip_path, files_dict)
            
            loaded = load_zip_to_dict(zip_path)
            assert loaded == files_dict
    
    def test_load_nonexistent_zip(self):
        """Test loading nonexistent zip file raises error."""
        try:
            load_zip_to_dict(Path("/nonexistent.zip"))
            assert False, "Should have raised FileNotFoundError"
        except FileNotFoundError:
            pass
    
    def test_zip_preserves_data_types(self):
        """Test that zip operations preserve data types."""
        with tempfile.TemporaryDirectory() as tmpdir:
            zip_path = Path(tmpdir) / "backup.zip"
            
            files_dict = {
                "config.json": {
                    "string": "value",
                    "number": 42,
                    "float": 3.14,
                    "bool": True,
                    "null": None,
                    "array": [1, 2, 3],
                    "object": {"nested": "value"}
                }
            }
            create_zip_from_dict(zip_path, files_dict)
            
            loaded = load_zip_to_dict(zip_path)
            assert loaded == files_dict
    
    def test_create_zip_creates_parent_dirs(self):
        """Test that create_zip creates parent directories."""
        with tempfile.TemporaryDirectory() as tmpdir:
            zip_path = Path(tmpdir) / "nested" / "dir" / "backup.zip"
            
            files_dict = {"config.json": {"key": "value"}}
            create_zip_from_dict(zip_path, files_dict)
            
            assert zip_path.exists()
            loaded = load_zip_to_dict(zip_path)
            assert loaded == files_dict
