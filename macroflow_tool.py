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
import subprocess
import time
from pathlib import Path
from typing import Dict, List, Optional

from src.tools.common import run_command
from src.tools.registry import register_tool

logger = logging.getLogger(__name__)

# Docker container name (should match tool.mk)
DOCKER_CONTAINER_NAME = "sayhello_hnet_antibody"


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


def _run_docker_command(cmd: List[str], workdir: str = None) -> Dict:
    """
    Run command inside Docker container.
    
    Args:
        cmd: Command to run inside container (e.g., ['ls', '/root'])
        workdir: Working directory for the command (optional)
        
    Returns:
        Dictionary with command execution result
    """
    try:
        # Check if Docker is available
        docker_check = subprocess.run(
            ["docker", "--version"],
            capture_output=True,
            text=True,
            timeout=5
        )
        if docker_check.returncode != 0:
            return {
                "success": False,
                "error": "Docker is not available",
                "stdout": "",
                "stderr": "Docker command not found"
            }
        
        # Check if container exists and is running
        container_check = subprocess.run(
            ["docker", "ps", "--format", "{{.Names}}"],
            capture_output=True,
            text=True,
            timeout=5
        )
        
        if DOCKER_CONTAINER_NAME not in container_check.stdout:
            return {
                "success": False,
                "error": f"Container {DOCKER_CONTAINER_NAME} is not running",
                "stdout": "",
                "stderr": f"Please run 'make prepare-sayhello' to start the container"
            }
        
        # Run command in container
        docker_cmd = ["docker", "exec"]
        if workdir:
            docker_cmd.extend(["-w", workdir])
        docker_cmd.append(DOCKER_CONTAINER_NAME)
        docker_cmd.extend(cmd)
        
        logger.info(f"Running Docker command: {' '.join(docker_cmd)}")
        
        result = subprocess.run(
            docker_cmd,
            capture_output=True,
            text=True,
            timeout=300  # 5 minutes for deep learning inference
        )
        
        logger.info(f"Docker command returncode: {result.returncode}")
        logger.info(f"Docker command stdout length: {len(result.stdout)}")
        logger.info(f"Docker command stderr length: {len(result.stderr)}")
        
        return {
            "success": result.returncode == 0,
            "stdout": result.stdout,
            "stderr": result.stderr,
            "returncode": result.returncode
        }
        
    except subprocess.TimeoutExpired:
        return {
            "success": False,
            "error": "Command timed out",
            "stdout": "",
            "stderr": "Docker command execution timed out after 30 seconds"
        }
    except Exception as e:
        logger.error(f"Docker command failed: {e}")
        return {
            "success": False,
            "error": str(e),
            "stdout": "",
            "stderr": str(e)
        }


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
    name="humanness_predict",
    description="""
    Humanness 预测工具 - 判别蛋白质序列是否为人源。
    
    这个工具使用深度学习模型对蛋白质序列进行人源/非人源判别。
    
    **参数**：
    - input_file (str, 必需): 输入 FASTA 文件路径（容器内路径或将自动上传）
    - output_file (str, 可选): 输出文件路径，默认为 "humanness_results.csv"
    - checkpoint (str, 可选): 模型检查点路径，默认为 "pretrained_model/humanness.ckpt"
    - batch_size (int, 可选): 批处理大小，默认为 32
    - verbose (bool, 可选): 是否显示详细输出，默认为 False
    
    **示例**：
    humanness_predict(input_file="my_sequences.fasta")
    humanness_predict(input_file="test.fasta", output_file="results.csv", batch_size=64)
    
    **返回**：
    - success: 是否成功
    - output_file: 输出文件路径
    - results: 预测结果摘要
    - stdout: 命令输出
    - stderr: 错误输出
    """,
    category="bioinformatics",
    metadata={
        "version": "1.0.0",
        "requires_docker": True,
        "container_name": DOCKER_CONTAINER_NAME,
        "model_type": "deep_learning",
        "task": "humanness_prediction",
    },
)
def humanness_predict_tool(
    input_file: str = None,
    output_file: str = "humanness_results.csv",
    checkpoint: str = "pretrained_model/humanness.ckpt",
    batch_size: int = 32,
    verbose: bool = False,
    **kwargs,
) -> dict:
    """
    Predict humanness of protein sequences.
    
    Args:
        input_file: Path to input FASTA file (required)
        output_file: Path to output file (default: "humanness_results.csv")
        checkpoint: Path to model checkpoint (default: "pretrained_model/humanness.ckpt")
        batch_size: Batch size for inference (default: 32)
        verbose: Enable verbose output (default: False)
        **kwargs: Additional parameters (for compatibility)
        
    Returns:
        Dictionary containing:
        - success: Whether the operation succeeded
        - output_file: Path to output file
        - results: Summary of prediction results
        - stdout: Command output
        - stderr: Error output (if any)
        - processing_time: Time taken in seconds
    """
    start_time = time.time()
    
    # 参数验证
    if input_file is None or not str(input_file).strip():
        logger.error("Input file parameter is missing or empty")
        return {
            "success": False,
            "error": "参数 'input_file' 是必需的。请提供输入 FASTA 文件路径，例如: input_file='sequences.fasta'",
        }
    
    input_file = str(input_file).strip()
    logger.info(f"Humanness prediction tool called with input_file='{input_file}'")
    
    try:
        # 构建命令（使用 uv run）
        cmd_parts = [
            "uv run python inference_humanness.py",
            f"-i {input_file}",
            f"--output {output_file}",
            f"--checkpoint {checkpoint}",
            f"--batch-size {batch_size}",
        ]
        
        if verbose:
            cmd_parts.append("--verbose")
        
        command = " ".join(cmd_parts)
        # 使用 bash -c 执行，通过 workdir 参数设置工作目录
        cmd_list = ["bash", "-c", command]
        
        logger.info(f"Executing humanness prediction: {command}")
        
        # 在 Docker 容器中执行命令，设置工作目录为 /root/code
        result = _run_docker_command(cmd_list, workdir="/root/code")
        
        processing_time = time.time() - start_time
        
        if not result["success"]:
            logger.error(f"Humanness prediction failed: {result.get('error', 'Unknown error')}")
            return {
                "success": False,
                "error": result.get("error", "Prediction failed"),
                "stdout": result.get("stdout", ""),
                "stderr": result.get("stderr", ""),
                "input_file": input_file,
                "container": DOCKER_CONTAINER_NAME,
                "processing_time": processing_time,
            }
        
        logger.info(f"Humanness prediction completed successfully in {processing_time:.3f}s")
        
        # 尝试解析输出文件获取结果摘要
        results_summary = None
        try:
            # 读取输出文件的前几行作为摘要
            read_cmd = ["sh", "-c", f"head -n 10 {output_file}"]
            read_result = _run_docker_command(read_cmd, workdir="/root/code")
            if read_result["success"]:
                results_summary = read_result["stdout"]
        except Exception as e:
            logger.warning(f"Failed to read results summary: {e}")
        
        return {
            "success": True,
            "output_file": output_file,
            "input_file": input_file,
            "results_summary": results_summary,
            "stdout": result.get("stdout", ""),
            "stderr": result.get("stderr", ""),
            "container": DOCKER_CONTAINER_NAME,
            "processing_time": processing_time,
            "returncode": result.get("returncode", 0),
        }
        
    except Exception as e:
        logger.error(f"Humanness prediction tool failed: {e}")
        processing_time = time.time() - start_time
        return {
            "success": False,
            "error": f"执行失败: {str(e)}",
            "input_file": input_file,
            "container": DOCKER_CONTAINER_NAME,
            "processing_time": processing_time,
        }

