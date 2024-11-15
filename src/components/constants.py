# third party imports
import pyaudio


# ---------------------------------------------------------------------------------------------------  #
# Assistant instructions
# ---------------------------------------------------------------------------------------------------  #

ASSISTANT_NAME = "Jarvis"
MY_NAME = "Chris"

BASE_INSTRUCTIONS = (
    f"You are {ASSISTANT_NAME}, your role is to provide insightful and supportive responses tailored to {MY_NAME}'s needs. "
    f"Maintain a helpful, informative approach. Similar to Jarvis from Iron Man. "
    f"Below are some additional instructions to help you understand your role and how to interact with {MY_NAME}: "
    f"Make sure to always keep your responses as concise and to the point as possible."
    f"Never break character."
)

# ---------------------------------------------------------------------------------------------------  #
# OpenAI Real-Time API parameters
# ---------------------------------------------------------------------------------------------------  #

OPEN_AI_VOICE = "echo"
OPENAI_PREFIX_PADDING_MS = 300
OPENAI_SILENCE_THRESHOLD = 0.5
OPENAI_SILENCE_DURATION_MS = 700

# ---------------------------------------------------------------------------------------------------  #
# Websocket connection parameters
# ---------------------------------------------------------------------------------------------------  #

WS_CLOSE_TIMEOUT = 120
WS_PING_INTERVAL = 30
WS_PING_TIMEOUT = 10

# ---------------------------------------------------------------------------------------------------  #
# Audio parameters
# ---------------------------------------------------------------------------------------------------  #

# Audio recording parameters
CHUNK = 1024
FORMAT = pyaudio.paInt16
CHANNELS = 1
RATE = 24000
SILENCE_DURATION = 0.2


