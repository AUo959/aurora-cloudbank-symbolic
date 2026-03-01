from scripts.drop_in_thread_agent_v2 import tag_thread_context


def test_alias_and_folder_high_priority():
    text = "Threadcore symbolic anchor drift vector reflect seal"
    result = tag_thread_context(text)
    assert result["alias"] == "SymbolicOps"
    assert result["folder"] == "SymbolicOps"
    assert result["priority"] == "high"
    assert "directive" in result


def test_unsorted_low_priority():
    result = tag_thread_context("")
    assert result["alias"] == "Unsorted"
    assert result["folder"] == "Unsorted"
    assert result["priority"] == "low"


def test_no_directive_flag():
    text = "Commit to the github repo"
    result = tag_thread_context(text, include_directive=False)
    assert "directive" not in result
