# Event Documentation

This document details the various events emitted by the server, including their descriptions, purposes, fields, emission conditions, and usage guidelines.

---

## Event Types

### 1. `error` Event
**Description**  
The `error` event is emitted whenever an error occurs during communication or processing. This could stem from client-side issues (e.g., invalid requests) or server-side problems (e.g., internal errors).

**Purpose**  
To notify the client of any issues preventing successful processing of a request or event, enabling graceful exception handling.

**Fields**
- `event_id`: Unique identifier for the event
- `type`: "error"
- `error`: Object detailing the error:
  - `type`: Category of the error (e.g., "invalid_request_error", "transcription_error")
  - `code`: Specific error code (e.g., "invalid_event", "audio_unintelligible")
  - `message`: Human-readable error description
  - `param`: Additional parameter information (if applicable)
  - `event_id`: ID of the related event, if relevant

**When It's Emitted**
- When the server encounters an error while processing a client event
- In case of an internal server error affecting the session

**Usage**  
Clients should:
- Listen for `error` events to handle exceptions (e.g., logging, retrying, user notification)

---

### 2. `session.created` Event
**Description**  
Automatically emitted when a new WebSocket connection is established, providing initial session configuration.

**Purpose**  
To confirm session creation and inform the client about default settings.

**Fields**
- `event_id`: Unique identifier for the event
- `type`: "session.created"
- `session`: Object with session configuration:
  - `id`: Session ID
  - `object`: "realtime.session"
  - `model`: AI model in use (e.g., "gpt-4o-realtime-preview-2024-10-01")
  - `modalities`: Communication modes (e.g., ["text", "audio"])
  - Additional configuration fields:
    - `instructions`
    - `voice`
    - `input_audio_format`
    - `output_audio_format`
    - `input_audio_transcription`
    - `turn_detection`
    - `tools`
    - `tool_choice`
    - `temperature`
    - `max_response_output_tokens`

**When It's Emitted**  
Immediately after establishing a new WebSocket connection.

**Usage**  
Clients use this event to:
- Confirm session activation
- Retrieve default configurations
- Adjust client-side settings based on session parameters

### 3. `session.updated` Event
**Description**  
Sent in response to a `session.update` event from the client, reflecting session configuration changes.

**Purpose**  
To acknowledge updates and provide the client with the new configuration.

**Fields**
- `event_id`: Unique identifier for the event
- `type`: "session.updated"
- `session`: Updated session configuration (same structure as in `session.created`)

**When It's Emitted**  
After the client sends a `session.update` event.

**Usage**  
Clients can:
- Verify requested changes
- Adjust behavior according to new settings
- Update UI elements

---

### 4. `conversation.created` Event
**Description**  
Indicates the creation of a new conversation within the session.

**Purpose**  
To inform the client of established conversation context for message exchanges.

**Fields**
- `event_id`: Unique identifier for the event
- `type`: "conversation.created"
- `conversation`: Object representing the conversation:
  - `id`: Conversation ID
  - `object`: "realtime.conversation"

**When It's Emitted**  
Right after the session is created.

**Usage**  
Clients use this event to:
- Track the conversation ID
- Initialize data structures
- Update UI components

---

### 5. `conversation.item.created` Event
**Description**  
Emitted when a new item (e.g., message, function call) is added to the conversation history.

**Purpose**  
To notify the client of an added item, ensuring synchronized conversation histories.

**Fields**
- `event_id`: Unique identifier for the event
- `type`: "conversation.item.created"
- `previous_item_id`: ID of the preceding item
- `item`: Object representing the new item:
  - `id`: Unique ID
  - `object`: "realtime.item"
  - `type`: Type of item (e.g., "message", "function_call")
  - `status`: Current status (e.g., "completed", "in_progress")
  - `role`: Role associated with the item (e.g., "user", "assistant")
  - `content`: Array of content parts

**When It's Emitted**
- After processing a user's message
- When generating a response

**Usage**  
Clients should:
- Update conversation histories
- Display messages or actions
- Maintain synchronization between client-side and server-side states

---

### 6. `conversation.item.input_audio_transcription.completed` Event
**Description**  
Emitted when the server completes transcription of audio input from the user.

**Purpose**  
To provide the client with text transcription of the audio message.

**Fields**
- `event_id`: Unique identifier for the event
- `type`: "conversation.item.input_audio_transcription.completed"
- `item_id`: ID of the user message item
- `content_index`: Index of the content part with audio
- `transcript`: Transcribed text

**When It's Emitted**  
After the server successfully transcribes audio input.

**Usage**  
Clients can:
- Display the transcribed text to the user
- Use the transcript for processing or analytics
- Update UI components

---

### 7. `response.created` Event
**Description**  
Indicates that the server has started generating a response.

**Purpose**  
To inform the client that response generation has begun.

**Fields**
- `event_id`: Unique identifier for the event
- `type`: "response.created"
- `response`: Object containing:
  - `id`: Response ID
  - `object`: "realtime.response"
  - `status`: Current status
  - `output`: Array of response items
  - `usage`: Token usage information

**When It's Emitted**  
When the server begins processing a response.

**Usage**  
Clients should:
- Prepare for incoming response data
- Update UI to show response generation status
- Track response progress

---

### 8. `response.done` Event
**Description**  
Signals completion of response generation.

**Purpose**  
To indicate that all response data has been sent.

**Fields**
- `event_id`: Unique identifier for the event
- `type`: "response.done"
- `response`: Final response object with complete data

**When It's Emitted**  
After all response content has been transmitted.

**Usage**  
Clients should:
- Finalize response display
- Update conversation state
- Clean up any temporary UI elements

---

### 9. `conversation.item.truncated` Event
**Description**  
Sent when a conversation item (typically an assistant's message) is truncated.

**Purpose**  
To synchronize the conversation state when messages are cut short, especially during interruptions.

**Fields**
- `event_id`: Unique identifier for the event
- `type`: "conversation.item.truncated"
- `item_id`: ID of the truncated item
- `content_index`: Index of the truncated content part
- `audio_end_ms`: Timestamp where truncation occurred

**When It's Emitted**  
After processing a truncation request from the client.

**Usage**  
Clients should:
- Update conversation display
- Adjust audio playback state
- Sync conversation history

---

### 10. `input_audio_buffer.committed` Event
**Description**  
Confirms that an audio buffer has been successfully processed and committed.

**Purpose**  
To acknowledge that audio input has been received and will be processed.

**Fields**
- `event_id`: Unique identifier for the event
- `type`: "input_audio_buffer.committed"
- `previous_item_id`: ID of the preceding conversation item
- `item_id`: ID of the new message item being created

**When It's Emitted**
- After client commits audio buffer
- When server auto-commits in VAD mode

**Usage**  
Clients should:
- Update recording status
- Prepare for transcription events
- Handle UI state changes

---

### 11. `input_audio_buffer.speech_started` Event
**Description**  
Indicates that speech has been detected in the audio input.

**Purpose**  
To provide real-time feedback about voice activity detection.

**Fields**
- `event_id`: Unique identifier for the event
- `type`: "input_audio_buffer.speech_started"
- `audio_start_ms`: Timestamp of speech detection
- `item_id`: ID of the associated message item

**When It's Emitted**  
When the server's VAD system detects speech in the audio stream.

**Usage**  
Clients can:
- Update UI to show active speech detection
- Start recording indicators
- Handle interruption logic

---

### 12. `input_audio_buffer.speech_stopped` Event
**Description**  
Signals that speech in the audio input has ended.

**Purpose**  
To indicate the end of speech detection and prepare for processing.

**Fields**
- `event_id`: Unique identifier for the event
- `type`: "input_audio_buffer.speech_stopped"
- `audio_end_ms`: Timestamp when speech ended
- `item_id`: ID of the associated message item

**When It's Emitted**  
When the VAD system determines speech has stopped.

**Usage**  
Clients should:
- Update recording UI
- Prepare for response
- Handle audio processing state

---

### 13. `response.text.delta` Event
**Description**  
Provides incremental updates to text being generated.

**Purpose**  
To enable real-time streaming of text responses.

**Fields**
- `event_id`: Unique identifier for the event
- `type`: "response.text.delta"
- `response_id`: ID of the current response
- `item_id`: ID of the message item
- `output_index`: Index in the response output array
- `content_index`: Index of the content part
- `delta`: New text content

**When It's Emitted**  
Continuously during text generation.

**Usage**  
Clients should:
- Update text display incrementally
- Handle streaming UI updates
- Buffer text appropriately

---

### 14. `response.audio.delta` Event
**Description**  
Streams chunks of generated audio data.

**Purpose**  
To enable real-time audio playback of responses.

**Fields**
- `event_id`: Unique identifier for the event
- `type`: "response.audio.delta"
- `response_id`: ID of the current response
- `item_id`: ID of the message item
- `output_index`: Index in the response output array
- `content_index`: Index of the content part
- `delta`: Base64-encoded audio data

**When It's Emitted**  
Continuously during audio generation.

**Usage**  
Clients should:
- Buffer audio data
- Handle streaming playback
- Manage audio resources efficiently

---

### 15. `response.audio_transcript.delta` Event
**Description**  
Provides real-time transcription updates for generated audio.

**Purpose**  
To enable synchronized captions/subtitles with audio playback.

**Fields**
- `event_id`: Unique identifier for the event
- `type`: "response.audio_transcript.delta"
- `response_id`: ID of the current response
- `item_id`: ID of the message item
- `output_index`: Index in response output array
- `content_index`: Index of content part
- `delta`: Incremental transcript text

**When It's Emitted**  
During audio generation, as transcription becomes available.

**Usage**  
Clients should:
- Display real-time captions
- Sync transcript with audio playback
- Update accessibility features

---

### 16. `response.function_call_arguments.delta` Event
**Description**  
Streams partial function call argument data as it's generated.

**Purpose**  
To provide real-time updates of function call parameters.

**Fields**
- `event_id`: Unique identifier for the event
- `type`: "response.function_call_arguments.delta"
- `response_id`: ID of the current response
- `item_id`: ID of the message item
- `output_index`: Index in response output array
- `call_id`: ID of the function call
- `delta`: Partial JSON string of arguments

**When It's Emitted**  
During function call argument generation.

**Usage**  
Clients should:
- Buffer argument data
- Prepare for function execution
- Handle partial JSON parsing

---

### 17. `response.content_part.added` Event
**Description**  
Signals the start of a new content part in the response.

**Purpose**  
To prepare the client for incoming content of a specific type.

**Fields**
- `event_id`: Unique identifier for the event
- `type`: "response.content_part.added"
- `response_id`: ID of the current response
- `item_id`: ID of the message item
- `output_index`: Index in response output array
- `content_index`: Index of the new content part
- `part`: Object describing content type and metadata

**When It's Emitted**  
Before streaming content for a new part begins.

**Usage**  
Clients should:
- Initialize appropriate content handlers
- Prepare UI elements
- Set up content-specific state

---

### 18. `response.content_part.done` Event
**Description**  
Indicates completion of a content part's streaming.

**Purpose**  
To signal that a specific content part is complete.

**Fields**
- `event_id`: Unique identifier for the event
- `type`: "response.content_part.done"
- `response_id`: ID of the current response
- `item_id`: ID of the message item
- `output_index`: Index in response output array
- `content_index`: Index of completed content part
- `part`: Final state of the content part

**When It's Emitted**  
After all data for a content part has been sent.

**Usage**  
Clients should:
- Finalize content display/playback
- Clean up content-specific resources
- Update UI state

---

### 19. `response.output_item.added` Event
**Description**  
Indicates addition of a new output item to the response.

**Purpose**  
To prepare the client for a new message or function call.

**Fields**
- `event_id`: Unique identifier for the event
- `type`: "response.output_item.added"
- `response_id`: ID of the current response
- `output_index`: Index of new output item
- `item`: Initial state of the output item

**When It's Emitted**  
When the server starts generating a new output item.

**Usage**  
Clients should:
- Initialize item-specific handlers
- Prepare UI for new content
- Set up item state tracking

---

### 20. `response.output_item.done` Event
**Description**  
Signals completion of an output item in the response.

**Purpose**  
To indicate that all content for an output item has been sent.

**Fields**
- `event_id`: Unique identifier for the event
- `type`: "response.output_item.done"
- `response_id`: ID of the current response
- `output_index`: Index of completed output item
- `item`: Final state of the output item

**When It's Emitted**  
After all content parts for an item are complete.

**Usage**  
Clients should:
- Finalize item display
- Update conversation state
- Clean up item-specific resources

---

### 21. `response.text.done` Event
**Description**  
Indicates completion of text generation for a content part.

**Purpose**  
To signal that all text content has been sent for a particular part.

**Fields**
- `event_id`: Unique identifier for the event
- `type`: "response.text.done"
- `response_id`: ID of the current response
- `item_id`: ID of the message item
- `output_index`: Index in response output array
- `content_index`: Index of content part
- `text`: Complete text content

**When It's Emitted**  
After all text deltas have been sent.

**Usage**  
Clients should:
- Finalize text display
- Verify text completeness
- Trigger any post-text-generation actions

---

### 22. `response.audio.done` Event
**Description**  
Signals completion of audio generation for a content part.

**Purpose**  
To indicate that all audio data has been streamed.

**Fields**
- `event_id`: Unique identifier for the event
- `type`: "response.audio.done"
- `response_id`: ID of the current response
- `item_id`: ID of the message item
- `output_index`: Index in response output array
- `content_index`: Index of content part
- `duration_ms`: Total duration of the audio

**When It's Emitted**  
After all audio chunks have been transmitted.

**Usage**  
Clients should:
- Complete audio playback
- Update audio progress indicators
- Clean up audio resources

---

### 23. `response.audio_transcript.done` Event
**Description**  
Indicates completion of audio transcription streaming.

**Purpose**  
To provide the final, complete transcript of generated audio.

**Fields**
- `event_id`: Unique identifier for the event
- `type`: "response.audio_transcript.done"
- `response_id`: ID of the current response
- `item_id`: ID of the message item
- `output_index`: Index in response output array
- `content_index`: Index of content part
- `transcript`: Complete transcript text

**When It's Emitted**  
After all transcript deltas have been sent.

**Usage**  
Clients should:
- Display final transcript
- Update caption/subtitle displays
- Enable transcript-related features

---

### 24. `response.function_call_arguments.done` Event
**Description**  
Signals completion of function call argument generation.

**Purpose**  
To provide the complete, valid JSON arguments for a function call.

**Fields**
- `event_id`: Unique identifier for the event
- `type`: "response.function_call_arguments.done"
- `response_id`: ID of the current response
- `item_id`: ID of the message item
- `output_index`: Index in response output array
- `call_id`: ID of the function call
- `arguments`: Complete JSON string of arguments

**When It's Emitted**  
After all argument deltas have been sent.

**Usage**  
Clients should:
- Parse complete arguments
- Execute function call
- Handle function results

---

### 25. `rate_limits.updated` Event
**Description**  
Provides updated rate limit information for the session.

**Purpose**  
To inform clients about current usage and remaining capacity.

**Fields**
- `event_id`: Unique identifier for the event
- `type`: "rate_limits.updated"
- `rate_limits`: Array of limit objects:
  - `type`: Type of limit
  - `limit`: Maximum allowed value
  - `remaining`: Remaining capacity
  - `reset_at`: Timestamp when limit resets

**When It's Emitted**
- After consuming resources
- When limits are reset
- Upon request for limit information

**Usage**  
Clients should:
- Monitor resource usage
- Implement rate limiting logic
- Plan request timing

---

### 26. `input_audio_buffer.cleared` Event
**Description**  
Confirms that the input audio buffer has been cleared.

**Purpose**  
To acknowledge successful clearing of the audio buffer.

**Fields**
- `event_id`: Unique identifier for the event
- `type`: "input_audio_buffer.cleared"

**When It's Emitted**  
After processing an audio buffer clear request.

**Usage**  
Clients should:
- Reset audio recording state
- Clear audio-related UI elements
- Prepare for new audio input

---

## Best Practices

1. **Error Handling**
   - Always implement error event listeners
   - Provide appropriate user feedback
   - Include retry logic where appropriate

2. **State Management**
   - Maintain synchronized state with server
   - Track conversation and response IDs
   - Update UI based on event status

3. **Resource Management**
   - Clean up resources when sessions end
   - Handle audio streams appropriately
   - Monitor rate limits and usage

4. **User Experience**
   - Show appropriate loading states
   - Provide feedback for all operations
   - Handle interruptions gracefully

## Rate Limits and Usage

The server enforces rate limits on various operations. Monitor the following:
- Token usage per response
- Requests per minute
- Audio duration limits
- Concurrent sessions

## Security Considerations

1. **Authentication**
   - Maintain secure session tokens
   - Handle session expiration appropriately

2. **Data Privacy**
   - Handle user data according to privacy policies
   - Clear sensitive data when sessions end

3. **Input Validation**
   - Validate all client-side input
   - Handle malformed responses gracefully

---

For detailed implementation examples and code samples, refer to the client documentation.

