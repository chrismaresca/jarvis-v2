# Built in imports
import asyncio
import os
import sys
import time
import json
import base64

# Third party imports
import websockets
import pyaudio

# Module imports
from components.logging import (
    log_tool_call,
    log_error,
    log_info,
    log_warning,
    log_ws_event,
    log_runtime,
    log_debug,
)
from components.microphone import AMicrophone
from components.events import EventHandlers

# Constants
from components.constants import (
    # OpenAI
    BASE_INSTRUCTIONS,
    OPEN_AI_VOICE,
    OPENAI_PREFIX_PADDING_MS,
    OPENAI_SILENCE_THRESHOLD,
    OPENAI_SILENCE_DURATION_MS,
    # Audio
    FORMAT,
    CHANNELS,
    RATE,
    CHUNK,
    SILENCE_DURATION,
    # Websocket
    WS_CLOSE_TIMEOUT,
    WS_PING_INTERVAL,
    WS_PING_TIMEOUT,
    # Assistant
    ASSISTANT_NAME,
)

# Events
from components.events import ServerEvents, ClientEvents

# Tools
from components.tools import base_tools, function_map


class RealtimeAPI:
    """A class for interacting with the OpenAI Real-Time API, handling session setup, message processing, and audio handling."""

    def __init__(self, prompts=None, model=None, tools=None):
        """Initialize the RealtimeAPI client.

        Args:
            prompts (list[str], optional): List of custom prompts to use for the assistant. Defaults to None.
            model (str, optional): OpenAI model identifier to use. Defaults to "gpt-4o-realtime-preview-2024-10-01".
            tools (list[dict], optional): List of custom tools/functions available to the assistant. Defaults to base_tools.
        """

        self.prompts = prompts
        self.model = model or "gpt-4o-realtime-preview-2024-10-01"
        self.api_key = os.getenv("OPENAI_API_KEY")
        if not self.api_key:
            log_error("Please set the OPENAI_API_KEY in your .env file.")
            sys.exit(1)
        self.exit_event = asyncio.Event()
        self.microphone = AMicrophone()

        # Initialize state variables
        self.assistant_reply = ""
        self.audio_chunks = []
        self.response_in_progress = False
        self.function_call = None
        self.function_call_args = ""
        self.response_start_time = None

        # Event Handler
        self.event_handlers = EventHandlers()
        self._register_event_handlers()

        # Tools
        self.tools = tools or base_tools

    # ---------------------------------------------------------------------------------------------------  #
    # ---------------------------------------------------------------------------------------------------  #
    # Session and Process Methods
    # ---------------------------------------------------------------------------------------------------  #
    # ---------------------------------------------------------------------------------------------------  #

    async def run(self):
        """
        Main loop for the RealtimeAPI class, handling connection setup, session initialization, and message processing.
        """
        while True:
            try:
                url = f"wss://api.openai.com/v1/realtime?model={self.model}"
                headers = {
                    "Authorization": f"Bearer {self.api_key}",
                    "OpenAI-Beta": "realtime=v1",
                }
                async with websockets.connect(
                    url,
                    additional_headers=headers,
                    close_timeout=WS_CLOSE_TIMEOUT,  # Close timeout is the time in seconds the server waits after initiating a close handshake before forcibly closing the connection if no response is received.
                    ping_interval=WS_PING_INTERVAL,  # Ping interval is interval in seconds for the server to send a “ping” to check client connectivity and responsiveness.
                    ping_timeout=WS_PING_TIMEOUT,  # Ping timeout is time in seconds the server waits for a client “pong” response after a ping, after which an unresponsive client may trigger a forced close.
                ) as websocket:
                    log_info("{ASSISTANT_NAME} is online.", style="bold green")

                    await self.initialize_session(websocket)
                    ws_task = asyncio.create_task(self.process_ws_messages(websocket))

                    log_info(
                        f"{ASSISTANT_NAME} is listening. Begin the conversation whenever you'd like."
                    )

                    if self.prompts:
                        await self.send_initial_prompts(websocket)
                    else:
                        self.microphone.start_recording()
                        log_info("🎤 Recording started...")

                    await self.send_user_audio(websocket)

                    await ws_task

                break
            except websockets.exceptions.ConnectionClosedError as e:
                if "keepalive ping timeout" in str(e):
                    log_warning(
                        "WebSocket connection lost due to keepalive ping timeout. Reconnecting..."
                    )
                    await asyncio.sleep(1)
                    continue
                else:
                    log_error(f"WebSocket connection closed unexpectedly: {e}")
                    break
            except Exception as e:
                log_error(f"An unexpected error occurred: {e}")
                break
            finally:
                self.microphone.stop_recording()
                self.microphone.close()

    # ---------------------------------------------------------------------------------------------------  #

    async def initialize_session(self, websocket):
        """Initializes a session by sending a session update to the websocket with the necessary parameters."""
        session_update = {
            "type": ClientEvents.SESSION_UPDATE,
            "session": {
                "modalities": ["text", "audio"],
                "instructions": BASE_INSTRUCTIONS,
                "voice": OPEN_AI_VOICE,
                "input_audio_format": "pcm16",
                "output_audio_format": "pcm16",
                "turn_detection": {
                    "type": "server_vad",
                    "threshold": OPENAI_SILENCE_THRESHOLD,
                    "prefix_padding_ms": OPENAI_PREFIX_PADDING_MS,
                    "silence_duration_ms": OPENAI_SILENCE_DURATION_MS,
                },
                "tools": self.tools,
            },
        }
        log_ws_event("Outgoing", session_update)
        await websocket.send(json.dumps(session_update))

    # ---------------------------------------------------------------------------------------------------  #

    async def process_ws_messages(self, websocket):
        """Processes incoming messages from the websocket connection, handling events and delegating to specialized handlers."""
        while True:
            try:
                message = await websocket.recv()
                event = json.loads(message)
                log_ws_event("Incoming", event)
                await self.handle_event(event, websocket)
            except websockets.ConnectionClosed:
                log_warning("WebSocket connection lost.")
                break

    # ---------------------------------------------------------------------------------------------------  #
    # ---------------------------------------------------------------------------------------------------  #
    # Generic Event Handle and Handle Register Methods
    # ---------------------------------------------------------------------------------------------------  #
    # ---------------------------------------------------------------------------------------------------  #

    async def handle_event(self, event, websocket):
        """Handles incoming events from the websocket connection, managing the response flow and triggering specialized event handlers."""
        event_type = event.get("type")
        handler = self.event_handlers.get_handler(event_type)
        if handler:
            await handler(event, websocket)
        else:
            log_warning(f"Unhandled event type: {event_type}")

    def _register_event_handlers(self):
        self.event_handlers.register(
            ServerEvents.RESPONSE_CREATED, self.handle_response_created
        )
        self.event_handlers.register(
            ServerEvents.RESPONSE_OUTPUT_ITEM_ADDED, self.handle_output_item_added
        )
        self.event_handlers.register(
            ServerEvents.RESPONSE_FUNCTION_CALL_ARGUMENTS_DELTA,
            self.handle_function_call_arguments_delta,
        )
        self.event_handlers.register(
            ServerEvents.RESPONSE_FUNCTION_CALL_ARGUMENTS_DONE,
            self.handle_function_call_arguments_done,
        )
        self.event_handlers.register(
            ServerEvents.RESPONSE_TEXT_DELTA, self.handle_response_text_delta
        )
        self.event_handlers.register(
            ServerEvents.RESPONSE_AUDIO_DELTA, self.handle_response_audio_delta
        )
        self.event_handlers.register(
            ServerEvents.RESPONSE_DONE, self.handle_response_done
        )
        self.event_handlers.register(ServerEvents.ERROR, self.handle_error)
        self.event_handlers.register(
            ServerEvents.INPUT_AUDIO_BUFFER_SPEECH_STARTED, self.handle_speech_started
        )
        self.event_handlers.register(
            ServerEvents.INPUT_AUDIO_BUFFER_SPEECH_STOPPED, self.handle_speech_stopped
        )
        self.event_handlers.register(
            ServerEvents.RATE_LIMITS_UPDATED, self.handle_rate_limits_updated
        )

    # ---------------------------------------------------------------------------------------------------  #
    # ---------------------------------------------------------------------------------------------------  #
    # Specialized Event Handler Methods
    # ---------------------------------------------------------------------------------------------------  #
    # ---------------------------------------------------------------------------------------------------  #

    async def handle_response_created(self, event, websocket):
        """
        Handles the response.created event by starting the microphone to receive audio data.
        """
        self.microphone.start_receiving()
        self.response_in_progress = True

    # ---------------------------------------------------------------------------------------------------  #

    async def handle_output_item_added(self, event, websocket):
        """
        Handles an output item added event by extracting the item and checking if it's a function call.

        If it is a function call, we set self.function_call to the item data and self.function_call_args to an empty string (while we await the function call arguments from the agent in subsequent events).
        """
        item = event.get("item", {})
        if item.get("type") == "function_call":
            self.function_call = item
            self.function_call_args = ""

    # ---------------------------------------------------------------------------------------------------  #

    async def handle_function_call_arguments_delta(self, event, websocket):
        """
        As the function call arguments are streamed once a function call is initiated, we append them to self.function_call_args.

        TODO We should probably be checking if the function call was triggered before appending to the arguments.
        """
        self.function_call_args += event.get("delta", "")

    # ---------------------------------------------------------------------------------------------------  #

    async def handle_function_call_arguments_done(self, event, websocket):
        """
        Handler for when the model-generated function call arguments are done (response.function_call_arguments.done).

        - This extracts the function name and call ID, logging the call, and attempting to execute the function.

        - This information is extracted so we can correctly send the conversation.item.create event, which requires an 'item' field consisting of the id, type (message, function_call, function_call_output).
        """
        if self.function_call:
            function_name = self.function_call.get("name")
            call_id = self.function_call.get("call_id")
            log_info(
                f"Function call: {function_name} with args: {self.function_call_args}"
            )
            try:
                args = (
                    json.loads(self.function_call_args)
                    if self.function_call_args
                    else {}
                )
            except json.JSONDecodeError:
                args = {}
            await self.execute_function_call(function_name, call_id, args, websocket)

    # ---------------------------------------------------------------------------------------------------  #

    async def handle_response_text_delta(self, event, websocket):
        """
        Handles the response.text.delta event by appending the delta to self.assistant_reply.
        """
        delta = event.get("delta", "")
        self.assistant_reply += delta
        print(f"Assistant: {delta}", end="", flush=True)

    # ---------------------------------------------------------------------------------------------------  #

    async def handle_response_audio_delta(self, event, websocket):
        """
        Handles the response.audio.delta event by appending the delta to self.audio_chunks in base64 decoded format.
        """
        self.audio_chunks.append(base64.b64decode(event["delta"]))

    # ---------------------------------------------------------------------------------------------------  #

    async def handle_response_done(self, event, websocket):
        """
        Processes response completion by logging duration, playing audio chunks, and stopping microphone input.

        This also ensures that audio chunks is reset -- similar to adding an additional buffer so we can control the response flow.
        """
        if self.response_start_time is not None:
            response_end_time = time.perf_counter()
            response_duration = response_end_time - self.response_start_time
            log_runtime("realtime_api_response", response_duration)
            self.response_start_time = None

        log_info("Assistant response complete.", style="bold blue")
        if self.audio_chunks:
            audio_data = b"".join(self.audio_chunks)
            log_info(
                f"Sending {len(audio_data)} bytes of audio data to self.play_audio_with_silence_buffer()"
            )
            await self.play_audio_with_silence_buffer(audio_data)
            log_info("Finished self.play_audio_with_silence_buffer()")
        self.assistant_reply = ""
        self.audio_chunks = []
        log_info("Calling stop_receiving()")
        self.microphone.stop_receiving()

    # ---------------------------------------------------------------------------------------------------  #

    async def handle_error(self, event, websocket):
        """
        Handles any error event sent from the server. Directly handle two errors here:

        1. "buffer is empty" - no audio data was sent.
        2. "Conversation already has an active response" - the assistant is already responding, so the client should wait for the response to complete before sending more audio

        """
        error_message = event.get("error", {}).get("message", "")
        log_error(f"Error: {error_message}")
        if "buffer is empty" in error_message:
            log_info("Received 'buffer is empty' error, no audio data sent.")
        elif "Conversation already has an active response" in error_message:
            log_info("Received 'active response' error, adjusting response flow.")
            self.response_in_progress = True
        else:
            log_error(f"Unhandled error: {error_message}")

    # ---------------------------------------------------------------------------------------------------  #

    async def handle_speech_started(self, event, websocket):
        """
        Handles the speech_started event by logging that speech has been detected."
        """
        log_info("Speech detected, listening...")

    # ---------------------------------------------------------------------------------------------------  #

    async def handle_speech_stopped(self, event, websocket):
        """
        Handles the end of the user's speech, committing the input audio buffer and triggering a response from the agent via the input_audio_buffer.commit event.

        """
        self.microphone.stop_recording()
        log_info("Speech ended, processing...")
        self.response_start_time = time.perf_counter()
        await websocket.send(
            json.dumps({"type": ClientEvents.INPUT_AUDIO_BUFFER_COMMIT})
        )

    # ---------------------------------------------------------------------------------------------------  #

    async def handle_rate_limits_updated(self, event, websocket):
        self.response_in_progress = False
        self.microphone.is_recording = True
        log_info("Resumed recording after rate_limits.updated")

    # ---------------------------------------------------------------------------------------------------  #
    # ---------------------------------------------------------------------------------------------------  #
    # Audio Execution Methods
    # ---------------------------------------------------------------------------------------------------  #
    # ---------------------------------------------------------------------------------------------------  #

    async def send_initial_prompts(self, websocket):
        """
        Sends initial prompts to the conversation context via the client event 'conversation.item.create'.
        Only used if prompts are provided at initialization. This can be used to either provide a conversation starter or to provide context for the assistant.
        """
        log_info(f"Sending {len(self.prompts)} prompts: {self.prompts}")
        content = [{"type": "input_text", "text": prompt} for prompt in self.prompts]
        event = {
            "type": ClientEvents.CONVERSATION_ITEM_CREATE,
            "item": {
                "type": "message",
                "role": "user",
                "content": content,
            },
        }
        log_ws_event("Outgoing", event)
        await websocket.send(json.dumps(event))

        # Trigger the assistant's response
        response_create_event = {"type": ClientEvents.RESPONSE_CREATE}
        log_ws_event("Outgoing", response_create_event)
        await websocket.send(json.dumps(response_create_event))

    # ---------------------------------------------------------------------------------------------------  #

    async def send_user_audio(self, websocket):
        """
        Streams microphone audio data and appends audio bytes to the input buffer via the client event 'input_audio_buffer.append'.
        The buffer is a temporary storage for audio data until it is committed to the conversation context or discarded.

        - When using Server VAD, the buffer is committed automatically by the server.

        - When Server VAD is disabled, the buffer must be committed manually via the client event 'input_audio_buffer.commit'. You can also discard the buffer manually via the client event 'input_audio_buffer.clear'.
        """
        try:
            while not self.exit_event.is_set():
                await asyncio.sleep(
                    0.1
                )  # Ensure all audio data is accumulated before sending

                # Check if the microphone is in recording mode and audio data is available
                if not self.microphone.is_receiving:
                    audio_chunk = self.microphone.get_audio_data()
                    if audio_chunk and len(audio_chunk) > 0:
                        encoded_audio = base64.b64encode(audio_chunk).decode("utf-8")
                        if encoded_audio:
                            audio_event = {
                                "type": ClientEvents.INPUT_AUDIO_BUFFER_APPEND,
                                "audio": encoded_audio,
                            }
                            log_ws_event("Outgoing", audio_event)
                            await websocket.send(json.dumps(audio_event))
                        else:
                            log_debug("No audio data is available to send")
                else:
                    await asyncio.sleep(
                        0.1
                    )  # Brief delay if microphone is in receiving mode

        except KeyboardInterrupt:
            log_info("User terminated connection. Closing now.")

        finally:
            # Ensure cleanup of resources
            self.exit_event.set()
            self.microphone.stop_recording()
            self.microphone.close()
            await websocket.close()

    # ---------------------------------------------------------------------------------------------------  #

    async def play_audio_with_silence_buffer(self, audio_data):
        """
        Plays received audio data through the system's speakers with a smooth silence buffer at the end.
        """
        audio_interface = pyaudio.PyAudio()
        playback_stream = audio_interface.open(
            format=FORMAT, channels=CHANNELS, rate=RATE, output=True
        )

        # Stream the audio data to the output
        playback_stream.write(audio_data)

        # Append silence to ensure smooth playback without abrupt cuts or pops
        silence_samples = (
            int(RATE * SILENCE_DURATION) * CHANNELS * 2
        )  # 2 bytes per sample for 16-bit audio
        playback_stream.write(b"\x00" * silence_samples)

        # Brief pause to ensure audio completes before closing the stream
        await asyncio.sleep(0.5)

        # Close the stream and terminate the PyAudio instance
        playback_stream.stop_stream()
        playback_stream.close()
        audio_interface.terminate()
        log_debug("Agent completed audio playback")

    async def send_error_message_to_assistant(self, error_message, websocket):
        """
        Adds an error message to the conversation's context via the client event 'conversation.item.create'.
        """
        error_item = {
            "type": ClientEvents.CONVERSATION_ITEM_CREATE,
            "item": {
                "type": "message",
                "role": "assistant",
                "content": [{"type": "text", "text": error_message}],
            },
        }
        log_ws_event("Outgoing", error_item)
        await websocket.send(json.dumps(error_item))

    # ---------------------------------------------------------------------------------------------------  #
    # Function Execution Method
    # ---------------------------------------------------------------------------------------------------  #

    async def execute_function_call(self, function_name, call_id, args, websocket):
        """
        Executes a function call from the assistant and adds the result to the conversation context via the client event 'conversation.item.create'.
        """
        if function_name in function_map:
            try:
                result = await function_map[function_name](**args)
                log_tool_call(function_name, args, result)
            except Exception as e:
                error_message = f"Error executing function '{function_name}': {str(e)}"
                log_error(error_message)
                result = {"error": error_message}
                await self.send_error_message_to_assistant(error_message, websocket)
        else:
            error_message = f"Function '{function_name}' not found."
            log_error(error_message)
            result = {"error": error_message}
            await self.send_error_message_to_assistant(error_message, websocket)

        function_call_output = {
            "type": ClientEvents.CONVERSATION_ITEM_CREATE,
            "item": {
                "type": "function_call_output",
                "call_id": call_id,
                "output": json.dumps(result),
            },
        }
        log_ws_event("Outgoing", function_call_output)
        await websocket.send(json.dumps(function_call_output))
        await websocket.send(json.dumps({"type": ClientEvents.RESPONSE_CREATE}))

        # Reset function call state
        self.function_call = None
        self.function_call_args = ""
