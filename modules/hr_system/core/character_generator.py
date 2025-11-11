"""
Character Generator - Quantum-Symbolic Crew Profile Creation

Generates crew members with full quantum-symbolic properties including:
- Core identity (name, rank, background, personality)
- Quantum profile (skill vectors, cultural_score, memory capacity)
- Professional attributes (specializations, certifications, experience)
- Psychological profile (work style, team dynamics, leadership)
- Integration properties (DLP tags, T1/SRB anchors, memory allocation)
"""

import random
from datetime import datetime
from typing import Dict, List, Optional, Any
from dataclasses import dataclass, field
from enum import Enum


class Rank(str, Enum):
    """Military/station rank structure"""
    COMMANDER = "Commander"
    LIEUTENANT_COMMANDER = "Lieutenant Commander"
    LIEUTENANT = "Lieutenant"
    LIEUTENANT_JG = "Lieutenant (Junior Grade)"
    ENSIGN = "Ensign"
    CHIEF_PETTY_OFFICER = "Chief Petty Officer"
    PETTY_OFFICER = "Petty Officer"
    CREWMAN = "Crewman"


class ExperienceLevel(str, Enum):
    """Experience level classification"""
    SENIOR = "senior"  # 10+ years
    EXPERIENCED = "experienced"  # 5-10 years
    INTERMEDIATE = "intermediate"  # 2-5 years
    JUNIOR = "junior"  # 0-2 years


class Department(str, Enum):
    """Station department structure"""
    COMMAND = "Command"
    OPERATIONS = "Operations"
    SECURITY = "Security"
    SCIENCE = "Science"
    ENGINEERING = "Engineering"
    MEDICAL = "Medical"
    HUMAN_RESOURCES = "Human Resources"


@dataclass
class QuantumProfile:
    """Quantum-symbolic properties for crew member"""
    skill_vector: List[float]  # VSA skill representation
    cultural_score: float  # CASK cultural intelligence score (0.0-1.0)
    memory_tier: str  # Dark matter memory allocation tier
    memory_capacity: int  # Available memory slots
    t1_anchor: int  # Temporal anchor state
    srb_anchor: int  # Spatial-relational boundary anchor
    dlp_tag: str  # Data lineage protocol tag
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "skill_vector": self.skill_vector,
            "cultural_score": self.cultural_score,
            "memory_tier": self.memory_tier,
            "memory_capacity": self.memory_capacity,
            "anchors": {
                "T1": self.t1_anchor,
                "SRB": self.srb_anchor
            },
            "dlp_tag": self.dlp_tag
        }


@dataclass
class CharacterProfile:
    """Complete character profile for crew member"""
    # Core Identity
    name: str
    rank: Rank
    department: Department
    section: Optional[str] = None
    
    # Professional
    specializations: List[str] = field(default_factory=list)
    certifications: List[str] = field(default_factory=list)
    experience_level: ExperienceLevel = ExperienceLevel.INTERMEDIATE
    years_experience: int = 5
    
    # Background
    background_story: str = ""
    previous_assignments: List[str] = field(default_factory=list)
    education: List[str] = field(default_factory=list)
    
    # Personality
    personality_traits: List[str] = field(default_factory=list)
    work_style: str = "collaborative"
    leadership_style: Optional[str] = None
    motivations: List[str] = field(default_factory=list)
    
    # Performance
    strengths: List[str] = field(default_factory=list)
    development_areas: List[str] = field(default_factory=list)
    
    # Quantum Profile
    quantum_profile: Optional[QuantumProfile] = None
    
    # Integration
    reports_to: Optional[str] = None
    status: str = "candidate"  # candidate, hired, onboarding, active, inactive
    hire_date: Optional[str] = None
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for JSON serialization"""
        data = {
            "name": self.name,
            "rank": self.rank.value,
            "department": self.department.value,
            "section": self.section,
            "specializations": self.specializations,
            "certifications": self.certifications,
            "experience_level": self.experience_level.value,
            "years_experience": self.years_experience,
            "background": {
                "story": self.background_story,
                "previous_assignments": self.previous_assignments,
                "education": self.education
            },
            "personality": {
                "traits": self.personality_traits,
                "work_style": self.work_style,
                "leadership_style": self.leadership_style,
                "motivations": self.motivations
            },
            "performance": {
                "strengths": self.strengths,
                "development_areas": self.development_areas
            },
            "reports_to": self.reports_to,
            "status": self.status,
            "hire_date": self.hire_date
        }
        
        if self.quantum_profile:
            data["quantum_profile"] = self.quantum_profile.to_dict()
            
        return data


class CharacterGenerator:
    """
    Generates crew member profiles with quantum-symbolic properties.
    
    Features:
    - Role-specific character generation
    - Quantum profile creation (skill vectors, cultural scores)
    - Personality and background narrative generation
    - Integration with simulation state
    """
    
    def __init__(self):
        """Initialize character generator"""
        self.timestamp_seed = datetime.now().timestamp()
        
        # Name pools (diverse representation)
        self.first_names = {
            "command": ["Sarah", "Marcus", "Kenji", "Fatima", "Carlos", "Priya"],
            "technical": ["Elena", "James", "Yuki", "Ahmed", "Sofia", "Raj"],
            "operations": ["Maria", "David", "Mei", "Hassan", "Anna", "Kwame"],
            "medical": ["Lisa", "Michael", "Hana", "Omar", "Isabella", "Tariq"]
        }
        
        self.last_names = [
            "Chen", "Johnson", "Nakamura", "García", "Schmidt", "Okafor",
            "Silva", "Kim", "Ivanov", "Dubois", "Patel", "Rodriguez",
            "Yamamoto", "Hassan", "Andersson", "Rossi", "Larsen", "Moretti"
        ]
        
    def generate_character(
        self,
        role: str,
        department: Department,
        rank: Rank,
        specializations: List[str],
        experience_level: ExperienceLevel = ExperienceLevel.EXPERIENCED,
        section: Optional[str] = None,
        count: int = 1
    ) -> List[CharacterProfile]:
        """
        Generate character profile(s) for a specific role.
        
        Args:
            role: Job title/role name
            department: Department assignment
            rank: Military/station rank
            specializations: List of specialized skills
            experience_level: Experience level (junior to senior)
            section: Specific section within department
            count: Number of candidates to generate
            
        Returns:
            List of CharacterProfile objects
        """
        candidates = []
        
        for i in range(count):
            # Generate core identity
            name = self._generate_name(role, i)
            
            # Generate background
            background = self._generate_background(role, experience_level, specializations)
            
            # Generate personality
            personality = self._generate_personality(role, experience_level)
            
            # Generate quantum profile
            quantum_profile = self._generate_quantum_profile(
                role, specializations, experience_level
            )
            
            # Assemble character
            character = CharacterProfile(
                name=name,
                rank=rank,
                department=department,
                section=section,
                specializations=specializations,
                certifications=self._generate_certifications(role, specializations),
                experience_level=experience_level,
                years_experience=self._calculate_years_experience(experience_level),
                background_story=background["story"],
                previous_assignments=background["assignments"],
                education=background["education"],
                personality_traits=personality["traits"],
                work_style=personality["work_style"],
                leadership_style=personality["leadership_style"],
                motivations=personality["motivations"],
                strengths=self._generate_strengths(specializations, experience_level),
                development_areas=self._generate_development_areas(experience_level),
                quantum_profile=quantum_profile,
                reports_to=self._determine_reports_to(department, rank),
                status="candidate"
            )
            
            candidates.append(character)
            
        return candidates
    
    def _generate_name(self, role: str, seed: int) -> str:
        """Generate diverse name based on role"""
        random.seed(self.timestamp_seed + seed)
        
        # Determine name pool category
        if "Chief" in role or "Officer" in role:
            category = "command"
        elif "Engineer" in role or "Analyst" in role:
            category = "technical"
        elif "Doctor" in role or "Medical" in role:
            category = "medical"
        else:
            category = "operations"
            
        first = random.choice(self.first_names[category])
        last = random.choice(self.last_names)
        
        return f"{first} {last}"
    
    def _generate_background(
        self, role: str, experience: ExperienceLevel, specializations: List[str]
    ) -> Dict[str, Any]:
        """Generate background narrative"""
        
        # Experience-based background templates
        if experience == ExperienceLevel.SENIOR:
            story = (
                f"Veteran professional with 15+ years across multiple stations and fleet operations. "
                f"Proven track record in {', '.join(specializations[:2])}. "
                f"Known for strategic thinking and ability to build high-performing teams."
            )
            assignments = [
                "Fleet Command - Strategic Operations (5 years)",
                "Research Station Alpha - Department Head (4 years)",
                "Deep Space Platform Gamma - Section Lead (6 years)"
            ]
            education = [
                "Advanced Degree in Organizational Leadership",
                "Specialized certifications in " + specializations[0],
                "Fleet Command School Graduate"
            ]
        elif experience == ExperienceLevel.EXPERIENCED:
            story = (
                f"Accomplished professional with strong expertise in {', '.join(specializations[:2])}. "
                f"Successfully led multiple cross-functional initiatives. "
                f"Balance of technical depth and leadership capability."
            )
            assignments = [
                "Station Beta - Senior Team Member (3 years)",
                "Fleet Operations Center - Specialist (2 years)",
                "Research Facility - Junior Team Lead (2 years)"
            ]
            education = [
                "Graduate degree in relevant field",
                "Professional certifications in " + specializations[0],
                "Leadership development program"
            ]
        elif experience == ExperienceLevel.INTERMEDIATE:
            story = (
                f"Developing professional with solid foundation in {', '.join(specializations[:2])}. "
                f"Demonstrated growth potential and adaptability. "
                f"Ready for increased responsibility."
            )
            assignments = [
                "Current Station - Team Member (2 years)",
                "Training Facility - Apprentice (1 year)"
            ]
            education = [
                "Bachelor's degree in relevant field",
                "Core certifications in " + specializations[0]
            ]
        else:  # JUNIOR
            story = (
                f"Promising early-career professional with training in {', '.join(specializations[:2])}. "
                f"Eager to contribute and develop expertise. "
                f"Strong academic background."
            )
            assignments = [
                "Academy Internship Program",
                "Station Rotation - Trainee"
            ]
            education = [
                "Recent graduate with honors",
                "Foundational certifications"
            ]
            
        return {
            "story": story,
            "assignments": assignments,
            "education": education
        }
    
    def _generate_personality(
        self, role: str, experience: ExperienceLevel
    ) -> Dict[str, Any]:
        """Generate personality profile"""
        
        # Role-based personality traits
        if "Chief" in role:
            traits = ["strategic", "visionary", "decisive", "empathetic", "diplomatic"]
            work_style = "collaborative-leadership"
            leadership_style = "transformational"
            motivations = [
                "Building high-performing organizations",
                "Developing people and teams",
                "Strategic impact"
            ]
        elif "Specialist" in role:
            traits = ["analytical", "detail-oriented", "methodical", "innovative", "focused"]
            work_style = "independent-expert"
            leadership_style = "technical-leadership" if experience == ExperienceLevel.SENIOR else None
            motivations = [
                "Technical excellence",
                "Problem-solving",
                "Continuous learning"
            ]
        else:
            traits = ["reliable", "collaborative", "adaptable", "proactive", "thorough"]
            work_style = "team-oriented"
            leadership_style = None
            motivations = [
                "Team success",
                "Skill development",
                "Mission contribution"
            ]
            
        return {
            "traits": traits,
            "work_style": work_style,
            "leadership_style": leadership_style,
            "motivations": motivations
        }
    
    def _generate_quantum_profile(
        self, role: str, specializations: List[str], experience: ExperienceLevel
    ) -> QuantumProfile:
        """Generate quantum-symbolic properties"""
        
        # Generate skill vector (simplified - would integrate with Skill Composer)
        import secrets
        skill_vector = [secrets.SystemRandom().random() for _ in range(10)]
        
        # Cultural score (higher for experienced staff)
        experience_multiplier = {
            ExperienceLevel.SENIOR: 0.9,
            ExperienceLevel.EXPERIENCED: 0.75,
            ExperienceLevel.INTERMEDIATE: 0.6,
            ExperienceLevel.JUNIOR: 0.5
        }
        cultural_score = random.uniform(0.7, 1.0) * experience_multiplier[experience]
        
        # Memory allocation based on role and experience
        if "Chief" in role:
            memory_tier = "executive"
            memory_capacity = 10000
        elif experience == ExperienceLevel.SENIOR:
            memory_tier = "senior"
            memory_capacity = 5000
        else:
            memory_tier = "standard"
            memory_capacity = 2000
            
        # Generate anchors
        t1_anchor = random.randint(1000, 9999)
        srb_anchor = random.randint(100, 999)
        
        # DLP tag
        timestamp = datetime.now().isoformat()
        dlp_tag = f"DLP:crew_{role.replace(' ', '_')}_{timestamp}"
        
        return QuantumProfile(
            skill_vector=skill_vector,
            cultural_score=cultural_score,
            memory_tier=memory_tier,
            memory_capacity=memory_capacity,
            t1_anchor=t1_anchor,
            srb_anchor=srb_anchor,
            dlp_tag=dlp_tag
        )
    
    def _generate_certifications(self, role: str, specializations: List[str]) -> List[str]:
        """Generate relevant certifications"""
        certs = []
        
        if "HR" in role or "Human Resources" in role:
            certs.extend([
                "SHRM-SCP (Senior Certified Professional)",
                "Organizational Psychology Certification",
                "Talent Management Specialist"
            ])
        
        if "Security" in role or "Cybersecurity" in role:
            certs.extend([
                "CISSP (Certified Information Systems Security Professional)",
                "Security Operations Certification"
            ])
            
        # Add specialization-specific certs
        for spec in specializations[:2]:
            certs.append(f"Advanced {spec.replace('_', ' ').title()} Certification")
            
        return certs
    
    def _calculate_years_experience(self, level: ExperienceLevel) -> int:
        """Calculate years of experience"""
        ranges = {
            ExperienceLevel.SENIOR: (15, 25),
            ExperienceLevel.EXPERIENCED: (7, 12),
            ExperienceLevel.INTERMEDIATE: (3, 6),
            ExperienceLevel.JUNIOR: (0, 2)
        }
        min_years, max_years = ranges[level]
        return random.randint(min_years, max_years)
    
    def _generate_strengths(
        self, specializations: List[str], experience: ExperienceLevel
    ) -> List[str]:
        """Generate key strengths"""
        strengths = []
        
        # Specialization-based strengths
        for spec in specializations[:3]:
            strengths.append(f"Expert in {spec.replace('_', ' ')}")
            
        # Experience-based strengths
        if experience in [ExperienceLevel.SENIOR, ExperienceLevel.EXPERIENCED]:
            strengths.extend([
                "Strategic planning and execution",
                "Cross-functional collaboration",
                "Mentoring and team development"
            ])
        else:
            strengths.extend([
                "Quick learner and adaptable",
                "Strong technical foundation",
                "Collaborative team player"
            ])
            
        return strengths
    
    def _generate_development_areas(self, experience: ExperienceLevel) -> List[str]:
        """Generate development opportunities"""
        if experience == ExperienceLevel.SENIOR:
            return [
                "Enterprise-scale transformation experience",
                "Cross-organizational influence"
            ]
        elif experience == ExperienceLevel.EXPERIENCED:
            return [
                "Executive leadership experience",
                "Strategic visioning at scale"
            ]
        else:
            return [
                "Leadership experience",
                "Complex problem-solving at scale",
                "Cross-functional project management"
            ]
    
    def _determine_reports_to(self, department: Department, rank: Rank) -> Optional[str]:
        """Determine reporting structure"""
        if department == Department.HUMAN_RESOURCES:
            if rank == Rank.LIEUTENANT_COMMANDER:
                return "Commander Thorne"
            else:
                return "Chief Human Resources Officer"
        elif rank in [Rank.COMMANDER, Rank.LIEUTENANT_COMMANDER]:
            return "Commander Thorne"
        else:
            return f"{department.value} Department Head"


# Example usage for testing
if __name__ == "__main__":
    import logging
    logging.basicConfig(level=logging.INFO)
    logger = logging.getLogger(__name__)
    
    generator = CharacterGenerator()
    
    # Generate Chief HR Officer candidates
    candidates = generator.generate_character(
        role="Chief Human Resources Officer",
        department=Department.HUMAN_RESOURCES,
        rank=Rank.LIEUTENANT_COMMANDER,
        specializations=["talent_acquisition", "organizational_development", "workforce_planning"],
        experience_level=ExperienceLevel.SENIOR,
        count=3
    )
    
    logger.info("Generated %d candidates for Chief HR Officer", len(candidates))
    for i, candidate in enumerate(candidates, 1):
        logger.info("Candidate %d: %s (%s)", i, candidate.name, candidate.rank.value)
        logger.info("  Experience: %d years", candidate.years_experience)
        logger.info("  Specializations: %s", ', '.join(candidate.specializations))
        logger.info("  Cultural Score: %.2f", candidate.quantum_profile.cultural_score)
        logger.info("  Background: %s...", candidate.background_story[:100])
