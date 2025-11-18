"""
MacroFlow Toolkit - SayHello Tools Factory

This module provides the factory function for SayHello tool
following the LangChain 1.0 standard and auto-discovery convention.

约定：
- 工厂函数名称：make_tool (自动发现)
- 返回类型：List[BaseTool] (支持多工具)
- 参数：接受标准依赖 (CommandRunner, WorkspaceBuilder, PathResolver)
"""

import logging
from typing import List

from langchain_core.tools import BaseTool

from macroflow_toolkit.deps import CommandRunner, PathResolver, WorkspaceBuilder

# Import tool function
from .sayhello import sayhello

logger = logging.getLogger(__name__)


def make_tool(
    runner: CommandRunner,
    workspace: WorkspaceBuilder,
    path_resolver: PathResolver,
) -> List[BaseTool]:
    """
    Factory function for SayHello tools.

    Args:
        runner: Command execution implementation
        workspace: Workspace creation implementation
        path_resolver: Path resolution implementation

    Returns:
        List of SayHello tool instances
    """
    # Set up logging for the sayhello module
    import macroflow_toolkit.tools.sayhello.sayhello as sayhello_module

    sayhello_module.logger = logging.getLogger(f"{__name__}.sayhello")

    # Return the tool - note that filesystem tools don't use the dependencies,
    # but we accept them for consistency with the convention
    return [sayhello]
