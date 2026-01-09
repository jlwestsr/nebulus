import os
import httpx
from typing import Dict, Any, Optional

OLLAMA_HOST = os.getenv("OLLAMA_HOST", "http://ollama:11434")


async def create_model(
    name: str, modelfile: str, base: Optional[str] = None
) -> Dict[str, Any]:
    """Creates a new model in Ollama using a Modelfile.

    Args:
        name: Name of the model to create.
        modelfile: Content of the Modelfile.
        base: The base model name (optional, but recommended by some Ollama versions).

    Returns:
        JSON response from Ollama API.

    Raises:
        httpx.HTTPStatusError: If the API request fails.
    """
    url = f"{OLLAMA_HOST}/api/create"
    payload = {"name": name, "modelfile": modelfile, "stream": False}
    if base:
        payload["from"] = base

    async with httpx.AsyncClient(timeout=60.0) as client:
        response = await client.post(url, json=payload)
        response.raise_for_status()
        return response.json()


def generate_modelfile(
    base_model: str, system: str = "", parameters: Optional[Dict[str, Any]] = None
) -> str:
    """Generates a Modelfile string from components.

    Args:
        base_model: The base model name (e.g., 'llama3.1').
        system: Optional system prompt.
        parameters: Optional dictionary of Ollama parameters (e.g., {'temperature': 0.7}).

    Returns:
        The Modelfile content as a string.
    """
    lines = [f"FROM {base_model}"]

    if system:
        lines.append(f'SYSTEM """{system}"""')

    if parameters:
        for key, value in parameters.items():
            # Standard params like temperature, top_p, top_k
            lines.append(f"PARAMETER {key} {value}")

    return "\n".join(lines)
