"""
SayHello tool - generates personalized greetings.

Simple demonstration tool integrated with MacroFlow's new architecture.
"""

import json
import subprocess
import time
from pathlib import Path
from typing import Dict, List

from langchain_core.tools import tool
from pydantic import BaseModel, Field

logger = None  # Will be set by the factory function


class SayHelloInput(BaseModel):
    """Input schema for sayhello tool."""

    name: str = Field(
        description="The name of the person to greet, e.g., 'Alice', 'Bob', '小明'"
    )
    language: str = Field(
        description="Language code for the greeting",
        default="en",
    )


@tool(args_schema=SayHelloInput)
def sayhello(name: str, language: str = "en") -> Dict:
    """
    SayHello tool - generates personalized greetings in multiple languages.

    This is a simple demonstration tool showing how external tool packages
    integrate with MacroFlow.

    Args:
        name: The name of the person to greet
        language: Language code (en, zh, es, fr)

    Returns:
        Dictionary containing greeting message and metadata
    """
    import logging

    global logger
    if logger is None:
        logger = logging.getLogger(__name__)

    start_time = time.time()

    # Parameter validation
    if not name or not name.strip():
        return {
            "success": False,
            "error": "参数 'name' 不能为空",
        }

    supported_languages = ["en", "zh", "es", "fr"]
    if language not in supported_languages:
        logger.warning(f"Unsupported language '{language}', defaulting to 'en'")
        language = "en"

    try:
        # Build command
        cmd = [
            "sayhello",
            "--name", name,
            "--language", language,
            "--json",
        ]

        logger.info(f"Running command: {' '.join(cmd)}")

        # Run command in sayhello directory using uv
        sayhello_dir = Path(__file__).parent
        cmd_result = _run_sayhello_command(cmd, sayhello_dir)

        if not cmd_result["success"]:
            error_msg = "SayHello command failed"
            if "not found" in cmd_result.get("error", ""):
                error_msg = "SayHello not installed. Run 'make install-sayhello' to set it up."

            return {
                "success": False,
                "error": error_msg,
                "command": " ".join(["uv", "run"] + cmd),
                "stdout": cmd_result.get("stdout", ""),
                "stderr": cmd_result.get("stderr", ""),
            }

        # Parse JSON output
        result = json.loads(cmd_result["stdout"])
        result["processing_time"] = time.time() - start_time
        result["command"] = " ".join(["uv", "run"] + cmd)

        logger.info(f"SayHello completed successfully in {result['processing_time']:.3f}s")
        return result

    except Exception as e:
        logger.error(f"SayHello tool failed: {e}")
        return {
            "success": False,
            "error": f"执行失败: {str(e)}",
        }


def _run_sayhello_command(cmd: List[str], cwd: Path) -> Dict:
    """Run command in sayhello's UV environment."""
    try:
        # Run with uv
        full_cmd = ["uv", "run"] + cmd

        result = subprocess.run(
            full_cmd,
            cwd=str(cwd),
            capture_output=True,
            text=True,
            timeout=300,
        )

        return {
            "success": result.returncode == 0,
            "stdout": result.stdout,
            "stderr": result.stderr,
            "returncode": result.returncode,
        }

    except subprocess.TimeoutExpired:
        return {
            "success": False,
            "error": "Command timed out",
            "stdout": "",
            "stderr": "Command execution timed out",
        }
    except Exception as e:
        return {
            "success": False,
            "error": str(e),
            "stdout": "",
            "stderr": str(e),
        }


# Attach metadata for MacroFlow
sayhello.metadata = {
    "category": "demo",
    "aliases": ["greet", "hello"],
    "interrupt_config": None,
    "parameters": [
        {
            "name": "name",
            "type": "string",
            "required": True,
            "description": "The name of the person to greet",
            "examples": ["Alice", "Bob", "小明"],
        },
        {
            "name": "language",
            "type": "string",
            "required": False,
            "default": "en",
            "description": "Language code for the greeting",
            "enum": ["en", "zh", "es", "fr"],
        },
    ],
}
