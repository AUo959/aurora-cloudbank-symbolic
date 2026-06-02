from pathlib import Path

from setuptools import find_packages, setup


def _load_requirements(filename):
    """Read a requirements file, returning a list of PEP 508 specifiers.

    Skips blank lines, comment lines (#), and recursive-include directives (-r).
    Strips inline comments so entries like ``pkg>=1.0  # reason`` become ``pkg>=1.0``.
    """
    lines = []
    for raw in Path(filename).read_text().splitlines():
        line = raw.strip()
        if not line or line.startswith("#") or line.startswith("-r"):
            continue
        # Strip inline comment and trailing whitespace.
        line = line.split("#")[0].strip()
        if line:
            lines.append(line)
    return lines


setup(
    name="aurora-cloudbank-symbolic",
    version="1.0.0",
    description="Quantum-Symbolic Computing Platform with AI Integration",
    packages=find_packages(where="src"),
    package_dir={"": "src"},
    python_requires=">=3.11",
    # Single source of truth: requirements.txt drives production install_requires.
    # Adding a package here means adding it to requirements.txt — not both places.
    install_requires=_load_requirements("requirements.txt"),
    extras_require={
        "dev": _load_requirements("requirements-dev.txt"),
        "optional": _load_requirements("requirements-optional.txt"),
    },
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
    ],
)
