from modules.reflective_autonomy.threadcore_tagging import tag_thread_context

def test_symbolicops_high_priority():
    text = "Threadcore symbolic anchor drift vector reflect seal."
    result = tag_thread_context(text)
    assert result["primary_folder"] == "SymbolicOps"
    assert result["priority"] == "high"

def test_gitops_high_priority():
    text = "Commit to the github repo and merge the branch."
    result = tag_thread_context(text)
    assert result["primary_folder"] == "GitOps"
    assert result["priority"] == "high"

def test_ritualux_high_priority():
    text = "The ritual arch scroll invocation should trigger RitualUX."
    result = tag_thread_context(text)
    assert result["primary_folder"] == "RitualUX"
    assert result["priority"] == "high"

def test_securitycore_high_priority():
    text = "Encryption and key management are core to secure sessions."
    result = tag_thread_context(text)
    assert result["primary_folder"] == "SecurityCore"
    assert result["priority"] == "high"

def test_dataflow_medium_priority():
    text = "This dataset will be exported to the vector index."
    result = tag_thread_context(text)
    assert result["primary_folder"] == "DataFlow"
    assert result["priority"] in ["medium", "high"]

def test_automationengine_medium_priority():
    text = "The bot agent will automate the workflow."
    result = tag_thread_context(text)
    assert result["primary_folder"] == "AutomationEngine"
    assert result["priority"] in ["medium", "high"]

def test_diagnostics_medium_priority():
    text = "Error trace and log issue detected."
    result = tag_thread_context(text)
    assert result["primary_folder"] == "Diagnostics"
    assert result["priority"] in ["medium", "high"]

def test_sitebuilder_medium_priority():
    text = "The website page uses html and css for images."
    result = tag_thread_context(text)
    assert result["primary_folder"] == "SiteBuilder"
    assert result["priority"] in ["medium", "high"]

def test_empty_string():
    result = tag_thread_context("")
    assert result["primary_folder"] == "Unsorted"
    assert result["priority"] == "low"

def test_non_string_input():
    result = tag_thread_context(None)
    assert result["primary_folder"] == "Unsorted"
    assert result["priority"] == "low"

def test_multiple_category_match():
    text = "Threadcore github repo symbolic anchor commit."
    result = tag_thread_context(text)
    assert result["primary_folder"] in ["SymbolicOps", "GitOps"]
    assert result["priority"] in ["medium", "high"]
