"""Test cases for nested dictionary utilities."""

from mxx.utils.nested import (
    nested_get,
    nested_set,
    nested_remove,
    nested_update
)


class TestNestedGet:
    """Test the nested_get function."""
    
    def test_simple_get(self):
        """Test getting a simple nested value."""
        data = {"config": {"server": {"port": 8080}}}
        assert nested_get(data, "config/server/port") == 8080
    
    def test_get_with_default(self):
        """Test getting with default value."""
        data = {"config": {"server": {"port": 8080}}}
        assert nested_get(data, "config/missing/key", "default") == "default"
    
    def test_get_empty_key(self):
        """Test getting with empty key returns data itself."""
        data = {"key": "value"}
        assert nested_get(data, "") == data
    
    def test_get_nonexistent_path(self):
        """Test getting nonexistent path."""
        data = {"config": {"server": {}}}
        assert nested_get(data, "config/server/port") is None
        assert nested_get(data, "nonexistent/path") is None
    
    def test_get_with_dots_in_key(self):
        """Test getting keys with literal dots."""
        data = {"config": {"some.key.name": "value"}}
        assert nested_get(data, "config/some.key.name") == "value"
    
    def test_get_intermediate_non_dict(self):
        """Test getting when intermediate value is not a dict."""
        data = {"config": "string_value"}
        assert nested_get(data, "config/server/port") is None


class TestNestedSet:
    """Test the nested_set function."""
    
    def test_simple_set(self):
        """Test setting a simple nested value."""
        data = {}
        nested_set(data, "config/server/port", 8080)
        assert data == {"config": {"server": {"port": 8080}}}
    
    def test_set_overwrite_existing(self):
        """Test overwriting existing value."""
        data = {"config": {"server": {"port": 8080}}}
        nested_set(data, "config/server/port", 9000)
        assert data["config"]["server"]["port"] == 9000
    
    def test_set_creates_intermediate_dicts(self):
        """Test that intermediate dicts are created."""
        data = {}
        nested_set(data, "a/b/c/d", "value")
        assert data == {"a": {"b": {"c": {"d": "value"}}}}
    
    def test_set_overwrites_non_dict(self):
        """Test that non-dict intermediate values are overwritten."""
        data = {"config": "string"}
        nested_set(data, "config/server/port", 8080)
        assert data == {"config": {"server": {"port": 8080}}}
    
    def test_set_empty_key_raises(self):
        """Test that empty key raises ValueError."""
        data = {}
        try:
            nested_set(data, "", "value")
            assert False, "Should have raised ValueError"
        except ValueError as e:
            assert "cannot be empty" in str(e).lower()


class TestNestedRemove:
    """Test the nested_remove function."""
    
    def test_simple_remove(self):
        """Test removing a simple nested key."""
        data = {"config": {"server": {"port": 8080, "host": "localhost"}}}
        result = nested_remove(data, "config/server/port")
        assert result is True
        assert data == {"config": {"server": {"host": "localhost"}}}
    
    def test_remove_nonexistent(self):
        """Test removing nonexistent key returns False."""
        data = {"config": {"server": {}}}
        result = nested_remove(data, "config/server/port")
        assert result is False
        assert data == {"config": {"server": {}}}
    
    def test_remove_empty_key(self):
        """Test removing with empty key returns False."""
        data = {"key": "value"}
        result = nested_remove(data, "")
        assert result is False
    
    def test_remove_entire_branch(self):
        """Test removing entire nested branch."""
        data = {"config": {"server": {"port": 8080}, "client": {}}}
        nested_remove(data, "config/server")
        assert data == {"config": {"client": {}}}
    
    def test_remove_with_invalid_path(self):
        """Test removing with invalid path."""
        data = {"config": "string"}
        result = nested_remove(data, "config/server/port")
        assert result is False


class TestNestedUpdate:
    """Test the nested_update function."""
    
    def test_simple_update(self):
        """Test simple nested update."""
        target = {"config": {"server": {"port": 8080}}}
        source = {"config": {"server": {"host": "localhost"}}}
        nested_update(target, source)
        assert target == {
            "config": {"server": {"port": 8080, "host": "localhost"}}
        }
    
    def test_deep_merge(self):
        """Test deep merge of nested dicts."""
        target = {"config": {"server": {"port": 8080}}}
        source = {"config": {"server": {"host": "localhost"}, "client": {"timeout": 30}}}
        nested_update(target, source)
        assert target == {
            "config": {
                "server": {"port": 8080, "host": "localhost"},
                "client": {"timeout": 30}
            }
        }
    
    def test_overwrite_non_dict(self):
        """Test that non-dict values are overwritten."""
        target = {"config": {"value": "old"}}
        source = {"config": {"value": "new"}}
        nested_update(target, source)
        assert target == {"config": {"value": "new"}}
    
    def test_add_new_keys(self):
        """Test adding completely new keys."""
        target = {"existing": "value"}
        source = {"new": "value"}
        nested_update(target, source)
        assert target == {"existing": "value", "new": "value"}
    
    def test_empty_source(self):
        """Test update with empty source."""
        target = {"key": "value"}
        source = {}
        nested_update(target, source)
        assert target == {"key": "value"}
    
    def test_empty_target(self):
        """Test update with empty target."""
        target = {}
        source = {"key": "value"}
        nested_update(target, source)
        assert target == {"key": "value"}
