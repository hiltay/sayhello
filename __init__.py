# Copyright (c) 2025 Bytedance Ltd. and/or its affiliates
# SPDX-License-Identifier: MIT

"""
SayHello tool package for MacroFlow.

This package provides greeting functionality as a demonstration
of how to integrate external tools into MacroFlow.
"""

# Import the MacroFlow integration
from .macroflow_tool import sayhello_batch_tool, sayhello_tool

__all__ = ["sayhello_tool", "sayhello_batch_tool"]

