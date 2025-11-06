"""
Tests for SayHello tool.

Run with:
    cd src/tools/sayhello
    uv run pytest tests/
"""

import pytest


def test_sayhello_basic():
    """Test basic sayhello functionality"""
    from sayhello import sayhello
    
    result = sayhello("Alice")
    assert result == "hello Alice!"


def test_sayhello_advanced():
    """Test advanced sayhello with language support"""
    from sayhello import sayhello_advanced
    
    result = sayhello_advanced("Bob", language="en")
    assert result["greeting"] == "hello Bob!"
    assert result["name"] == "Bob"
    assert result["language"] == "en"


def test_sayhello_chinese():
    """Test Chinese greeting"""
    from sayhello import sayhello_advanced
    
    result = sayhello_advanced("小明", language="zh")
    assert "小明" in result["greeting"]
    assert result["language"] == "zh"


def test_sayhello_empty_name():
    """Test error handling for empty name"""
    from sayhello import sayhello
    
    with pytest.raises(ValueError, match="Name cannot be empty"):
        sayhello("")


def test_macroflow_tool():
    """Test MacroFlow integration"""
    from macroflow_tool import sayhello_tool
    
    result = sayhello_tool(name="Charlie")
    
    assert result["success"] is True
    assert "Charlie" in result["greeting"]
    assert "processing_time" in result


def test_macroflow_tool_chinese():
    """Test MacroFlow tool with Chinese"""
    from macroflow_tool import sayhello_tool
    
    result = sayhello_tool(name="小红", language="zh")
    
    assert result["success"] is True
    assert "小红" in result["greeting"]
    assert result["language"] == "zh"


def test_macroflow_batch_tool():
    """Test batch processing"""
    from macroflow_tool import sayhello_batch_tool
    
    result = sayhello_batch_tool(
        names=["Alice", "Bob", "Charlie"],
        language="en"
    )
    
    assert result["success"] is True
    assert result["total"] == 3
    assert result["successful"] == 3
    assert len(result["results"]) == 3


if __name__ == "__main__":
    pytest.main([__file__, "-v"])

