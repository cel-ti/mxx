"""Test cases for config and model loading."""

import os
import tempfile
from pathlib import Path
from unittest import mock
import pytest

from mxx.core.config import get_config_path, get_profile_path
from mxx.core.model_load import (
    get_all_files,
    get_file,
    load_model,
    get_list,
    get_models,
    _cache
)
from mxx.models.ld import LDModel
from mxx.models.maa import MaaModel
from mxx.models.profile import MxxProfile
from mxx.utils.nofuss.toml import save_toml


class TestGetConfigPath:
    """Test the get_config_path and get_profile_path functions."""
    
    def test_default_config_path(self):
        """Test that default config path is in user home."""
        # Clear cache before test
        get_config_path.cache_clear()
        
        # Mock home to a temp directory
        with tempfile.TemporaryDirectory() as tmpdir:
            with mock.patch('pathlib.Path.home', return_value=Path(tmpdir)):
                # Ensure no env override
                with mock.patch.dict(os.environ, {}, clear=False):
                    if 'MXX_CONFIG_DIR' in os.environ:
                        del os.environ['MXX_CONFIG_DIR']
                    
                    config_path = get_config_path()
                    
                    assert config_path == Path(tmpdir) / ".mxx"
                    assert config_path.exists()
        
        # Clear cache after test
        get_config_path.cache_clear()
    
    def test_default_profile_path(self):
        """Test that default profile path is in config/configs."""
        # Clear cache before test
        get_config_path.cache_clear()
        
        # Mock home to a temp directory
        with tempfile.TemporaryDirectory() as tmpdir:
            with mock.patch('pathlib.Path.home', return_value=Path(tmpdir)):
                # Ensure no env override
                with mock.patch.dict(os.environ, {}, clear=False):
                    if 'MXX_CONFIG_DIR' in os.environ:
                        del os.environ['MXX_CONFIG_DIR']
                    
                    profile_path = get_profile_path()
                    
                    assert profile_path == Path(tmpdir) / ".mxx" / "configs"
                    assert profile_path.exists()
        
        # Clear cache after test
        get_config_path.cache_clear()
    
    def test_env_variable_override(self):
        """Test that MXX_CONFIG_DIR environment variable overrides default."""
        # Clear cache before test
        get_config_path.cache_clear()
        
        with tempfile.TemporaryDirectory() as tmpdir:
            custom_path = Path(tmpdir) / "custom_config"
            
            with mock.patch.dict(os.environ, {'MXX_CONFIG_DIR': str(custom_path)}):
                config_path = get_config_path()
                profile_path = get_profile_path()
                
                assert config_path == custom_path
                assert config_path.exists()
                assert profile_path == custom_path / "configs"
                assert profile_path.exists()
        
        # Clear cache after test
        get_config_path.cache_clear()
    
    def test_keyring_override(self):
        """Test that keyring override works when available."""
        # Clear cache before test
        get_config_path.cache_clear()
        
        with tempfile.TemporaryDirectory() as tmpdir:
            keyring_path = Path(tmpdir) / "keyring_config"
            
            # Mock keyring
            mock_keyring = mock.MagicMock()
            mock_keyring.get_password.return_value = str(keyring_path)
            
            with mock.patch.dict('sys.modules', {'keyring': mock_keyring}):
                with mock.patch.dict(os.environ, {}, clear=False):
                    if 'MXX_CONFIG_DIR' in os.environ:
                        del os.environ['MXX_CONFIG_DIR']
                    
                    config_path = get_config_path()
                    profile_path = get_profile_path()
                    
                    assert config_path == keyring_path
                    assert config_path.exists()
                    assert profile_path == keyring_path / "configs"
                    assert profile_path.exists()
                    mock_keyring.get_password.assert_called_once_with("mxx", "config_dir")
        
        # Clear cache after test
        get_config_path.cache_clear()
    
    def test_config_path_caching(self):
        """Test that config path is cached."""
        get_config_path.cache_clear()
        
        with tempfile.TemporaryDirectory() as tmpdir:
            with mock.patch.dict(os.environ, {'MXX_CONFIG_DIR': str(tmpdir)}):
                path1 = get_config_path()
                path2 = get_config_path()
                
                assert path1 is path2  # Same object due to caching
        
        get_config_path.cache_clear()


class TestModelLoadFunctions:
    """Test model loading functions."""
    
    def setup_method(self):
        """Set up test environment before each test."""
        # Clear the cache before each test
        _cache.clear()
        get_config_path.cache_clear()
    
    def teardown_method(self):
        """Clean up after each test."""
        _cache.clear()
        get_config_path.cache_clear()
    
    def test_get_all_files(self):
        """Test getting all TOML files from config directory."""
        with tempfile.TemporaryDirectory() as tmpdir:
            config_dir = Path(tmpdir)
            profiles_dir = config_dir / "configs"
            profiles_dir.mkdir()
            
            # Create test files
            (profiles_dir / "profile1.toml").touch()
            (profiles_dir / "profile2.ld.toml").touch()
            (profiles_dir / "profile3.maa.toml").touch()
            (profiles_dir / "not_toml.txt").touch()
            
            with mock.patch.dict(os.environ, {'MXX_CONFIG_DIR': str(config_dir)}):
                files = list(get_all_files())
                
                assert len(files) == 3
                
                # Check file names and parts
                file_dict = {stem: (file, part3) for file, stem, part3 in files}
                
                assert "profile1" in file_dict
                assert file_dict["profile1"][1] is None
                
                assert "profile2.ld" in file_dict
                assert file_dict["profile2.ld"][1] == "ld"
                
                assert "profile3.maa" in file_dict
                assert file_dict["profile3.maa"][1] == "maa"
    
    def test_get_file_exact_match(self):
        """Test getting a file by exact name match."""
        with tempfile.TemporaryDirectory() as tmpdir:
            config_dir = Path(tmpdir)
            profiles_dir = config_dir / "configs"
            profiles_dir.mkdir()
            
            (profiles_dir / "myprofile.toml").touch()
            (profiles_dir / "other.ld.toml").touch()
            
            with mock.patch.dict(os.environ, {'MXX_CONFIG_DIR': str(config_dir)}):
                result = get_file("myprofile")
                
                assert result is not None
                file, part2, part3 = result
                assert file.name == "myprofile.toml"
                assert part2 == "myprofile"
                assert part3 is None
    
    def test_get_file_partial_match(self):
        """Test getting a file by partial name match."""
        with tempfile.TemporaryDirectory() as tmpdir:
            config_dir = Path(tmpdir)
            profiles_dir = config_dir / "configs"
            profiles_dir.mkdir()
            
            (profiles_dir / "myprofile.ld.toml").touch()
            
            with mock.patch.dict(os.environ, {'MXX_CONFIG_DIR': str(config_dir)}):
                result = get_file("myprofile")
                
                assert result is not None
                file, part2, part3 = result
                assert file.name == "myprofile.ld.toml"
                assert part2 == "myprofile.ld"
                assert part3 == "ld"
    
    def test_get_file_with_extension(self):
        """Test getting a file when full name with extension is provided."""
        with tempfile.TemporaryDirectory() as tmpdir:
            config_dir = Path(tmpdir)
            profiles_dir = config_dir / "configs"
            profiles_dir.mkdir()
            
            (profiles_dir / "myprofile.ld.toml").touch()
            
            with mock.patch.dict(os.environ, {'MXX_CONFIG_DIR': str(config_dir)}):
                result = get_file("myprofile.ld")
                
                assert result is not None
                file, part2, part3 = result
                assert file.name == "myprofile.ld.toml"
    
    def test_get_file_not_found(self):
        """Test that None is returned when file doesn't exist."""
        with tempfile.TemporaryDirectory() as tmpdir:
            config_dir = Path(tmpdir)
            profiles_dir = config_dir / "configs"
            profiles_dir.mkdir()
            
            with mock.patch.dict(os.environ, {'MXX_CONFIG_DIR': str(config_dir)}):
                result = get_file("nonexistent")
                
                assert result is None
    
    def test_load_model_ld(self):
        """Test loading an LD model from TOML file."""
        with tempfile.TemporaryDirectory() as tmpdir:
            config_dir = Path(tmpdir)
            profiles_dir = config_dir / "configs"
            profiles_dir.mkdir()
            
            # Create LD model file
            ld_data = {"name": "test_device"}
            save_toml(ld_data, profiles_dir / "device.ld.toml")
            
            with mock.patch.dict(os.environ, {'MXX_CONFIG_DIR': str(config_dir)}):
                model = load_model("device")
                
                assert isinstance(model, LDModel)
                assert model.name == "test_device"
                assert model.index is None
    
    def test_load_model_maa(self):
        """Test loading a MAA model from TOML file."""
        with tempfile.TemporaryDirectory() as tmpdir:
            config_dir = Path(tmpdir)
            profiles_dir = config_dir / "configs"
            profiles_dir.mkdir()
            
            # Create MAA model file
            maa_data = {
                "path": "/test/path",
                "app": "test_app",
                "configDir": "/configs"
            }
            save_toml(maa_data, profiles_dir / "maa_config.maa.toml")
            
            with mock.patch.dict(os.environ, {'MXX_CONFIG_DIR': str(config_dir)}):
                model = load_model("maa_config")
                
                assert isinstance(model, MaaModel)
                assert model.path == "/test/path"
                assert model.app == "test_app"
                assert model.configDir == "/configs"
    
    def test_load_model_profile(self):
        """Test loading a profile model from TOML file."""
        with tempfile.TemporaryDirectory() as tmpdir:
            config_dir = Path(tmpdir)
            profiles_dir = config_dir / "configs"
            profiles_dir.mkdir()
            
            # Create profile file
            profile_data = {
                "ld": {"name": "device1"},
                "maa": {"path": "/path", "app": "app1"}
            }
            save_toml(profile_data, profiles_dir / "myprofile.toml")
            
            with mock.patch.dict(os.environ, {'MXX_CONFIG_DIR': str(config_dir)}):
                model = load_model("myprofile")
                
                assert isinstance(model, MxxProfile)
                assert isinstance(model.ld, LDModel)
                assert model.ld.name == "device1"
                assert isinstance(model.maa, MaaModel)
                assert model.maa.path == "/path"
    
    def test_load_model_with_template(self):
        """Test loading a model that references a template."""
        with tempfile.TemporaryDirectory() as tmpdir:
            config_dir = Path(tmpdir)
            profiles_dir = config_dir / "configs"
            profiles_dir.mkdir()
            
            # Create template MAA model
            template_data = {
                "path": "/template/path",
                "app": "template_app"
            }
            save_toml(template_data, profiles_dir / "template.maa.toml")
            
            # Create profile that uses template
            profile_data = {
                "ld": {"index": 5},
                "maa": {"template": "template"}
            }
            save_toml(profile_data, profiles_dir / "with_template.toml")
            
            with mock.patch.dict(os.environ, {'MXX_CONFIG_DIR': str(config_dir)}):
                model = load_model("with_template")
                
                assert isinstance(model, MxxProfile)
                assert isinstance(model.ld, LDModel)
                assert model.ld.index == 5
                assert isinstance(model.maa, MaaModel)
                assert model.maa.path == "/template/path"
                assert model.maa.app == "template_app"
    
    def test_load_model_template_not_found(self):
        """Test that loading fails when template doesn't exist."""
        with tempfile.TemporaryDirectory() as tmpdir:
            config_dir = Path(tmpdir)
            profiles_dir = config_dir / "configs"
            profiles_dir.mkdir()
            
            profile_data = {
                "maa": {"template": "nonexistent_template"}
            }
            save_toml(profile_data, profiles_dir / "bad_template.toml")
            
            with mock.patch.dict(os.environ, {'MXX_CONFIG_DIR': str(config_dir)}):
                with pytest.raises(ValueError, match="Template model 'nonexistent_template' not found"):
                    load_model("bad_template")
    
    def test_load_model_template_with_extra_keys(self):
        """Test that loading fails when template definition has extra keys."""
        with tempfile.TemporaryDirectory() as tmpdir:
            config_dir = Path(tmpdir)
            profiles_dir = config_dir / "configs"
            profiles_dir.mkdir()
            
            profile_data = {
                "maa": {
                    "template": "some_template",
                    "extra_key": "should_not_be_here"
                }
            }
            save_toml(profile_data, profiles_dir / "bad_template.toml")
            
            with mock.patch.dict(os.environ, {'MXX_CONFIG_DIR': str(config_dir)}):
                with pytest.raises(ValueError, match="Template definition for 'maa' .* has extra keys"):
                    load_model("bad_template")
    
    def test_load_model_caching(self):
        """Test that loaded models are cached."""
        with tempfile.TemporaryDirectory() as tmpdir:
            config_dir = Path(tmpdir)
            profiles_dir = config_dir / "configs"
            profiles_dir.mkdir()
            
            ld_data = {"name": "cached_device"}
            save_toml(ld_data, profiles_dir / "cached.ld.toml")
            
            with mock.patch.dict(os.environ, {'MXX_CONFIG_DIR': str(config_dir)}):
                model1 = load_model("cached")
                model2 = load_model("cached")
                
                # Should be the same cached object
                assert model1 is model2
    
    def test_load_model_not_found(self):
        """Test that None is returned when model file doesn't exist."""
        with tempfile.TemporaryDirectory() as tmpdir:
            config_dir = Path(tmpdir)
            profiles_dir = config_dir / "configs"
            profiles_dir.mkdir()
            
            with mock.patch.dict(os.environ, {'MXX_CONFIG_DIR': str(config_dir)}):
                model = load_model("nonexistent")
                
                assert model is None
    
    def test_get_list(self):
        """Test getting list of all model names."""
        with tempfile.TemporaryDirectory() as tmpdir:
            config_dir = Path(tmpdir)
            profiles_dir = config_dir / "configs"
            profiles_dir.mkdir()
            
            # Create multiple files
            (profiles_dir / "profile1.toml").touch()
            (profiles_dir / "device.ld.toml").touch()
            (profiles_dir / "maa_config.maa.toml").touch()
            
            with mock.patch.dict(os.environ, {'MXX_CONFIG_DIR': str(config_dir)}):
                names = list(get_list())
                
                assert len(names) == 3
                assert "profile1" in names
                assert "device.ld" in names
                assert "maa_config.maa" in names
    
    def test_get_models(self):
        """Test getting all models with their names."""
        with tempfile.TemporaryDirectory() as tmpdir:
            config_dir = Path(tmpdir)
            profiles_dir = config_dir / "configs"
            profiles_dir.mkdir()
            
            # Create valid model files
            save_toml({"name": "device1"}, profiles_dir / "dev1.ld.toml")
            save_toml({"path": "/path"}, profiles_dir / "maa1.maa.toml")
            save_toml(
                {"ld": {"index": 1}, "maa": {"path": "/p"}},
                profiles_dir / "profile.toml"
            )
            
            with mock.patch.dict(os.environ, {'MXX_CONFIG_DIR': str(config_dir)}):
                models = list(get_models())
                
                assert len(models) == 3
                
                names = [name for name, model in models]
                assert "dev1.ld" in names
                assert "maa1.maa" in names
                assert "profile" in names
                
                # Verify model types
                model_dict = {name: model for name, model in models}
                assert isinstance(model_dict["dev1.ld"], LDModel)
                assert isinstance(model_dict["maa1.maa"], MaaModel)
                assert isinstance(model_dict["profile"], MxxProfile)
    
    def test_complex_nested_model_with_template(self):
        """Test loading complex nested models with templates."""
        with tempfile.TemporaryDirectory() as tmpdir:
            config_dir = Path(tmpdir)
            profiles_dir = config_dir / "configs"
            profiles_dir.mkdir()
            
            # Create MAA template with nested config
            template_data = {
                "path": "/base/path",
                "app": "base_app",
                "fileConfig": {
                    "include": ["*.json"],
                    "exclude": ["*.bak"]
                },
                "parseConfig": {
                    "overwrite": {"key1": "value1"},
                    "exclude": ["field1"]
                }
            }
            save_toml(template_data, profiles_dir / "base_maa.maa.toml")
            
            # Create profile using template
            profile_data = {
                "ld": {"name": "mydevice"},
                "maa": {"template": "base_maa"}
            }
            save_toml(profile_data, profiles_dir / "complex.toml")
            
            with mock.patch.dict(os.environ, {'MXX_CONFIG_DIR': str(config_dir)}):
                model = load_model("complex")
                
                assert isinstance(model, MxxProfile)
                assert model.ld.name == "mydevice"
                assert model.maa.path == "/base/path"
                assert model.maa.app == "base_app"
                assert model.maa.fileConfig.include == ["*.json"]
                assert model.maa.parseConfig.overwrite == {"key1": "value1"}


class TestIntegrationScenarios:
    """Test real-world integration scenarios."""
    
    def setup_method(self):
        """Set up test environment."""
        _cache.clear()
        get_config_path.cache_clear()
    
    def teardown_method(self):
        """Clean up after tests."""
        _cache.clear()
        get_config_path.cache_clear()
    
    def test_multiple_profiles_with_shared_templates(self):
        """Test loading multiple profiles that share templates."""
        with tempfile.TemporaryDirectory() as tmpdir:
            config_dir = Path(tmpdir)
            profiles_dir = config_dir / "configs"
            profiles_dir.mkdir()
            
            # Create shared MAA template
            maa_template = {
                "path": "/shared/path",
                "app": "shared_app"
            }
            save_toml(maa_template, profiles_dir / "shared_maa.maa.toml")
            
            # Create two profiles using the same template
            profile1_data = {
                "ld": {"name": "device1"},
                "maa": {"template": "shared_maa"}
            }
            save_toml(profile1_data, profiles_dir / "profile1.toml")
            
            profile2_data = {
                "ld": {"index": 2},
                "maa": {"template": "shared_maa"}
            }
            save_toml(profile2_data, profiles_dir / "profile2.toml")
            
            with mock.patch.dict(os.environ, {'MXX_CONFIG_DIR': str(config_dir)}):
                p1 = load_model("profile1")
                p2 = load_model("profile2")
                
                # Both should have same MAA data
                assert p1.maa.path == p2.maa.path == "/shared/path"
                assert p1.maa.app == p2.maa.app == "shared_app"
                
                # But different LD data
                assert p1.ld.name == "device1"
                assert p2.ld.index == 2
    
    def test_all_operations_with_custom_config_dir(self):
        """Test all operations work correctly with custom config directory."""
        with tempfile.TemporaryDirectory() as tmpdir:
            config_dir = Path(tmpdir) / "custom_configs"
            config_dir.mkdir()
            profiles_dir = config_dir / "configs"
            profiles_dir.mkdir()
            
            # Create various files
            save_toml({"name": "dev1"}, profiles_dir / "device1.ld.toml")
            save_toml({"path": "/p1"}, profiles_dir / "maa1.maa.toml")
            save_toml(
                {"ld": {"index": 1}, "maa": {"path": "/p2"}},
                profiles_dir / "full_profile.toml"
            )
            
            with mock.patch.dict(os.environ, {'MXX_CONFIG_DIR': str(config_dir)}):
                # Test get_all_files
                files = list(get_all_files())
                assert len(files) == 3
                
                # Test get_list
                names = list(get_list())
                assert len(names) == 3
                
                # Test get_file
                assert get_file("device1") is not None
                assert get_file("nonexistent") is None
                
                # Test load_model
                dev = load_model("device1")
                assert isinstance(dev, LDModel)
                
                # Test get_models
                models = list(get_models())
                assert len(models) == 3
