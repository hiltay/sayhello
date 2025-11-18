"""
SayHello tool package for MacroFlow.

This package provides greeting functionality as a demonstration
of how to integrate external tools into MacroFlow.
"""

# Main exports - factory function for MacroFlow toolkit
from .macroflow_tool import make_tool

__all__ = ["make_tool"]
