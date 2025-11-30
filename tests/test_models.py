"""Test cases for data models."""

import pytest
from mxx.models.ld import LDModel
from mxx.models.maa import MaaFileConfigModel, MaaConfigParseModel, MaaModel
from mxx.models.profile import MxxProfile


class TestBaseModel:
    """Test the BaseModel base class."""
    
    def test_update_simple_fields(self):
        """Test updating simple fields on a model."""
        model = LDModel(name="test")
        model.update({"name": "updated", "index": 5})
        
        assert model.name == "updated"
        assert model.index == 5
    
    def test_update_with_extra_fields(self):
        """Test that extra fields are stored in the extra dict."""
        model = LDModel(name="test")
        model.update({"name": "test", "custom_field": "value", "another": 123})
        
        assert model.name == "test"
        assert model.extra == {"custom_field": "value", "another": 123}
    
    def test_update_nested_model(self):
        """Test updating nested BaseModel instances."""
        profile = MxxProfile()
        profile.ld = LDModel(name="original")
        
        profile.update({
            "ld": {"name": "updated", "index": 10}
        })
        
        assert profile.ld.name == "updated"
        assert profile.ld.index == 10
    
    def test_create_simple_model(self):
        """Test creating a model with the create class method."""
        data = {"name": "test_name"}
        model = LDModel.create(data)
        
        assert model.name == "test_name"
        assert model.index is None
    
    def test_create_nested_model(self):
        """Test creating a model with nested BaseModel instances."""
        data = {
            "ld": {"name": "test_ld"},
            "maa": {"path": "/test/path", "app": "test_app"}
        }
        profile = MxxProfile.create(data)
        
        assert isinstance(profile.ld, LDModel)
        assert profile.ld.name == "test_ld"
        assert isinstance(profile.maa, MaaModel)
        assert profile.maa.path == "/test/path"
        assert profile.maa.app == "test_app"
    
    def test_create_deeply_nested_model(self):
        """Test creating a model with deeply nested structures."""
        data = {
            "maa": {
                "path": "/path",
                "fileConfig": {
                    "include": ["*.json", "*.toml"],
                    "exclude": ["*.bak"]
                },
                "parseConfig": {
                    "overwrite": {"key": "value"},
                    "exclude": ["field1", "field2"]
                }
            }
        }
        profile = MxxProfile.create(data)
        
        assert isinstance(profile.maa, MaaModel)
        assert isinstance(profile.maa.fileConfig, MaaFileConfigModel)
        assert profile.maa.fileConfig.include == ["*.json", "*.toml"]
        assert profile.maa.fileConfig.exclude == ["*.bak"]
        assert isinstance(profile.maa.parseConfig, MaaConfigParseModel)
        assert profile.maa.parseConfig.overwrite == {"key": "value"}
        assert profile.maa.parseConfig.exclude == ["field1", "field2"]


class TestLDModel:
    """Test the LDModel class."""
    
    def test_create_with_name_only(self):
        """Test creating LDModel with only name."""
        model = LDModel(name="test_name")
        
        assert model.name == "test_name"
        assert model.index is None
    
    def test_create_with_index_only(self):
        """Test creating LDModel with only index."""
        model = LDModel(index=5)
        
        assert model.index == 5
        assert model.name is None
    
    def test_create_with_both_raises_error(self):
        """Test that creating LDModel with both name and index raises ValueError."""
        with pytest.raises(ValueError, match="Only one of 'name' or 'index' should be provided"):
            LDModel(name="test", index=5)
    
    def test_create_with_neither_raises_error(self):
        """Test that creating LDModel with neither name nor index raises ValueError."""
        with pytest.raises(ValueError, match="Either 'name' or 'index' must be provided"):
            LDModel()
    
    def test_update_preserves_validation(self):
        """Test that updating an LDModel works correctly."""
        model = LDModel(name="original")
        model.update({"name": "updated"})
        
        assert model.name == "updated"
        assert model.index is None


class TestMaaFileConfigModel:
    """Test the MaaFileConfigModel class."""
    
    def test_default_initialization(self):
        """Test default initialization with empty lists."""
        model = MaaFileConfigModel()
        
        assert model.exclude == []
        assert model.include == []
    
    def test_initialization_with_values(self):
        """Test initialization with include and exclude patterns."""
        model = MaaFileConfigModel(
            include=["*.json", "*.toml"],
            exclude=["*.bak", "*.tmp"]
        )
        
        assert model.include == ["*.json", "*.toml"]
        assert model.exclude == ["*.bak", "*.tmp"]
    
    def test_create_from_dict(self):
        """Test creating MaaFileConfigModel from dictionary."""
        data = {
            "include": ["pattern1", "pattern2"],
            "exclude": ["pattern3"]
        }
        model = MaaFileConfigModel.create(data)
        
        assert model.include == ["pattern1", "pattern2"]
        assert model.exclude == ["pattern3"]


class TestMaaConfigParseModel:
    """Test the MaaConfigParseModel class."""
    
    def test_default_initialization(self):
        """Test default initialization with empty dict and list."""
        model = MaaConfigParseModel()
        
        assert model.overwrite == {}
        assert model.exclude == []
    
    def test_initialization_with_values(self):
        """Test initialization with overwrite and exclude values."""
        model = MaaConfigParseModel(
            overwrite={"key1": "value1", "key2": 123},
            exclude=["field1", "field2"]
        )
        
        assert model.overwrite == {"key1": "value1", "key2": 123}
        assert model.exclude == ["field1", "field2"]
    
    def test_create_from_dict(self):
        """Test creating MaaConfigParseModel from dictionary."""
        data = {
            "overwrite": {"config": "override"},
            "exclude": ["sensitive_field"]
        }
        model = MaaConfigParseModel.create(data)
        
        assert model.overwrite == {"config": "override"}
        assert model.exclude == ["sensitive_field"]


class TestMaaModel:
    """Test the MaaModel class."""
    
    def test_default_initialization(self):
        """Test default initialization with None values."""
        model = MaaModel()
        
        assert model.path is None
        assert model.app is None
        assert model.configDir is None
        assert model.fileConfig is None
        assert model.parseConfig is None
    
    def test_initialization_with_simple_values(self):
        """Test initialization with simple string values."""
        model = MaaModel(
            path="/test/path",
            app="test_app",
            configDir="/config/dir"
        )
        
        assert model.path == "/test/path"
        assert model.app == "test_app"
        assert model.configDir == "/config/dir"
    
    def test_initialization_with_nested_configs(self):
        """Test initialization with nested config models."""
        file_config = MaaFileConfigModel(include=["*.json"])
        parse_config = MaaConfigParseModel(exclude=["field1"])
        
        model = MaaModel(
            path="/path",
            fileConfig=file_config,
            parseConfig=parse_config
        )
        
        assert model.fileConfig == file_config
        assert model.parseConfig == parse_config
    
    def test_create_with_nested_dicts(self):
        """Test creating MaaModel with nested dictionary data."""
        data = {
            "path": "/test/path",
            "app": "app_name",
            "configDir": "/configs",
            "fileConfig": {
                "include": ["*.toml"],
                "exclude": ["*.bak"]
            },
            "parseConfig": {
                "overwrite": {"setting": "value"},
                "exclude": ["private"]
            }
        }
        model = MaaModel.create(data)
        
        assert model.path == "/test/path"
        assert model.app == "app_name"
        assert model.configDir == "/configs"
        assert isinstance(model.fileConfig, MaaFileConfigModel)
        assert model.fileConfig.include == ["*.toml"]
        assert isinstance(model.parseConfig, MaaConfigParseModel)
        assert model.parseConfig.overwrite == {"setting": "value"}
    
    def test_update_nested_configs(self):
        """Test updating nested config models."""
        model = MaaModel(
            fileConfig=MaaFileConfigModel(include=["*.json"]),
            parseConfig=MaaConfigParseModel(exclude=["field1"])
        )
        
        model.update({
            "fileConfig": {
                "include": ["*.toml", "*.json"],
                "exclude": ["*.tmp"]
            },
            "parseConfig": {
                "overwrite": {"new": "value"}
            }
        })
        
        assert model.fileConfig.include == ["*.toml", "*.json"]
        assert model.fileConfig.exclude == ["*.tmp"]
        assert model.parseConfig.overwrite == {"new": "value"}


class TestMxxProfile:
    """Test the MxxProfile class."""
    
    def test_default_initialization(self):
        """Test default initialization with None values."""
        profile = MxxProfile()
        
        assert profile.ld is None
        assert profile.maa is None
    
    def test_initialization_with_models(self):
        """Test initialization with ld and maa models."""
        ld = LDModel(name="test_ld")
        maa = MaaModel(path="/path")
        
        profile = MxxProfile(ld=ld, maa=maa)
        
        assert profile.ld == ld
        assert profile.maa == maa
    
    def test_create_full_profile(self):
        """Test creating a complete profile from dictionary."""
        data = {
            "ld": {
                "name": "test_name"
            },
            "maa": {
                "path": "/maa/path",
                "app": "maa_app",
                "configDir": "/configs",
                "fileConfig": {
                    "include": ["*.json", "*.toml"],
                    "exclude": ["*.bak"]
                },
                "parseConfig": {
                    "overwrite": {"key": "value"},
                    "exclude": ["sensitive"]
                }
            }
        }
        profile = MxxProfile.create(data)
        
        assert isinstance(profile.ld, LDModel)
        assert profile.ld.name == "test_name"
        assert isinstance(profile.maa, MaaModel)
        assert profile.maa.path == "/maa/path"
        assert profile.maa.app == "maa_app"
        assert isinstance(profile.maa.fileConfig, MaaFileConfigModel)
        assert profile.maa.fileConfig.include == ["*.json", "*.toml"]
        assert isinstance(profile.maa.parseConfig, MaaConfigParseModel)
        assert profile.maa.parseConfig.overwrite == {"key": "value"}
    
    def test_create_partial_profile_ld_only(self):
        """Test creating a profile with only ld data."""
        data = {"ld": {"index": 10}}
        profile = MxxProfile.create(data)
        
        assert isinstance(profile.ld, LDModel)
        assert profile.ld.index == 10
        assert profile.maa is None
    
    def test_create_partial_profile_maa_only(self):
        """Test creating a profile with only maa data."""
        data = {"maa": {"path": "/test"}}
        profile = MxxProfile.create(data)
        
        assert profile.ld is None
        assert isinstance(profile.maa, MaaModel)
        assert profile.maa.path == "/test"
    
    def test_update_profile_with_none_fields(self):
        """Test updating a profile when fields are None."""
        profile = MxxProfile()
        profile.update({
            "ld": {"name": "new_name"},
            "maa": {"path": "/new/path"}
        })
        
        # When fields are None, update sets them directly as values
        assert profile.ld == {"name": "new_name"}
        assert profile.maa == {"path": "/new/path"}
    
    def test_update_existing_models(self):
        """Test updating existing models in profile."""
        profile = MxxProfile(
            ld=LDModel(name="original"),
            maa=MaaModel(path="/original")
        )
        
        profile.update({
            "ld": {"name": "updated"},
            "maa": {"path": "/updated", "app": "new_app"}
        })
        
        assert profile.ld.name == "updated"
        assert profile.maa.path == "/updated"
        assert profile.maa.app == "new_app"
    
    def test_extra_fields_in_profile(self):
        """Test that extra fields are captured in profile."""
        data = {
            "ld": {"name": "test"},
            "custom_field": "custom_value",
            "another_field": 123
        }
        profile = MxxProfile.create(data)
        
        assert profile.ld.name == "test"
        assert profile.extra == {
            "custom_field": "custom_value",
            "another_field": 123
        }


class TestEdgeCases:
    """Test edge cases and error conditions."""
    
    def test_empty_data_update(self):
        """Test updating with empty dictionary."""
        model = LDModel(name="test")
        model.update({})
        
        assert model.name == "test"
        assert model.extra == {}
    
    def test_none_values_in_update(self):
        """Test updating with None values."""
        model = MaaModel(path="/path", app="app")
        model.update({"path": None, "app": "new_app"})
        
        assert model.path is None
        assert model.app == "new_app"
    
    def test_complex_nested_extra_fields(self):
        """Test that complex nested extra fields are preserved."""
        data = {
            "path": "/path",
            "app": "test_app",
            "extra_nested": {
                "level1": {
                    "level2": ["item1", "item2"]
                }
            }
        }
        model = MaaModel.create(data)
        
        assert model.path == "/path"
        assert model.app == "test_app"
        assert "extra_nested" in model.extra
        assert model.extra["extra_nested"]["level1"]["level2"] == ["item1", "item2"]
    
    def test_mixed_field_types(self):
        """Test models handle different field types correctly."""
        data = {
            "overwrite": {
                "string": "text",
                "number": 42,
                "float": 3.14,
                "bool": True,
                "list": [1, 2, 3],
                "nested": {"key": "value"}
            }
        }
        model = MaaConfigParseModel.create(data)
        
        assert model.overwrite["string"] == "text"
        assert model.overwrite["number"] == 42
        assert model.overwrite["float"] == 3.14
        assert model.overwrite["bool"] is True
        assert model.overwrite["list"] == [1, 2, 3]
        assert model.overwrite["nested"]["key"] == "value"
