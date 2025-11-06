"""
SayHello tool main implementation.

This module provides the core functionality of the sayhello tool.
"""

import logging
from typing import Dict

logger = logging.getLogger(__name__)


def sayhello(name: str) -> str:
    """
    Generate a greeting message for the given name.
    
    This is the core function of the sayhello tool. It takes a name
    and returns a personalized greeting.
    
    Args:
        name: The name of the person to greet
        
    Returns:
        A greeting string in the format "hello {name}!"
        
    Examples:
        >>> sayhello("Alice")
        'hello Alice!'
        
        >>> sayhello("Bob")
        'hello Bob!'
    """
    if not name or not name.strip():
        raise ValueError("Name cannot be empty")
    
    greeting = f"hello {name}!"
    logger.info(f"Generated greeting: {greeting}")
    return greeting


def sayhello_advanced(name: str, language: str = "en") -> Dict[str, str]:
    """
    Generate a greeting in different languages.
    
    This is an advanced version that supports multiple languages.
    
    Args:
        name: The name of the person to greet
        language: Language code ('en', 'zh', 'es', 'fr')
        
    Returns:
        Dictionary with greeting and metadata
    """
    greetings = {
        "en": f"hello {name}!",
        "zh": f"你好 {name}！",
        "es": f"¡hola {name}!",
        "fr": f"bonjour {name}!",
    }
    
    greeting = greetings.get(language, greetings["en"])
    
    return {
        "greeting": greeting,
        "language": language,
        "name": name,
        "length": len(greeting),
    }


if __name__ == "__main__":
    # Simple test
    print(sayhello("World"))
    print(sayhello_advanced("World", "zh"))

