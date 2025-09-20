from modules.reflective_autonomy.symbolic_tagging_engine import classify_thread_content


def test_symbolicops_high_priority():
    text = "This threadcore symbolic anchor vector should trigger SymbolicOps."
    result = classify_thread_content(text)
    assert result["primary_folder"] == "SymbolicOps"
    assert result["priority"] == "high"


def test_gitops_high_priority():
    text = "Commit to the github repo and merge the branch."
    result = classify_thread_content(text)
    assert result["primary_folder"] == "GitOps"


def test_unsorted_low_priority():
    text = "This is unrelated content."
    result = classify_thread_content(text)
    assert result["primary_folder"] == "Unsorted"
    assert result["priority"] == "low"


def test_ritualux_high_priority():
    text = "The ritual arch scroll invocation should trigger RitualUX."
    result = classify_thread_content(text)
    assert result["primary_folder"] == "RitualUX"
    assert result["priority"] == "high"


def test_securitycore_high_priority():
    text = "Please use secure encryption and auth keys to decrypt the session."
    result = classify_thread_content(text)
    assert result["primary_folder"] == "SecurityCore"
    assert result["priority"] in ["medium", "high"]


def test_dataflow_medium_priority():
    text = "This dataset will be exported to the vector index."
    result = classify_thread_content(text)
    assert result["primary_folder"] == "DataFlow"
    assert result["priority"] in ["medium", "high"]


def test_automationengine_medium_priority():
    text = "The bot agent will automate the workflow."
    result = classify_thread_content(text)
    assert result["primary_folder"] == "AutomationEngine"
    assert result["priority"] in ["medium", "high"]


def test_diagnostics_medium_priority():
    text = "Error trace and log issue detected."
    result = classify_thread_content(text)
    assert result["primary_folder"] == "Diagnostics"
    assert result["priority"] in ["medium", "high"]


def test_sitebuilder_medium_priority():
    text = "The website page uses html and css for images."
    result = classify_thread_content(text)
    assert result["primary_folder"] == "SiteBuilder"
    assert result["priority"] in ["medium", "high"]


def test_empty_string():
    result = classify_thread_content("")
    assert result["priority"] == "low"


def test_non_string_input():
    result = classify_thread_content(None)
    assert result["primary_folder"] == "Unsorted"
    assert result["priority"] == "low"


def test_multiple_category_match():
    text = "This threadcore github repo is for symbolic anchor and commit."
    result = classify_thread_content(text)
    # Should pick the category with the highest weighted score, or alphabetically if tied
    assert result["primary_folder"] in ["SymbolicOps", "GitOps"]
    assert result["priority"] in ["medium", "high"]
