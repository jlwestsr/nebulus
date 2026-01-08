import base64
from gantry.chat import construct_multimodal_payload


# Mock classes to simulate Chainlit elements
class MockImage:
    def __init__(self, path, mime="image/png"):
        self.path = path
        self.mime = mime


def test_construct_payload_text_only():
    """Verify that a text-only message returns simple string content."""
    content = "Hello world"
    images = []
    payload = construct_multimodal_payload(content, images)
    assert payload == content


def test_construct_payload_with_image(tmp_path):
    """Verify that a message with an image returns the structured content list."""
    # Create a dummy image file
    img_file = tmp_path / "test.png"
    img_file.write_bytes(b"fake_image_data")

    mock_image = MockImage(str(img_file), "image/png")

    content = "Describe this"
    images = [mock_image]

    payload = construct_multimodal_payload(content, images)

    assert isinstance(payload, list)
    assert len(payload) == 2

    # Check text part
    assert payload[0]["type"] == "text"
    assert payload[0]["text"] == content

    # Check image part
    assert payload[1]["type"] == "image_url"
    assert payload[1]["image_url"]["url"].startswith("data:image/png;base64,")

    # Verify base64 encoding
    expected_b64 = base64.b64encode(b"fake_image_data").decode("utf-8")
    assert payload[1]["image_url"]["url"] == f"data:image/png;base64,{expected_b64}"
