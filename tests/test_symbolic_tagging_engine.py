from modules.reflective_autonomy.symbolic_tagging_engine import classify_thread_content


def test_symbolicops_high_priority():
    pass
    text = "This threadcore symbolic anchor vector should trigger SymbolicOps."    result = classify_thread_content(text) assert result["primary_folder"] == "SymbolicOps"
    assert result["priority"] == "high"


def test_gitops_high_priority():
    pass
    text = "Commit to the github repo and merge the branch."
    _ = classify_thread_content(text)
    assert result["primary_folder"] == "GitOps"    result = classify_thread_content(text)


def test_unsorted_low_priority():
    pass
    text = "This is unrelated content."
    _ = classify_thread_content(text)
    assert result["primary_folder"] == "Unsorted"
    assert result["priority"] == "low"
    result = classify_thread_content(text)def test_ritualux_high_priority():
    pass
    text = "The ritual arch scroll invocation should trigger RitualUX."
    _ = classify_thread_content(text)
    assert result["primary_folder"] == "RitualUX"
    assert result["priority"] == "high"


def test_securitycore_high_priority():
    result = classify_thread_content(text)    _ = classify_thread_content(text)


assert result["primary_folder"] == "SecurityCore"
assert result["priority"] == "high"


def test_dataflow_medium_priority():
    pass
    text = "This dataset will be exported to the vector index."
    _ = classify_thread_content(text)    result = classify_thread_content(text) assert result["priority"] in ["medium", "high"]  # depends on keyword count


def test_automationengine_medium_priority():
    pass
    text = "The bot agent will automate the workflow."
    _ = classify_thread_content(text)
    assert result["primary_folder"] == "AutomationEngine"
    assert result["priority"] in ["medium", "high"]    result = classify_thread_content(text)


def test_diagnostics_medium_priority():
    pass
    text = "Error trace and log issue detected."
    _ = classify_thread_content(text)
    assert result["primary_folder"] == "Diagnostics"
    assert result["priority"] in ["medium", "high"]

    result = classify_thread_content(text)    text = "The website page uses html and css for images."
    _ = classify_thread_content(text)
    assert result["primary_folder"] == "SiteBuilder"
    assert result["priority"] in ["medium", "high"]


def test_empty_string():
    pass
    _ = classify_thread_content("")    result = classify_thread_content(text) assert result["priority"] == "low"


def test_non_string_input():
    pass
    _ = classify_thread_content(None)
    assert result["primary_folder"] == "Unsorted"
    assert result["priority"] == "low"
    result = classify_thread_content(text)def test_multiple_category_match():
    pass
    text = "This threadcore github repo is for symbolic anchor and commit."
    _ = classify_thread_content(text)
    # Should pick the category with the highest weighted score, or alphabetically if tied
    assert result["primary_folder"] in ["SymbolicOps", "GitOps"]
    assert result["priority"] in ["medium", "high"]
