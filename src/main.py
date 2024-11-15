# Built in imports
import asyncio
import argparse
import os

# Third party imports
from dotenv import load_dotenv

# Local imports
from components.logging import (
    log_error,
    log_info,

)

# Client import
from components.client import RealtimeAPI

# Load environment variables
load_dotenv()


def main():
    log_info(f"Starting realtime API...")
    
    # Parse arguments
    parser = argparse.ArgumentParser(description="Realtime API with optional prompts")
    parser.add_argument("--prompts", type=str, help="Prompts separated by |")
    args = parser.parse_args()
    
    prompts = args.prompts.split("|") if args.prompts else None

    realtime_api_instance = RealtimeAPI(prompts=prompts)
    
    try:
        asyncio.run(realtime_api_instance.run())
    except KeyboardInterrupt:
        log_info("Program terminated by user")
    except Exception as e:
        log_error(f"An unexpected error occurred: {e}")


if __name__ == "__main__":
    print("Press Ctrl+C to exit the program.")
    main()