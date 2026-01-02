import os
import chainlit as cl
from openai import AsyncOpenAI


# Configure Ollama client
client = AsyncOpenAI(
    base_url=os.getenv("OLLAMA_HOST", "http://ollama:11434") + "/v1",
    api_key="ollama",  # required but unused
)

# Settings
settings = {
    "model": "llama3.1:latest",
    "temperature": 0.7,
    "max_tokens": 2000,
}


@cl.on_chat_start
async def start():
    cl.user_session.set("settings", settings)

    await cl.Message(
        content="Hello from Gantry! I am connected to your local Ollama instance."
    ).send()


@cl.on_message
async def main(message: cl.Message):
    settings = cl.user_session.get("settings")

    msg = cl.Message(content="")
    await msg.send()

    stream = await client.chat.completions.create(
        messages=[
            {"role": "system", "content": "You are a helpful AI assistant."},
            {"role": "user", "content": message.content},
        ],
        stream=True,
        **settings,
    )

    async for part in stream:
        if token := part.choices[0].delta.content:
            await msg.stream_token(token)

    await msg.update()
