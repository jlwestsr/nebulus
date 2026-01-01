import chainlit as cl


@cl.on_chat_start
async def start():
    await cl.Message(
        content="Hello from Gantry! The Chainlit interface is now active."
    ).send()


@cl.on_message
async def main(message: cl.Message):
    # Echo for now
    await cl.Message(content=f"You said: {message.content}").send()
