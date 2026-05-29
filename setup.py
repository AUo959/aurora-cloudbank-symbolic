from setuptools import find_packages, setup

setup(
    name="aurora-cloudbank-symbolic",
    version="1.0.0",
    description="Quantum-Symbolic Computing Platform with AI Integration",
    packages=find_packages(where="src"),
    package_dir={"": "src"},
    # NOTE (#834): aligned with sdk/python/pyproject.toml, cli/pyproject.toml,
    # CLAUDE.md, and Dockerfile (3.11). k8s/Dockerfile and runtime.txt run on
    # 3.12, which satisfies this floor. #836 plans to delete setup.py in favor
    # of PEP 621 pyproject.toml; until then, keep this file consistent.
    python_requires=">=3.11",
    install_requires=[
        "black>=23.0.0",
        "flake8>=6.0.0",
        "pytest>=7.0.0",
    ],
    extras_require={
        "dev": ["coverage>=7.0.0"],
    },
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
    ],
)
