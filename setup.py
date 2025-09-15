from setuptools import find_packages, setup

setup(
    name="aurora-cloudbank-symbolic",
    version="1.0.0",
    description="Aurora Cloudbank Symbolic Simulation Engine",
    packages=find_packages(where="src"),
    package_dir={"": "src"},
    python_requires=">=3.11",
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
    ],
)
