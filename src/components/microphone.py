import pyaudio
import queue
import logging
from components.constants import FORMAT, CHANNELS, RATE, CHUNK

class AMicrophone:
    """Handles asynchronous microphone operations for recording and streaming audio input."""

    def __init__(self):
        """Initializes audio stream and internal queue for audio data buffering."""
        self.p = pyaudio.PyAudio()
        self.stream = self.p.open(
            format=FORMAT,
            channels=CHANNELS,
            rate=RATE,
            input=True,
            frames_per_buffer=CHUNK,
            stream_callback=self._callback,
        )
        self.queue = queue.Queue()
        self.is_recording = False
        self.is_receiving = False
        logging.info("AsyncMicrophone initialized and ready")

    def _callback(self, in_data, frame_count, time_info, status):
        """Processes incoming audio data based on current recording status."""
        if self.is_recording and not self.is_receiving:
            self.queue.put(in_data)
        return (None, pyaudio.paContinue)

    def start_recording(self):
        """Begins capturing audio data into the internal queue."""
        self.is_recording = True
        logging.info("Recording started")

    def stop_recording(self):
        """Stops capturing audio data, pausing the recording process."""
        self.is_recording = False
        logging.info("Recording stopped")

    def start_receiving(self):
        """Enables receiving mode, suspending audio recording."""
        self.is_receiving = True
        self.is_recording = False
        logging.info("Receiving assistant responses enabled")

    def stop_receiving(self):
        """Disables receiving mode, allowing recording to resume if started."""
        self.is_receiving = False
        logging.info("Receiving assistant responses disabled")

    def get_audio_data(self):
        """Retrieves and clears buffered audio data from the internal queue."""
        data = b""
        while not self.queue.empty():
            data += self.queue.get()
        return data if data else None

    def close(self):
        """Closes the audio stream and terminates PyAudio instance."""
        self.stream.stop_stream()
        self.stream.close()
        self.p.terminate()
        logging.info("AsyncMicrophone stream closed")
