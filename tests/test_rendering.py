from gantry.chat import process_thinking_tags


def test_process_thinking_tags_basic():
    """Test basic parsing of a complete think block."""
    input_text = (
        "Here is some context. <think>This is reasoning.</think> This is the answer."
    )
    expected = "Here is some context. <details open class='thinking-block'><summary>Thinking Process</summary><div class='thinking-content'>This is reasoning.</div></details> This is the answer."
    assert process_thinking_tags(input_text) == expected


def test_process_thinking_tags_incomplete_start():
    """Test when only start tag is present (streaming scenario)."""
    input_text = "Start <think> reasoning..."
    # Should open the block but not close it yet
    expected = "Start <details open class='thinking-block'><summary>Thinking Process</summary><div class='thinking-content'> reasoning..."
    assert process_thinking_tags(input_text) == expected


def test_process_thinking_tags_incomplete_end():
    """Test processing when end tag appears."""
    # If we apply to accumulating buffer:
    input_text = "Start <think> reasoning... </think> done."
    expected = "Start <details open class='thinking-block'><summary>Thinking Process</summary><div class='thinking-content'> reasoning... </div></details> done."
    assert process_thinking_tags(input_text) == expected


def test_process_thinking_tags_no_tags():
    """Test with no tags."""
    input_text = "Just regular text."
    assert process_thinking_tags(input_text) == input_text


def test_process_thinking_tags_nested_broken():
    """Test robustness against malformed tags."""
    input_text = "Broken <think> tag without end"
    expected = "Broken <details open class='thinking-block'><summary>Thinking Process</summary><div class='thinking-content'> tag without end"
    assert process_thinking_tags(input_text) == expected
