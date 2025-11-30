"""Test cases for pattern matching utilities."""

from mxx.utils.pattern import (
    matches_pattern,
    matches_any_pattern,
    filter_keys_by_pattern
)


class TestMatchesPattern:
    """Test the matches_pattern function."""
    
    def test_exact_match(self):
        """Test exact string matching."""
        assert matches_pattern("hello", "hello")
        assert not matches_pattern("hello", "world")
    
    def test_wildcard_star(self):
        """Test * wildcard matching."""
        assert matches_pattern("wxx_auto.settings", "wxx*")
        assert matches_pattern("wxx_auto.settings", "*settings")
        assert matches_pattern("wxx_auto.settings", "wxx*.set*")
        assert not matches_pattern("other.key", "wxx*")
    
    def test_wildcard_question(self):
        """Test ? wildcard matching."""
        assert matches_pattern("abc", "a?c")
        assert matches_pattern("a1c", "a?c")
        assert not matches_pattern("abbc", "a?c")
    
    def test_wildcard_brackets(self):
        """Test bracket patterns."""
        assert matches_pattern("a1", "a[0-9]")
        assert matches_pattern("a5", "a[0-9]")
        assert not matches_pattern("ab", "a[0-9]")
        
        assert matches_pattern("ax", "a[!0-9]")
        assert not matches_pattern("a1", "a[!0-9]")
    
    def test_complex_patterns(self):
        """Test complex pattern combinations."""
        assert matches_pattern("test_file_123.txt", "test_*_*.txt")
        assert matches_pattern("config.prod.json", "config.*.json")
        assert matches_pattern("user_admin", "user_*")


class TestMatchesAnyPattern:
    """Test the matches_any_pattern function."""
    
    def test_single_pattern_match(self):
        """Test matching against single pattern."""
        assert matches_any_pattern("wxx.settings", ["wxx*"])
        assert not matches_any_pattern("other", ["wxx*"])
    
    def test_multiple_patterns_match(self):
        """Test matching against multiple patterns."""
        assert matches_any_pattern("wxx.settings", ["wxx*", "config*"])
        assert matches_any_pattern("config.main", ["wxx*", "config*"])
        assert not matches_any_pattern("other", ["wxx*", "config*"])
    
    def test_empty_patterns(self):
        """Test with empty pattern list."""
        assert not matches_any_pattern("anything", [])


class TestFilterKeysByPattern:
    """Test the filter_keys_by_pattern function."""
    
    def test_include_filter(self):
        """Test including keys that match pattern."""
        keys = ["wxx.a", "wxx.b", "other", "config"]
        result = filter_keys_by_pattern(keys, "wxx*")
        assert result == ["wxx.a", "wxx.b"]
    
    def test_exclude_filter(self):
        """Test excluding keys that match pattern."""
        keys = ["wxx.a", "wxx.b", "other", "config"]
        result = filter_keys_by_pattern(keys, "wxx*", exclude=True)
        assert result == ["other", "config"]
    
    def test_no_matches(self):
        """Test when no keys match pattern."""
        keys = ["key1", "key2", "key3"]
        result = filter_keys_by_pattern(keys, "nomatch*")
        assert result == []
    
    def test_all_match(self):
        """Test when all keys match pattern."""
        keys = ["item1", "item2", "item3"]
        result = filter_keys_by_pattern(keys, "item*")
        assert result == ["item1", "item2", "item3"]
    
    def test_empty_list(self):
        """Test with empty key list."""
        result = filter_keys_by_pattern([], "pattern*")
        assert result == []
