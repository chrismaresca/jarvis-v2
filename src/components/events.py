# Client Events (Events we send to OpenAI)
class ClientEvents:
    SESSION_UPDATE = "session.update"
    CONVERSATION_ITEM_CREATE = "conversation.item.create"
    RESPONSE_CREATE = "response.create"
    INPUT_AUDIO_BUFFER_APPEND = "input_audio_buffer.append"
    INPUT_AUDIO_BUFFER_COMMIT = "input_audio_buffer.commit"

# Server Events (Events we receive from OpenAI)
class ServerEvents:
    # Session events
    SESSION_CREATED = "session.created"
    SESSION_UPDATED = "session.updated"

    # Response events
    RESPONSE_CREATED = "response.created"
    RESPONSE_DONE = "response.done"

    # Text events
    RESPONSE_TEXT_DELTA = "response.text.delta"
    RESPONSE_TEXT_DONE = "response.text.done"

    # Audio events
    RESPONSE_AUDIO_DELTA = "response.audio.delta"
    RESPONSE_AUDIO_DONE = "response.audio.done"

    # Function call events
    RESPONSE_OUTPUT_ITEM_ADDED = "response.output_item.added"
    RESPONSE_FUNCTION_CALL_ARGUMENTS_DELTA = "response.function_call_arguments.delta"
    RESPONSE_FUNCTION_CALL_ARGUMENTS_DONE = "response.function_call_arguments.done"

    # Speech detection events
    INPUT_AUDIO_BUFFER_SPEECH_STARTED = "input_audio_buffer.speech_started"
    INPUT_AUDIO_BUFFER_SPEECH_STOPPED = "input_audio_buffer.speech_stopped"

    # Rate limit events
    RATE_LIMITS_UPDATED = "rate_limits.updated"

    # Error events
    ERROR = "error"
    
    
class EventHandlers:
    def __init__(self):
        self._handlers = {}

    def register(self, event_type, handler):
        """Register a handler for an event type"""
        self._handlers[event_type] = handler

    def get_handler(self, event_type):
        """Get the handler for a specific event type"""
        return self._handlers.get(event_type)