#!/usr/bin/env python3
"""
SayHello CLI - Command line interface for sayhello tool.

This CLI allows calling sayhello from the command line or other processes.
"""

import argparse
import json
import logging
import sys

from .main import sayhello, sayhello_advanced

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)
logger = logging.getLogger(__name__)


def main():
    """Main CLI entry point."""
    parser = argparse.ArgumentParser(
        description="SayHello - Generate personalized greetings",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  sayhello --name Alice
  sayhello --name Bob --language zh
  sayhello --name Charlie --language es --json
        """,
    )
    
    # Required arguments
    parser.add_argument(
        "--name",
        type=str,
        required=True,
        help="Name of the person to greet",
    )
    
    # Optional arguments
    parser.add_argument(
        "--language",
        type=str,
        default="en",
        choices=["en", "zh", "es", "fr"],
        help="Language code for greeting (default: en)",
    )
    
    parser.add_argument(
        "--json",
        action="store_true",
        help="Output result as JSON",
    )
    
    parser.add_argument(
        "--simple",
        action="store_true",
        help="Use simple greeting (just the message)",
    )
    
    parser.add_argument(
        "--verbose",
        action="store_true",
        help="Enable verbose logging",
    )
    
    args = parser.parse_args()
    
    # Configure logging level
    if args.verbose:
        logging.getLogger().setLevel(logging.DEBUG)
    
    try:
        # Call the appropriate function
        if args.simple:
            # Simple greeting
            result = sayhello(args.name)
            
            if args.json:
                output = {
                    "success": True,
                    "greeting": result,
                    "name": args.name,
                }
                print(json.dumps(output, ensure_ascii=False, indent=2))
            else:
                print(result)
        else:
            # Advanced greeting with language support
            result = sayhello_advanced(args.name, args.language)
            
            if args.json:
                output = {
                    "success": True,
                    "greeting": result["greeting"],
                    "language": result["language"],
                    "name": result["name"],
                    "message_length": result["length"],
                }
                print(json.dumps(output, ensure_ascii=False, indent=2))
            else:
                print(result["greeting"])
        
        return 0
        
    except ValueError as e:
        logger.error(f"Validation error: {e}")
        if args.json:
            error_output = {
                "success": False,
                "error": str(e),
            }
            print(json.dumps(error_output, ensure_ascii=False, indent=2))
        else:
            print(f"Error: {e}", file=sys.stderr)
        return 1
        
    except Exception as e:
        logger.error(f"Unexpected error: {e}")
        if args.json:
            error_output = {
                "success": False,
                "error": f"Unexpected error: {str(e)}",
            }
            print(json.dumps(error_output, ensure_ascii=False, indent=2))
        else:
            print(f"Unexpected error: {e}", file=sys.stderr)
        return 2


if __name__ == "__main__":
    sys.exit(main())

