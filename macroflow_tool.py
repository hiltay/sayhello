# Copyright (c) 2025 Bytedance Ltd. and/or its affiliates
# SPDX-License-Identifier: MIT

"""
SayHello tool integration for MacroFlow.

This file provides the integration layer between the sayhello tool
and the MacroFlow framework. It wraps the core sayhello functionality
and registers it with MacroFlow's tool registry.
"""

import json
import logging
import time
from pathlib import Path
from typing import Dict, List, Optional

from src.tools.common import run_command
from src.tools.registry import register_tool

logger = logging.getLogger(__name__)


def _get_sayhello_dir() -> Path:
    """Get the path to the sayhello tool directory."""
    return Path(__file__).parent.resolve()


def _run_sayhello_command(cmd: List[str]) -> Dict:
    """
    Run sayhello command in its own UV environment.
    
    Args:
        cmd: Command to run (e.g., ['sayhello', '--name', 'Alice'])
        
    Returns:
        Dictionary with command execution result
    """
    sayhello_dir = _get_sayhello_dir()
    
    # Check if uv.lock exists
    if not (sayhello_dir / "uv.lock").exists():
        logger.warning("uv.lock not found. Run 'make prepare-sayhello' to set up.")
    
    # Run command in sayhello's UV environment
    return run_command(
        cmd,
        cwd=str(sayhello_dir),
        env_wrapper="uv run",
        check_exists=[sayhello_dir],
    )


@register_tool(
    name="sayhello",
    description="""
    SayHello 工具 - 生成个性化问候语。
    
    这是一个简单的问候工具，用于演示如何将外部工具包集成到 MacroFlow。
    
    **重要：参数名称必须完全匹配**
    
    必需参数：
    - name (str): 要问候的人的名字，例如 "Alice"、"Bob"、"小明"
    
    可选参数：
    - language (str): 语言代码，默认 'en'
      支持的值: 'en' (English), 'zh' (中文), 'es' (Spanish), 'fr' (French)
    
    正确的调用示例：
    ```
    sayhello(name="Alice")
    sayhello(name="Bob", language="zh")
    sayhello(name="小明", language="zh")
    ```
    
    错误示例（不要使用）：
    - sayhello(person="Alice")  # 错误：参数名应该是 name
    - sayhello(target_person="Alice")  # 错误：参数名应该是 name
    - sayhello(user="Alice")  # 错误：参数名应该是 name
    
    注意：必须使用参数名 'name'，不要使用 person、target_person、user 等其他名称。
    """,
    category="demo",
    metadata={
        "version": "1.0.0",
        "author": "MacroFlow Team",
        "requires_gpu": False,
        "avg_runtime": "instant",
        "type": "greeting",
    },
)
def sayhello_tool(
    name: str = None,
    language: str = "en",
    **kwargs,  # 捕获其他参数
) -> dict:
    """
    MacroFlow wrapper for sayhello tool.
    
    This function wraps the core sayhello functionality and provides
    a standardized interface for MacroFlow to call.
    
    Args:
        name: The name of the person to greet
        language: Language code for the greeting (default: 'en')
        **kwargs: Additional parameters (for compatibility)
        
    Returns:
        Dictionary containing:
        - success: Whether the operation succeeded
        - greeting: The generated greeting message
        - language: The language used
        - name: The name that was greeted
        - processing_time: Time taken in seconds
    """
    start_time = time.time()
    
    # 参数别名映射 - 处理 LLM 可能使用的不同参数名
    if name is None:
        # 尝试从 kwargs 中获取常见的别名
        name_aliases = [
            'recipient',        # "recipient": "Bob"
            'target_person',    # "target_person": "Alice"
            'person',           # "person": "Charlie"
            'user',             # "user": "Dave"
            'username',         # "username": "Eve"
            'target',           # "target": "Frank"
            'who',              # "who": "Grace"
            'person_name',      # "person_name": "Henry"
        ]
        for alias in name_aliases:
            if alias in kwargs:
                name = kwargs[alias]
                logger.warning(f"Parameter alias detected: '{alias}' -> 'name', value: {name}")
                break
    
    # 处理 language 参数的别名
    if 'greeting_language' in kwargs:
        language = kwargs['greeting_language']
        logger.warning(f"Parameter alias detected: 'greeting_language' -> 'language', value: {language}")
    
    # 语言代码映射（中文 -> zh）
    language_mapping = {
        '中文': 'zh',
        '英文': 'en',
        'chinese': 'zh',
        'english': 'en',
        'spanish': 'es',
        'french': 'fr',
    }
    if language.lower() in language_mapping:
        original_lang = language
        language = language_mapping[language.lower()]
        logger.info(f"Language mapped: '{original_lang}' -> '{language}'")
    
    logger.info(f"SayHello tool called with name='{name}', language='{language}'")
    
    # 参数验证
    if not name or not name.strip():
        logger.error("Name parameter is empty")
        return {
            "success": False,
            "error": "参数 'name' 不能为空",
        }
    
    supported_languages = ["en", "zh", "es", "fr"]
    if language not in supported_languages:
        logger.warning(f"Unsupported language '{language}', defaulting to 'en'")
        language = "en"
    
    try:
        # 构建命令行参数
        cmd = [
            "sayhello",
            "--name", name,
            "--language", language,
            "--json",  # 输出 JSON 格式
        ]
        
        logger.info(f"Running command: {' '.join(cmd)}")
        
        # 通过 UV 在独立环境中执行命令
        cmd_result = _run_sayhello_command(cmd)
        
        if not cmd_result["success"]:
            error_msg = "SayHello command failed"
            if "not found" in cmd_result.get("error", ""):
                error_msg = "SayHello not installed. Run 'make prepare-sayhello' to set it up."
            
            logger.error(f"{error_msg}: {cmd_result.get('error')}")
            return {
                "success": False,
                "error": error_msg,
                "command": " ".join(["uv", "run"] + cmd),
                "stdout": cmd_result.get("stdout", ""),
                "stderr": cmd_result.get("stderr", ""),
            }
        
        # 解析 JSON 输出
        try:
            result = json.loads(cmd_result["stdout"])
            
            processing_time = time.time() - start_time
            
            # 添加处理时间
            result["processing_time"] = processing_time
            result["command"] = " ".join(["uv", "run"] + cmd)
            
            logger.info(f"SayHello completed successfully in {processing_time:.3f}s")
            return result
            
        except json.JSONDecodeError as e:
            logger.error(f"Failed to parse JSON output: {e}")
            return {
                "success": False,
                "error": "Failed to parse command output",
                "stdout": cmd_result.get("stdout", ""),
                "stderr": cmd_result.get("stderr", ""),
            }
        
    except Exception as e:
        logger.error(f"SayHello tool failed: {e}")
        return {
            "success": False,
            "error": f"执行失败: {str(e)}",
        }


@register_tool(
    name="sayhello_batch",
    description="""
    批量 SayHello 工具 - 为多个用户生成问候语。
    
    参数：
    - names: 用户名列表（必需）
    - language: 统一使用的语言（可选，默认 'en'）
    
    示例：
    sayhello_batch(names=["Alice", "Bob", "Charlie"])
    sayhello_batch(names=["小明", "小红"], language="zh")
    """,
    category="demo",
    metadata={
        "version": "1.0.0",
        "batch_processing": True,
    },
)
def sayhello_batch_tool(
    names: list = None,
    language: str = "en",
    **kwargs,
) -> dict:
    """
    Batch greeting tool.
    
    Args:
        names: List of names to greet
        language: Language for all greetings
        **kwargs: Additional parameters
        
    Returns:
        Batch processing results
    """
    start_time = time.time()
    
    # 参数别名处理
    if names is None:
        names_aliases = [
            'recipients',      # "recipients": [...]
            'name_list',       # "name_list": [...]
            'people',          # "people": [...]
            'users',           # "users": [...]
            'targets',         # "targets": [...]
            'persons',         # "persons": [...]
        ]
        for alias in names_aliases:
            if alias in kwargs:
                names = kwargs[alias]
                logger.warning(f"Parameter alias detected: '{alias}' -> 'names'")
                break
    
    if not names or not isinstance(names, list):
        return {
            "success": False,
            "error": "参数 'names' 必须是非空列表",
        }
    
    logger.info(f"Processing batch of {len(names)} names in language '{language}'")
    
    results = []
    failed = []
    
    for name in names:
        try:
            # 调用单个 sayhello_tool（内部使用命令行）
            result = sayhello_tool(name=name, language=language)
            
            if result.get("success"):
                results.append({
                    "name": name,
                    "greeting": result.get("greeting", ""),
                })
            else:
                failed.append({
                    "name": name,
                    "error": result.get("error", "Unknown error"),
                })
        except Exception as e:
            logger.error(f"Failed to process name '{name}': {e}")
            failed.append({
                "name": name,
                "error": str(e),
            })
    
    processing_time = time.time() - start_time
    
    return {
        "success": True,
        "total": len(names),
        "successful": len(results),
        "failed": len(failed),
        "results": results,
        "failed_items": failed,
        "language": language,
        "processing_time": processing_time,
    }

