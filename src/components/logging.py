import logging
from rich.logging import RichHandler
from rich.console import Console
from rich.text import Text

console = Console()

# -------------------------------------------------------------------------------------------------
# Logging Setup
# -------------------------------------------------------------------------------------------------


# Constants for WebSocket event types and their emojis
EVENT_EMOJIS = {
    "session.update": "🛠️",
    "session.created": "🔌",
    "session.updated": "🔄",
    "input_audio_buffer.append": "🎤",
    "input_audio_buffer.commit": "✅",
    "input_audio_buffer.speech_started": "🗣️",
    "input_audio_buffer.speech_stopped": "🤫",
    "input_audio_buffer.cleared": "🧹",
    "input_audio_buffer.committed": "📨",
    "conversation.item.create": "📥",
    "conversation.item.delete": "🗑️",
    "conversation.item.truncate": "✂️",
    "conversation.item.created": "📤",
    "conversation.item.deleted": "🗑️",
    "conversation.item.truncated": "✂️",
    "response.create": "➡️",
    "response.created": "📝",
    "response.output_item.added": "➕",
    "response.output_item.done": "✅",
    "response.text.delta": "✍️",
    "response.text.done": "📝",
    "response.audio.delta": "🔊",
    "response.audio.done": "🔇",
    "response.done": "✔️",
    "response.cancel": "⛔",
    "response.function_call_arguments.delta": "📥",
    "response.function_call_arguments.done": "📥",
    "rate_limits.updated": "⏳",
    "error": "❌",
    "conversation.item.input_audio_transcription.completed": "📝",
    "conversation.item.input_audio_transcription.failed": "⚠️",
}


def setup_logging():
    """
    Set up logging with Rich for enhanced console output.
    Returns:
        logging.Logger: Configured logger for application logging.
    """
    logger = logging.getLogger("realtime_api")
    logger.setLevel(logging.INFO)
    handler = RichHandler(rich_tracebacks=True, console=console)
    formatter = logging.Formatter("%(message)s", datefmt="[%X]")
    handler.setFormatter(formatter)
    logger.addHandler(handler)
    logger.propagate = False
    return logger


logger = setup_logging()


# -------------------------------------------------------------------------------------------------
# Logging functions
# -------------------------------------------------------------------------------------------------


def log_ws_event(direction, event):
    """
    Logs WebSocket events with directional indicators and emojis.

    Args:
        direction (str): "Outgoing" or "Incoming" direction of the event.
        event (dict): Event details, must contain "type" as key.
    """
    event_type = event.get("type", "Unknown")
    emoji = EVENT_EMOJIS.get(event_type, "❓")
    icon = "⬆️ - Out" if direction == "Outgoing" else "⬇️ - In"
    style = "bold cyan" if direction == "Outgoing" else "bold green"
    logger.info(Text(f"{emoji} {icon} {event_type}", style=style))


def log_tool_call(function_name, args, result):
    """
    Logs function calls and their results.

    Args:
        function_name (str): Name of the function called.
        args (dict): Arguments passed to the function.
        result (Any): Result of the function call.
    """
    logger.info(
        Text(
            f"🛠️ Calling function: {function_name} with args: {args}",
            style="bold magenta",
        )
    )
    logger.info(Text(f"🛠️ Function call result: {result}", style="bold yellow"))


def log_error(message):
    """
    Logs an error message.

    Args:
        message (str): The error message to log.
    """
    logger.error(Text(message, style="bold red"))


def log_info(message, style="bold white"):
    """
    Logs an informational message with optional styling.

    Args:
        message (str): The message to log.
        style (str): Style to apply to the message.
    """
    logger.info(Text(message, style=style))


def log_debug(message):
    """
    Logs a debug message.

    Args:
        message (str): The debug message to log.
    """
    logger.debug(Text(message, style="dim white"))


def log_warning(message):
    """
    Logs a warning message.

    Args:
        message (str): The warning message to log.
    """
    logger.warning(Text(message, style="bold yellow"))


def log_runtime(operation, duration):
    """
    Logs the runtime duration of an operation.

    Args:
        operation (str): Name of the operation being timed
        duration (float): Duration of the operation in seconds
    """
    logger.info(Text(f"⏱️ {operation} took {duration:.2f} seconds", style="bold blue"))
