import pytest
from unittest.mock import patch, MagicMock
from gantry.ops.ollama import generate_modelfile, create_model


def test_generate_modelfile_basic():
    """Tests basic Modelfile generation."""
    modelfile = generate_modelfile("llama3.1")
    assert "FROM llama3.1" in modelfile
    assert "SYSTEM" not in modelfile


def test_generate_modelfile_with_system():
    """Tests Modelfile generation with a system prompt."""
    modelfile = generate_modelfile("llama3.1", system="You are a bot")
    assert 'SYSTEM """You are a bot"""' in modelfile


def test_generate_modelfile_with_params():
    """Tests Modelfile generation with parameters."""
    params = {"temperature": 0.5, "top_p": 0.9}
    modelfile = generate_modelfile("llama3.1", parameters=params)
    assert "PARAMETER temperature 0.5" in modelfile
    assert "PARAMETER top_p 0.9" in modelfile


@pytest.mark.asyncio
@patch("httpx.AsyncClient.post")
async def test_create_model_api_call(mock_post):
    """Tests the create_model API wrapper."""
    # The response object from httpx has synchronous methods like json()
    mock_response = MagicMock()
    mock_response.status_code = 200
    mock_response.json.return_value = {"status": "success"}
    mock_response.raise_for_status = MagicMock()

    # AsyncClient.post is awaited, so we make the mock return our mock_response
    mock_post.return_value = mock_response

    result = await create_model("test-model", "FROM latest", base="latest")
    assert result["status"] == "success"
    mock_post.assert_called_once()
