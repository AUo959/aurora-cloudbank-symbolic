"""
Tests for Character Init Standardization Phase 3 (Issue #430)

Tests:
- Location change tracking and routing
- Character caching performance
- Pre-commit hook character consistency detection
"""

import sys
import time
from pathlib import Path

import pytest

# Add the .aurora directory to the path for imports
sys.path.insert(0, str(Path(__file__).parent.parent / ".aurora"))
sys.path.insert(0, str(Path(__file__).parent.parent / "scripts"))


@pytest.mark.unit
class TestLocationRouting:
    """Tests for location change tracking (Phase 3 item 1)."""

    def test_route_to_security_operations(self):
        """Test routing to Security Operations with 'security' keyword."""
        from load_simulation import route_to_location

        result = route_to_location("security")

        assert result["success"] is True
        assert result["location_key"] == "security_operations"
        assert result["location"]["name"] == "Security Operations Center"
        assert result["location"]["deck"] == "Deck A"

    def test_route_to_conference_room(self):
        """Test routing to Conference Room Alpha with 'roundtable' keyword."""
        from load_simulation import route_to_location

        result = route_to_location("roundtable")

        assert result["success"] is True
        assert result["location_key"] == "conference_room_alpha"
        assert result["location"]["name"] == "Conference Room Alpha"
        # All Primary 8 should be present
        assert len(result["agents"]) == 8

    def test_route_to_ethics_chamber(self):
        """Test routing to Noor Chamber with 'ethics' keyword."""
        from load_simulation import route_to_location

        result = route_to_location("ethics")

        assert result["success"] is True
        assert result["location_key"] == "noor_chamber"
        assert result["location"]["name"] == "Noor Chamber"

    def test_route_to_science_lab(self):
        """Test routing to Science Lab with 'research' keyword."""
        from load_simulation import route_to_location

        result = route_to_location("research")

        assert result["success"] is True
        assert result["location_key"] == "science_lab"
        assert result["location"]["name"] == "Science Lab"

    def test_route_to_cultural_center(self):
        """Test routing to Cultural Center with 'crew' keyword."""
        from load_simulation import route_to_location

        result = route_to_location("crew")

        assert result["success"] is True
        assert result["location_key"] == "cultural_center"
        assert result["location"]["name"] == "Cultural Center"

    def test_route_default_to_command_bridge(self):
        """Test that unknown keywords default to Command Bridge."""
        from load_simulation import route_to_location

        result = route_to_location("unknown_keyword_xyz")

        assert result["success"] is True
        assert result["location_key"] == "command_bridge"
        assert result["location"]["name"] == "Command Bridge"

    def test_route_case_insensitive(self):
        """Test that routing is case-insensitive."""
        from load_simulation import route_to_location

        result = route_to_location("SECURITY")
        assert result["location_key"] == "security_operations"

        result = route_to_location("RoUnDtAbLe")
        assert result["location_key"] == "conference_room_alpha"

    def test_route_updates_state(self):
        """Test that routing updates the simulation state."""
        from load_simulation import route_to_location, load_simulation_state

        # Route to a specific location
        route_to_location("ethics")

        # Load the updated state
        state = load_simulation_state()

        # Verify the location was updated
        assert state["simulation"]["current_location"]["name"] == "Noor Chamber"


@pytest.mark.unit
class TestCharacterCache:
    """Tests for character caching performance (Phase 3 item 3)."""

    def test_cache_initialization(self):
        """Test that cache initializes properly."""
        from load_simulation import get_character_cache

        cache = get_character_cache()

        assert cache is not None
        stats = cache.get_stats()
        assert stats["total_characters"] == 8

    def test_cache_performance_under_100ms(self):
        """Test that cache build time is under 100ms (acceptance criteria)."""
        from load_simulation import CharacterCache

        # Force new cache creation
        CharacterCache._initialized = False
        CharacterCache._instance = None

        start_time = time.time()
        CharacterCache()
        build_time_ms = (time.time() - start_time) * 1000

        assert build_time_ms < 100, f"Cache build time {build_time_ms}ms exceeds 100ms limit"

    def test_cache_lookup_by_name(self):
        """Test character lookup by name."""
        from load_simulation import get_character_cache

        cache = get_character_cache()

        char = cache.get_by_name("Commander Alex Thorne")
        assert char is not None
        assert char["id"] == "CMD_001"
        assert char["gender"] == "Male (he/him)"

    def test_cache_lookup_by_partial_name(self):
        """Test character lookup by partial name."""
        from load_simulation import get_character_cache

        cache = get_character_cache()

        char = cache.get_by_name("thorne")
        assert char is not None
        assert char["name"] == "Commander Alex Thorne"

    def test_cache_lookup_by_id(self):
        """Test character lookup by ID."""
        from load_simulation import get_character_cache

        cache = get_character_cache()

        char = cache.get_by_id("CSO_002")
        assert char is not None
        assert char["name"] == "Julian Markov"

    def test_cache_lookup_by_agent_file(self):
        """Test character lookup by agent file."""
        from load_simulation import get_character_cache

        cache = get_character_cache()

        char = cache.get_by_agent_file("sato.py")
        assert char is not None
        assert char["name"] == "Dr. Amira Sato"

    def test_cache_agents_for_location(self):
        """Test getting agents for a specific location."""
        from load_simulation import get_character_cache

        cache = get_character_cache()

        agents = cache.get_agents_for_location("noor_chamber")
        names = [a["name"] for a in agents]

        # Noor Chamber should have Sato, Noor, Sorensen
        assert "Dr. Amira Sato" in names
        assert "Dr. Elira Noor" in names
        assert "Prof. Elena Sorensen" in names

    def test_cache_singleton(self):
        """Test that cache is a singleton."""
        from load_simulation import get_character_cache

        cache1 = get_character_cache()
        cache2 = get_character_cache()

        assert cache1 is cache2


@pytest.mark.unit
class TestCharacterConsistencyChecker:
    """Tests for character consistency detection (Phase 3 item 2)."""

    def test_detect_typo_alec(self):
        """Test detection of 'Alec' typo."""
        from check_character_consistency import check_for_typos

        content = "Commander Alec Thorne approved the mission."
        issues = check_for_typos(content, "test.md")

        assert len(issues) >= 1
        assert any("Alec" in issue[1] for issue in issues)

    def test_detect_typo_maya_shepherd(self):
        """Test detection of 'Shepherd' typo for Maya Shepard."""
        from check_character_consistency import check_for_typos

        content = "Lt. Commander Maya Shepherd reported to the bridge."
        issues = check_for_typos(content, "test.md")

        assert len(issues) >= 1
        assert any("Shepherd" in issue[1] for issue in issues)

    def test_no_false_positive_correct_names(self):
        """Test that correct names don't trigger typo detection."""
        from check_character_consistency import check_for_typos

        content = "Commander Alex Thorne and Lt. Commander Maya Shepard arrived."
        issues = check_for_typos(content, "test.md")

        assert len(issues) == 0

    def test_build_character_lookup(self):
        """Test that character lookup is built correctly."""
        from check_character_consistency import build_character_lookup

        lookup = build_character_lookup()

        assert "commander alex thorne" in lookup
        assert "thorne" in lookup
        assert "alex" in lookup
        assert "cmd_001" in lookup


@pytest.mark.unit
class TestPrimary8Characters:
    """Tests for Primary 8 character data integrity."""

    def test_all_8_characters_defined(self):
        """Test that all 8 Primary characters are defined."""
        from load_simulation import PRIMARY_8_CHARACTERS

        assert len(PRIMARY_8_CHARACTERS) == 8

    def test_commander_thorne_correct(self):
        """Test Commander Thorne's data is correct (the original issue)."""
        from load_simulation import PRIMARY_8_CHARACTERS

        thorne = next(c for c in PRIMARY_8_CHARACTERS if c["id"] == "CMD_001")

        assert thorne["name"] == "Commander Alex Thorne"
        assert "Alex" in thorne["name"]  # Not Alec
        assert thorne["gender"] == "Male (he/him)"
        assert thorne["agent_file"] == "thorne.py"

    def test_all_characters_have_required_fields(self):
        """Test all characters have required fields."""
        from load_simulation import PRIMARY_8_CHARACTERS

        required_fields = ["name", "role", "id", "gender", "agent_file"]

        for char in PRIMARY_8_CHARACTERS:
            for field in required_fields:
                assert field in char, f"Character {char.get('name', 'unknown')} missing {field}"

    def test_character_ids_unique(self):
        """Test all character IDs are unique."""
        from load_simulation import PRIMARY_8_CHARACTERS

        ids = [c["id"] for c in PRIMARY_8_CHARACTERS]
        assert len(ids) == len(set(ids))

    def test_agent_files_unique(self):
        """Test all agent files are unique."""
        from load_simulation import PRIMARY_8_CHARACTERS

        files = [c["agent_file"] for c in PRIMARY_8_CHARACTERS]
        assert len(files) == len(set(files))


@pytest.mark.unit
class TestLocationConfig:
    """Tests for location configuration."""

    def test_all_locations_defined(self):
        """Test that all 6 locations are defined."""
        from load_simulation import LOCATION_CONFIG

        expected_locations = [
            "command_bridge",
            "conference_room_alpha",
            "noor_chamber",
            "security_operations",
            "science_lab",
            "cultural_center"
        ]

        for loc in expected_locations:
            assert loc in LOCATION_CONFIG, f"Location {loc} not in config"

    def test_locations_have_required_fields(self):
        """Test all locations have required fields."""
        from load_simulation import LOCATION_CONFIG

        required_fields = ["name", "deck", "keywords", "primary_agents", "template", "tone"]

        for loc_key, loc_config in LOCATION_CONFIG.items():
            for field in required_fields:
                assert field in loc_config, f"Location {loc_key} missing {field}"

    def test_conference_room_has_all_primary_8(self):
        """Test Conference Room Alpha has all Primary 8 agents."""
        from load_simulation import LOCATION_CONFIG

        conf_room = LOCATION_CONFIG["conference_room_alpha"]

        assert len(conf_room["primary_agents"]) == 8
