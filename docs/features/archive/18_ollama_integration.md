# Feature: Ollama Integration

**Goal**: Enable Gantry to communicate with the local Ollama instance to provide chat functionality using LLMs.

## Requirements
- Gantry must connect to the specific Ollama instance defined in `docker-compose.yml`.
- The system must ensure the required model (e.g., `llama3.1:latest`) is available.
- If the model is missing, it should be pulled automatically or instructions provided.

## Technical Details
- **Ollama Host**: `http://ollama:11434` (Internal Docker Network)
- **Model**: `llama3.1` (Default)
- **Files to Modify**:
    - `gantry/chat.py`: Ensure client configuration matches environment.

## Verification
- User can send a message in Gantry and receive a response.
- "Hello from Gantry! I am connected to your local Ollama instance." is displayed on start.
