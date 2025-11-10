#!/usr/bin/env python3
"""
Character Loader System - L1 Canon Character Integration
--------------------------------------------------------
Loads canonical character profiles from simulation/L1_CANON_CHARACTER_ROSTER.md
and integrates them into the Orion Station simulation engine.

This system enables scaling from current 8 characters to full ~40 character roster
while maintaining consistency with canonical character data.

Features:
- Parses L1_CANON_CHARACTER_ROSTER.md structured format
- Extracts character attributes, stats, and metadata
- Creates Agent instances with proper specializations
- Validates character data integrity
- Supports gradual roster expansion (v1.1 → v2.0+)

Symbolic Tag: s.tag::char.loader.orion
"""

from dataclasses import dataclass, field
from pathlib import Path
from typing import Dict, List, Optional, Set
import re
import logging


@dataclass
class CharacterProfile:
    """Structured character data from L1 Canon Roster"""
    # Core Identity
    character_id: str  # e.g., "ENG_010"
    name: str
    role: str
    title: str
    division: str
    
    # Clearance and Contact
    clearance: str
    contact: str
    symbolic_tag: str
    
    # Simulation Stats
    base_speed: float
    specialization_multiplier: float
    collaboration_bonus: float
    
    # Focus Areas (for task matching)
    focus_areas: List[str] = field(default_factory=list)
    primary_systems: List[str] = field(default_factory=list)
    
    # Collaborative Network
    key_collaborators: List[str] = field(default_factory=list)
    
    # Phase 1 Attributes
    phase1_role: Optional[str] = None
    phase1_responsibilities: List[str] = field(default_factory=list)
    
    # Metadata
    alignment: Optional[str] = None
    version_added: str = "1.0"


class CharacterLoader:
    """Loads and manages L1 Canon characters for simulation"""
    
    def __init__(self, roster_path: Optional[Path] = None, logger: Optional[logging.Logger] = None):
        self.logger = logger or logging.getLogger(__name__)
        self.roster_path = roster_path or Path(__file__).parent / "L1_CANON_CHARACTER_ROSTER.md"
        self.characters: Dict[str, CharacterProfile] = {}
        self.version: str = "unknown"
        self._load_roster()
    
    def _load_roster(self) -> None:
        """Parse L1_CANON_CHARACTER_ROSTER.md and extract character data"""
        if not self.roster_path.exists():
            self.logger.warning(f"Roster file not found: {self.roster_path}")
            return
        
        content = self.roster_path.read_text(encoding="utf-8")
        
        # Extract version
        version_match = re.search(r"Version:\*\*\s*([^\s]+)", content)
        if version_match:
            self.version = version_match.group(1)
            self.logger.info(f"Loading L1 Canon Character Roster {self.version}")
        
        # Split into character sections (between ### N. **Name** headers)
        char_sections = re.split(r"###\s+\d+\.\s+\*\*(.+?)\*\*", content)
        
        # Process pairs: (name, section_content)
        for i in range(1, len(char_sections), 2):
            if i + 1 >= len(char_sections):
                break
            name = char_sections[i].strip()
            section = char_sections[i + 1]
            try:
                char = self._parse_character_section(name, section)
                if char:
                    self.characters[char.name] = char
                    self.logger.debug(f"Loaded character: {char.name} ({char.character_id})")
            except Exception as e:
                self.logger.error(f"Failed to parse character {name}: {e}")
                continue
        
        self.logger.info(f"Loaded {len(self.characters)} characters from roster")
    
    def _parse_character_section(self, name: str, section: str) -> Optional[CharacterProfile]:
        """Parse individual character section"""
        # Name is already provided from split
        
        # Helper function to extract field values
        def extract_field(pattern: str, flags=0) -> Optional[str]:
            match = re.search(pattern, section, flags)
            return match.group(1).strip() if match else None
        
        def extract_list_field(pattern: str) -> List[str]:
            match = re.search(pattern, section, re.DOTALL)
            if not match:
                return []
            items_text = match.group(1)
            items = re.findall(r"-\s*(.+?)$", items_text, re.MULTILINE)
            return [item.strip() for item in items]
        
        # Extract basic fields
        role = extract_field(r"\*\*Role:\*\*\s*(.+?)$", re.MULTILINE) or "Unknown"
        title = extract_field(r"\*\*Title:\*\*\s*(.+?)$", re.MULTILINE) or role
        division = extract_field(r"\*\*Division:\*\*\s*(.+?)$", re.MULTILINE) or "Unknown"
        
        # Extract identifiers
        clearance = extract_field(r"\*\*Clearance:\*\*\s*(.+?)$", re.MULTILINE) or "L2_STANDARD"
        character_id = extract_field(r"\*\*ID:\*\*\s*(.+?)$", re.MULTILINE) or "UNKNOWN"
        default_contact = f"{name.lower().replace(' ', '.')}@orion.station"
        contact = extract_field(r"\*\*Contact:\*\*\s*(.+?)$", re.MULTILINE) or default_contact
        symbolic_tag = extract_field(r"\*\*Symbolic Tag:\*\*\s*`(.+?)`", re.MULTILINE) or "s.tag::unknown"
        
        # Extract simulation stats
        base_speed = self._extract_float(section, r"\*\*Base Speed:\*\*\s*([\d.]+)", 0.80)
        spec_mult = self._extract_float(section, r"\*\*Specialization Multiplier:\*\*\s*([\d.]+)x", 1.00)
        collab_bonus = self._extract_float(section, r"\*\*Collaboration Bonus:\*\*\s*\+?([\d.]+)%", 0.0) / 100.0
        
        # Extract focus areas
        focus_areas = extract_list_field(r"\*\*Focus Areas:\*\*\s*\n((?:\s*-\s*.+?\n?)+)")
        
        # Extract primary systems
        primary_systems = extract_list_field(r"\*\*Primary Systems:\*\*\s*\n((?:\s*-\s*.+?\n?)+)")
        
        # Extract key collaborators
        collaborators = extract_list_field(r"\*\*Key Collaborators:\*\*\s*\n((?:\s*-\s*.+?\n?)+)")
        
        # Extract Phase 1 role
        phase1_role = extract_field(r"\*\*Phase 1 Role:\*\*\s*(.+?)(?:\n|$)", re.MULTILINE)
        phase1_responsibilities = extract_list_field(r"\*\*Phase 1 Responsibilities:\*\*\s*\n((?:\s*-\s*.+?\n?)+)")
        
        # Extract alignment
        alignment = extract_field(r"\*\*Alignment:\*\*\s*(.+?)$", re.MULTILINE)
        
        return CharacterProfile(
            character_id=character_id,
            name=name,
            role=role,
            title=title,
            division=division,
            clearance=clearance,
            contact=contact,
            symbolic_tag=symbolic_tag,
            base_speed=base_speed,
            specialization_multiplier=spec_mult,
            collaboration_bonus=collab_bonus,
            focus_areas=focus_areas,
            primary_systems=primary_systems,
            key_collaborators=collaborators,
            phase1_role=phase1_role,
            phase1_responsibilities=phase1_responsibilities,
            alignment=alignment,
            version_added=self.version
        )
    
    def _extract_float(self, text: str, pattern: str, default: float) -> float:
        """Extract float value from text using regex pattern"""
        match = re.search(pattern, text, re.MULTILINE)
        if match:
            try:
                return float(match.group(1))
            except (ValueError, IndexError):
                pass
        return default
    
    def get_character(self, name: str) -> Optional[CharacterProfile]:
        """Get character profile by name"""
        return self.characters.get(name)
    
    def get_all_characters(self) -> List[CharacterProfile]:
        """Get all loaded characters"""
        return list(self.characters.values())
    
    def get_characters_by_division(self, division: str) -> List[CharacterProfile]:
        """Get all characters in a specific division"""
        return [c for c in self.characters.values() if c.division == division]
    
    def get_characters_by_clearance(self, clearance: str) -> List[CharacterProfile]:
        """Get all characters with specific clearance level"""
        return [c for c in self.characters.values() if c.clearance == clearance]
    
    def get_characters_for_phase1(self) -> List[CharacterProfile]:
        """Get all characters with Phase 1 roles defined"""
        return [c for c in self.characters.values() if c.phase1_role]
    
    def get_focus_keywords(self, character: CharacterProfile) -> Set[str]:
        """Extract all focus keywords for task matching"""
        keywords = set()
        
        # Add focus areas
        for area in character.focus_areas:
            keywords.update(area.lower().split())
        
        # Add role keywords
        keywords.update(character.role.lower().split())
        
        # Add title keywords
        keywords.update(character.title.lower().split())
        
        # Clean up common words
        stopwords = {'and', 'or', 'the', 'a', 'an', 'for', 'of', 'in', 'to'}
        keywords = {k for k in keywords if k not in stopwords and len(k) > 2}
        
        return keywords
    
    def create_focus_string(self, character: CharacterProfile) -> str:
        """Create space-separated focus string for Agent initialization"""
        keywords = self.get_focus_keywords(character)
        return " ".join(sorted(keywords))
    
    def export_summary(self) -> Dict:
        """Export summary statistics about loaded roster"""
        return {
            "version": self.version,
            "total_characters": len(self.characters),
            "by_division": self._count_by_field("division"),
            "by_clearance": self._count_by_field("clearance"),
            "phase1_ready": len(self.get_characters_for_phase1()),
            "character_names": sorted(self.characters.keys())
        }
    
    def _count_by_field(self, field: str) -> Dict[str, int]:
        """Count characters grouped by a field"""
        counts = {}
        for char in self.characters.values():
            value = getattr(char, field, "Unknown")
            counts[value] = counts.get(value, 0) + 1
        return counts
    
    def validate_roster(self) -> List[str]:
        """Validate roster data integrity and return list of issues"""
        issues = []
        
        # Check for duplicate IDs
        ids = [c.character_id for c in self.characters.values()]
        if len(ids) != len(set(ids)):
            issues.append("Duplicate character IDs detected")
        
        # Check for duplicate symbolic tags
        tags = [c.symbolic_tag for c in self.characters.values()]
        if len(tags) != len(set(tags)):
            issues.append("Duplicate symbolic tags detected")
        
        # Validate stats
        for char in self.characters.values():
            if char.base_speed < 0.0 or char.base_speed > 2.0:
                issues.append(f"{char.name}: base_speed out of range (0.0-2.0)")
            
            if char.specialization_multiplier < 1.0 or char.specialization_multiplier > 2.0:
                issues.append(f"{char.name}: specialization_multiplier out of range (1.0-2.0)")
            
            if char.collaboration_bonus < 0.0 or char.collaboration_bonus > 0.50:
                issues.append(f"{char.name}: collaboration_bonus out of range (0.0-0.50)")
        
        return issues


def demo_load():
    """Demonstration of character loader functionality"""
    logging.basicConfig(level=logging.INFO, format="%(levelname)s: %(message)s")
    
    loader = CharacterLoader()
    
    print("\n=== L1 Canon Character Roster Loader ===")
    print(f"Version: {loader.version}")
    print(f"Characters loaded: {len(loader.characters)}")
    
    # Show summary
    summary = loader.export_summary()
    print("\n--- Summary ---")
    print(f"Total characters: {summary['total_characters']}")
    print(f"Phase 1 ready: {summary['phase1_ready']}")
    print(f"\nBy Division:")
    for div, count in summary['by_division'].items():
        print(f"  {div}: {count}")
    
    # Validate
    print("\n--- Validation ---")
    issues = loader.validate_roster()
    if issues:
        print("Issues found:")
        for issue in issues:
            print(f"  ⚠️  {issue}")
    else:
        print("✅ All validation checks passed")
    
    # Show character examples
    print("\n--- Character Examples ---")
    phase1_chars = loader.get_characters_for_phase1()
    for char in phase1_chars[:3]:  # Show first 3
        print(f"\n{char.name} ({char.character_id})")
        print(f"  Role: {char.role}")
        print(f"  Stats: speed={char.base_speed}, spec={char.specialization_multiplier}x, collab=+{char.collaboration_bonus*100:.0f}%")
        print(f"  Focus: {loader.create_focus_string(char)[:60]}...")
        if char.phase1_role:
            print(f"  Phase 1: {char.phase1_role}")
    
    # Check specific character
    print("\n--- Tobias Qin Check ---")
    tobias = loader.get_character("Tobias Qin")
    if tobias:
        print(f"✅ Tobias Qin loaded successfully")
        print(f"  ID: {tobias.character_id}")
        print(f"  Role: {tobias.role}")
        print(f"  Primary Systems: {', '.join(tobias.primary_systems[:2])}")
        print(f"  Base Speed: {tobias.base_speed}")
        print(f"  Specialization: {tobias.specialization_multiplier}x")
    else:
        print("❌ Tobias Qin not found in roster")


if __name__ == "__main__":
    demo_load()
