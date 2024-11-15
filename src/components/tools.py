# TODO: REMOVE all this
# Functions
import random
from datetime import datetime


async def get_random_number():
    return {"random_number": random.randint(1, 100)}


async def get_current_time():
    return {"current_time": datetime.now().strftime("%Y-%m-%d %H:%M:%S")}


# ---------------------------------------------------------------------------------------------------  #
# Tools
# ---------------------------------------------------------------------------------------------------  #

function_map = {
    "get_current_time": get_current_time,
    "get_random_number": get_random_number,
}


base_tools = [
    {
        "type": "function",
        "name": "get_current_time",
        "description": "Returns the current time.",
        "parameters": {
            "type": "object",
            "properties": {},
            "required": [],
        },
    },
    {
        "type": "function",
        "name": "get_random_number",
        "description": "Returns a random number between 1 and 100.",
        "parameters": {
            "type": "object",
            "properties": {},
            "required": [],
        },
    },
]
