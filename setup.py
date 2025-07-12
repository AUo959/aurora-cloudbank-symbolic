from setuptools import setup, find_packages

setup(
    name="aurora-cloudbank-symbolic",
    version="1.0.0",
    description="Aurora Cloudbank Symbolic Simulation Engine",
    packages=find_packages(where="src"),
    package_dir={"": "src"},
    python_requires=">=3.8",
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
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
    ],
)
