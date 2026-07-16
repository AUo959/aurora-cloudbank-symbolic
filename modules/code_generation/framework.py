"""
Ultra-High-Fidelity Code Generation Framework
==============================================

Anchor: CODE-GEN-FRAMEWORK-001
Version: 1.0.0
Team: Orion Station Crew
DLP: CONFIDENTIAL
Ethics: Picard_Delta_3
Aurora Integration: ENABLED

A meta-programming framework for generating ultra-high-fidelity code modules
that meet institutional standards for reliability, maintainability, and auditability.

Core Capabilities:
- Template-based code generation with full type annotations
- Automatic docstring generation with examples
- Security validation and best practices enforcement
- Audit trail generation for all generated code
- Test stub generation (unit, integration, edge cases)
- Integration scaffolding for Aurora infrastructure
"""

import logging
from datetime import datetime
from typing import Dict, Any, List, Tuple
from dataclasses import dataclass, field
from enum import Enum

# Try to import Aurora agent for strategic oversight
try:
    from src.agents.aurora_consciousness_agent import get_aurora_agent

    AURORA_AVAILABLE = True
except ImportError:
    AURORA_AVAILABLE = False


class CodeQualityStandard(Enum):
    """Code quality standard levels"""

    BASIC = "basic"  # Minimal standards
    STANDARD = "standard"  # Production ready
    ULTRA_HIGH_FIDELITY = "ultra_high_fidelity"  # Maximum quality


class ComponentType(Enum):
    """Types of code components to generate"""

    FUNCTION = "function"
    CLASS = "class"
    MODULE = "module"
    TEST_SUITE = "test_suite"
    INTEGRATION = "integration"


@dataclass
class FunctionSpec:
    """
    Specification for generating a function.

    Attributes:
        name: Function name
        description: Brief description of what function does
        parameters: List of (name, type, description) tuples
        return_type: Return type annotation
        return_description: Description of return value
        raises: List of (exception_type, description) tuples
        examples: List of usage example strings
        notes: Additional implementation notes
        security_considerations: Security requirements and validations
        integrations: List of integration points (registry, telemetry, etc.)
    """

    name: str
    description: str
    parameters: List[Tuple[str, str, str]]  # (name, type, description)
    return_type: str
    return_description: str
    raises: List[Tuple[str, str]] = field(default_factory=list)  # (exception, description)
    examples: List[str] = field(default_factory=list)
    notes: List[str] = field(default_factory=list)
    security_considerations: List[str] = field(default_factory=list)
    integrations: List[str] = field(default_factory=list)
    is_async: bool = False


@dataclass
class ClassSpec:
    """
    Specification for generating a class.

    Attributes:
        name: Class name
        description: Brief description of class purpose
        attributes: List of (name, type, description) tuples
        methods: List of FunctionSpec objects for methods
        base_classes: List of base class names
        integrations: List of integration points
    """

    name: str
    description: str
    attributes: List[Tuple[str, str, str]] = field(default_factory=list)
    methods: List[FunctionSpec] = field(default_factory=list)
    base_classes: List[str] = field(default_factory=list)
    integrations: List[str] = field(default_factory=list)


@dataclass
class GeneratedCode:
    """
    Result of code generation.

    Attributes:
        code: Generated Python code
        tests: Generated test code
        documentation: Generated documentation
        audit_trail: Audit trail of generation process
        metadata: Additional metadata about generation
    """

    code: str
    tests: str
    documentation: str
    audit_trail: List[Dict[str, Any]]
    metadata: Dict[str, Any]


class UltraHighFidelityCodeGenerator:
    """
    Meta-programming framework for generating production-ready code.

    Generates code modules that meet Aurora CloudBank Symbolic standards:
    - Full type annotations (Python 3.11+)
    - Comprehensive docstrings with examples
    - Security validation and input sanitization
    - Audit trail generation
    - Integration with Aurora infrastructure
    - Complete test coverage

    Example:
        >>> generator = UltraHighFidelityCodeGenerator()
        >>> spec = FunctionSpec(
        ...     name='calculate_risk',
        ...     description='Calculate risk score for decision',
        ...     parameters=[('scenario', 'Dict[str, Any]', 'Scenario to analyze')],
        ...     return_type='float',
        ...     return_description='Risk score between 0.0 and 1.0'
        ... )
        >>> result = generator.generate_function(spec)
        >>> print(result.code)
    """

    def __init__(
        self,
        quality_standard: CodeQualityStandard = CodeQualityStandard.ULTRA_HIGH_FIDELITY,
        enable_aurora_oversight: bool = True,
    ):
        """
        Initialize code generation framework.

        Args:
            quality_standard: Quality standard to enforce
            enable_aurora_oversight: Whether to enable Aurora strategic oversight
        """
        self.logger = self._setup_logging()
        self.quality_standard = quality_standard
        self.enable_aurora_oversight = enable_aurora_oversight and AURORA_AVAILABLE
        self.generation_count = 0

        # Initialize Aurora integration if enabled
        self.aurora = get_aurora_agent() if self.enable_aurora_oversight else None
        if self.aurora:
            self.logger.info("🌌 Aurora oversight enabled for code generation")

        self.logger.info(f"🏗️ Code Generation Framework initialized (standard={quality_standard.value})")

    def _setup_logging(self) -> logging.Logger:
        """Setup structured logging"""
        logger = logging.getLogger(__name__)
        if not logger.handlers:
            handler = logging.StreamHandler()
            formatter = logging.Formatter("[%(asctime)s] %(levelname)s - %(message)s", datefmt="%Y-%m-%d %H:%M:%S")
            handler.setFormatter(formatter)
            logger.addHandler(handler)
            logger.setLevel(logging.INFO)
        return logger

    def _generate_function_signature(self, spec: FunctionSpec) -> str:
        """
        Generate function signature with type annotations.

        Args:
            spec: Function specification

        Returns:
            Function signature string
        """
        # Build parameter list with type annotations
        params = []
        for param_name, param_type, _ in spec.parameters:
            params.append(f"{param_name}: {param_type}")

        params_str = ", ".join(params)

        # Add async if specified
        async_prefix = "async " if spec.is_async else ""

        # Build signature
        signature = f"{async_prefix}def {spec.name}({params_str}) -> {spec.return_type}:"

        return signature

    @staticmethod
    def _append_docstring_section(lines: List[str], heading: str, content: List[str], *, separate: bool = True) -> None:
        """Append one generated docstring section when content is present."""
        if not content:
            return
        if separate:
            lines.append("")
        lines.append(f"    {heading}:")
        lines.extend(content)

    @staticmethod
    def _format_parameter_docs(parameters: List[Tuple[str, str, str]]) -> List[str]:
        """Format parameter descriptions for a generated docstring."""
        return [f"        {name}: {description}" for name, _type, description in parameters]

    @staticmethod
    def _format_pair_docs(items: List[Tuple[str, str]]) -> List[str]:
        """Format name-description pairs for a generated docstring."""
        return [f"        {name}: {description}" for name, description in items]

    @staticmethod
    def _format_item_docs(items: List[str], prefix: str = "") -> List[str]:
        """Format simple items for a generated docstring."""
        return [f"        {prefix}{item}" for item in items]

    @staticmethod
    def _format_return_doc(description: str) -> List[str]:
        """Format a return description only when one is present."""
        if not description:
            return []
        return [f"        {description}"]

    def _generate_function_docstring(self, spec: FunctionSpec) -> str:
        """
        Generate comprehensive docstring following Google/NumPy style.

        Args:
            spec: Function specification

        Returns:
            Formatted docstring
        """
        lines = ['    """']
        lines.append(f"    {spec.description}")

        if any((spec.parameters, spec.raises, spec.examples, spec.notes)):
            lines.append("")  # Blank line after description

        self._append_docstring_section(
            lines,
            "Args",
            self._format_parameter_docs(spec.parameters),
            separate=False,
        )
        self._append_docstring_section(
            lines,
            "Returns",
            self._format_return_doc(spec.return_description),
            separate=bool(spec.parameters),
        )
        self._append_docstring_section(
            lines,
            "Raises",
            self._format_pair_docs(spec.raises),
        )
        self._append_docstring_section(
            lines,
            "Example",
            self._format_item_docs(spec.examples, ">>> "),
        )
        self._append_docstring_section(
            lines,
            "Notes",
            self._format_item_docs(spec.notes),
        )
        self._append_docstring_section(
            lines,
            "Security",
            self._format_item_docs(spec.security_considerations, "• "),
        )
        self._append_docstring_section(
            lines,
            "Integration",
            self._format_item_docs(spec.integrations, "• "),
        )

        lines.append('    """')

        return "\n".join(lines)

    @staticmethod
    def _generate_validation_lines(spec: FunctionSpec) -> List[str]:
        """Generate dictionary input checks requested by the specification."""
        if not spec.security_considerations:
            return []

        lines = ["    # Security validation"]
        for param_name, param_type, _param_description in spec.parameters:
            if "Dict" in param_type or "Any" in param_type:
                lines.append(f"    if not isinstance({param_name}, dict):")
                lines.append(f"        raise ValueError(f'{param_name} must be a dictionary')")
        lines.append("")
        return lines

    @staticmethod
    def _generate_logging_lines(spec: FunctionSpec) -> List[str]:
        """Generate self-contained logging setup for the emitted function."""
        param_names = [parameter[0] for parameter in spec.parameters]
        param_log = ", ".join(f"{name}={{{name}}}" for name in param_names[:2])
        return [
            "    # Logging",
            "    import logging",
            "    logger = logging.getLogger(__name__)",
            f"    logger.info(f'🔧 {spec.name} called: {param_log}')",
            "",
        ]

    @staticmethod
    def _generate_error_lines(spec: FunctionSpec) -> List[str]:
        """Generate the declared placeholder error contract, if any."""
        if not spec.raises:
            return []
        first_error = spec.raises[0][0]
        return [
            "    # Error handling",
            "    if result is None:",
            f"        raise {first_error}('Implementation required')",
            "",
        ]

    def _generate_function_body(self, spec: FunctionSpec) -> str:
        """Generate a self-contained function body."""
        lines = self._generate_validation_lines(spec)
        lines.extend(self._generate_logging_lines(spec))
        lines.extend(
            [
                "    # Main implementation",
                "    # TODO: Implement core logic here",
                "    result = None  # Replace with actual computation",
                "",
            ]
        )
        lines.extend(self._generate_error_lines(spec))
        lines.append("    return result")
        return "\n".join(lines)

    def _record_function_oversight(
        self,
        spec: FunctionSpec,
        audit_trail: List[Dict[str, Any]],
        timestamp: str,
    ) -> None:
        """Record generation-time Aurora oversight when it is available."""
        if not self.aurora:
            return
        thought = self.aurora.think(
            {
                "type": "code_generation",
                "component": "function",
                "name": spec.name,
                "standard": self.quality_standard.value,
            }
        )
        audit_trail.append(
            {
                "timestamp": timestamp,
                "step": "aurora_oversight",
                "thought_id": thought.thought_id,
                "coherence": thought.quantum_coherence,
            }
        )

    def _build_generated_code(
        self,
        *,
        code: str,
        tests: str,
        documentation: str,
        audit_trail: List[Dict[str, Any]],
        component_type: ComponentType,
        name: str,
    ) -> GeneratedCode:
        """Build a generated-code result with consistent metadata."""
        return GeneratedCode(
            code=code,
            tests=tests,
            documentation=documentation,
            audit_trail=audit_trail,
            metadata={
                "generation_number": self.generation_count,
                "standard": self.quality_standard.value,
                "component_type": component_type.value,
                "name": name,
            },
        )

    def generate_function(self, spec: FunctionSpec, generate_tests: bool = True) -> GeneratedCode:
        """
        Generate complete function with documentation and tests.

        Args:
            spec: Function specification
            generate_tests: Whether to generate test stubs

        Returns:
            GeneratedCode object with code, tests, docs, and audit trail

        Raises:
            ValueError: If specification is invalid
        """
        audit_trail = []
        timestamp = datetime.now().isoformat()

        self._record_function_oversight(spec, audit_trail, timestamp)

        # Generate components
        signature = self._generate_function_signature(spec)
        docstring = self._generate_function_docstring(spec)
        body = self._generate_function_body(spec)

        # Assemble function
        code_lines = [signature, docstring, body]
        code = "\n".join(code_lines)

        audit_trail.append(
            {
                "timestamp": datetime.now().isoformat(),
                "step": "code_generation",
                "component": "function",
                "name": spec.name,
                "lines": len(code.split("\n")),
            }
        )

        # Generate tests if requested
        tests = ""
        if generate_tests:
            tests = self._generate_function_tests(spec)
            audit_trail.append(
                {
                    "timestamp": datetime.now().isoformat(),
                    "step": "test_generation",
                    "test_count": len(tests.split("def test_")),
                }
            )

        # Generate documentation
        documentation = self._generate_function_documentation(spec)

        # Increment counter
        self.generation_count += 1

        self.logger.info(
            f"✨ Generated function '{spec.name}' "
            f"({len(code.split(chr(10)))} lines, standard={self.quality_standard.value})"
        )

        return self._build_generated_code(
            code=code,
            tests=tests,
            documentation=documentation,
            audit_trail=audit_trail,
            component_type=ComponentType.FUNCTION,
            name=spec.name,
        )

    def _generate_function_tests(self, spec: FunctionSpec) -> str:
        """
        Generate comprehensive test suite for function.

        Args:
            spec: Function specification

        Returns:
            Test code string
        """
        lines = []
        lines.append("import pytest")
        lines.append("from unittest.mock import Mock, patch")
        lines.append("")
        lines.append("")

        # Test basic functionality
        lines.append(f"def test_{spec.name}_basic():")
        lines.append('    """Test basic functionality"""')
        lines.append("    # TODO: Implement basic test")
        lines.append("    pass")
        lines.append("")
        lines.append("")

        # Test with valid inputs
        lines.append(f"def test_{spec.name}_valid_inputs():")
        lines.append('    """Test with various valid inputs"""')
        lines.append("    # TODO: Test normal cases")
        lines.append("    pass")
        lines.append("")
        lines.append("")

        # Test error conditions
        if spec.raises:
            for exc_type, _ in spec.raises:
                test_name = f"test_{spec.name}_raises_{exc_type.lower()}"
                lines.append(f"def {test_name}():")
                lines.append(f'    """Test that {exc_type} is raised appropriately"""')
                lines.append(f"    with pytest.raises({exc_type}):")
                lines.append("        # TODO: Call function with invalid input")
                lines.append("        pass")
                lines.append("")
                lines.append("")

        # Test edge cases
        lines.append(f"def test_{spec.name}_edge_cases():")
        lines.append('    """Test edge cases"""')
        lines.append("    # TODO: Test boundary conditions")
        lines.append("    # TODO: Test empty inputs")
        lines.append("    # TODO: Test extreme values")
        lines.append("    pass")
        lines.append("")
        lines.append("")

        # Integration test
        if spec.integrations:
            lines.append("@pytest.mark.integration")
            lines.append(f"def test_{spec.name}_integration():")
            lines.append('    """Test integration with Aurora infrastructure"""')
            lines.append("    # TODO: Test registry integration")
            lines.append("    # TODO: Test telemetry logging")
            lines.append("    # TODO: Test Aurora oversight")
            lines.append("    pass")

        return "\n".join(lines)

    def _generate_function_documentation(self, spec: FunctionSpec) -> str:
        """
        Generate markdown documentation for function.

        Args:
            spec: Function specification

        Returns:
            Markdown documentation string
        """
        lines = []
        lines.append(f"# `{spec.name}()`")
        lines.append("")
        lines.append(f"**Description:** {spec.description}")
        lines.append("")

        # Parameters
        if spec.parameters:
            lines.append("## Parameters")
            lines.append("")
            for param_name, param_type, param_desc in spec.parameters:
                lines.append(f"- **`{param_name}`** (`{param_type}`): {param_desc}")
            lines.append("")

        # Returns
        lines.append("## Returns")
        lines.append("")
        lines.append(f"**Type:** `{spec.return_type}`")
        lines.append("")
        lines.append(spec.return_description)
        lines.append("")

        # Examples
        if spec.examples:
            lines.append("## Examples")
            lines.append("")
            lines.append("```python")
            for example in spec.examples:
                lines.append(example)
            lines.append("```")
            lines.append("")

        # Notes
        if spec.notes:
            lines.append("## Notes")
            lines.append("")
            for note in spec.notes:
                lines.append(f"- {note}")
            lines.append("")

        return "\n".join(lines)

    def _record_class_oversight(
        self,
        spec: ClassSpec,
        audit_trail: List[Dict[str, Any]],
        timestamp: str,
    ) -> None:
        """Record generation-time Aurora oversight for a class."""
        if not self.aurora:
            return
        thought = self.aurora.think(
            {
                "type": "code_generation",
                "component": "class",
                "name": spec.name,
                "method_count": len(spec.methods),
            }
        )
        audit_trail.append(
            {
                "timestamp": timestamp,
                "step": "aurora_oversight",
                "thought_id": thought.thought_id,
            }
        )

    @staticmethod
    def _generate_class_declaration(spec: ClassSpec) -> List[str]:
        """Generate imports and the class declaration."""
        if spec.base_classes:
            bases = ", ".join(spec.base_classes)
            declaration = f"class {spec.name}({bases}):"
        else:
            declaration = f"class {spec.name}:"
        return ["import logging", "", declaration]

    @staticmethod
    def _generate_class_docstring(spec: ClassSpec) -> List[str]:
        """Generate the class-level documentation block."""
        lines = ['    """', f"    {spec.description}"]
        if spec.attributes:
            lines.extend(["", "    Attributes:"])
            for attr_name, attr_type, attr_desc in spec.attributes:
                lines.append(f"        {attr_name} ({attr_type}): {attr_desc}")
        if spec.integrations:
            lines.extend(["", "    Integration:"])
            for integration in spec.integrations:
                lines.append(f"        • {integration}")
        lines.extend(['    """', ""])
        return lines

    @staticmethod
    def _generate_class_initializer(spec: ClassSpec) -> List[str]:
        """Generate a self-contained class initializer."""
        lines = [
            "    def __init__(self):",
            '        """Initialize the class"""',
            "        self.logger = logging.getLogger(__name__)",
        ]
        for attr_name, _attr_type, _attr_desc in spec.attributes:
            lines.append(f"        self.{attr_name} = None  # TODO: Initialize")
        lines.append("")
        return lines

    def _generate_class_methods(self, spec: ClassSpec) -> List[str]:
        """Generate and indent every declared class method."""
        lines: List[str] = []
        for method_spec in spec.methods:
            method_code = self.generate_function(method_spec, generate_tests=False)
            for line in method_code.code.split("\n"):
                lines.append(f"    {line}" if line else "")
            lines.append("")
        return lines

    def generate_class(self, spec: ClassSpec, generate_tests: bool = True) -> GeneratedCode:
        """
        Generate complete class with methods, documentation, and tests.

        Args:
            spec: Class specification
            generate_tests: Whether to generate test stubs

        Returns:
            GeneratedCode object with code, tests, docs, and audit trail

        Raises:
            ValueError: If specification is invalid
        """
        audit_trail = []
        timestamp = datetime.now().isoformat()

        self._record_class_oversight(spec, audit_trail, timestamp)
        lines = self._generate_class_declaration(spec)
        lines.extend(self._generate_class_docstring(spec))
        lines.extend(self._generate_class_initializer(spec))
        lines.extend(self._generate_class_methods(spec))

        code = "\n".join(lines)

        audit_trail.append(
            {
                "timestamp": datetime.now().isoformat(),
                "step": "code_generation",
                "component": "class",
                "name": spec.name,
                "methods": len(spec.methods),
            }
        )

        tests = self._generate_class_tests(spec) if generate_tests else ""

        # Generate documentation
        documentation = f"# Class: {spec.name}\n\n{spec.description}"

        self.logger.info(
            f"✨ Generated class '{spec.name}' "
            f"({len(spec.methods)} methods, standard={self.quality_standard.value})"
        )

        return self._build_generated_code(
            code=code,
            tests=tests,
            documentation=documentation,
            audit_trail=audit_trail,
            component_type=ComponentType.CLASS,
            name=spec.name,
        )

    def _generate_class_tests(self, spec: ClassSpec) -> str:
        """Generate test suite for class"""
        lines = []
        lines.append("import pytest")
        lines.append("")
        lines.append("")
        lines.append(f"class Test{spec.name}:")
        lines.append(f'    """Test suite for {spec.name}"""')
        lines.append("")
        lines.append("    def test_initialization(self):")
        lines.append('        """Test class initialization"""')
        lines.append("        # TODO: Implement")
        lines.append("        pass")
        lines.append("")

        # Test each method
        for method_spec in spec.methods:
            lines.append(f"    def test_{method_spec.name}(self):")
            lines.append(f'        """Test {method_spec.name} method"""')
            lines.append("        # TODO: Implement")
            lines.append("        pass")
            lines.append("")

        return "\n".join(lines)

    def get_statistics(self) -> Dict[str, Any]:
        """
        Get code generation statistics.

        Returns:
            Dictionary with generation metrics
        """
        return {
            "total_generations": self.generation_count,
            "quality_standard": self.quality_standard.value,
            "aurora_oversight": self.enable_aurora_oversight,
            "aurora_available": AURORA_AVAILABLE,
        }
