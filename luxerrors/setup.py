
"""
Setup script for LuxErrors - Universal Error Handling System
"""

from setuptools import setup, find_packages

setup(
    name="luxerrors",
    version="1.0.0",
    description="Universal error handling system extracted from LuxDB",
    long_description=open("README.md").read() if __name__ == "__main__" else "",
    long_description_content_type="text/markdown",
    author="LuxDB Team",
    author_email="team@luxdb.dev",
    url="https://github.com/luxdb/luxerrors",
    packages=find_packages(),
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
        "Topic :: Software Development :: Libraries :: Python Modules",
        "Topic :: System :: Logging",
        "Topic :: Software Development :: Quality Assurance",
    ],
    python_requires=">=3.8",
    install_requires=[],
    extras_require={
        "dev": [
            "pytest>=7.0.0",
            "pytest-cov>=4.0.0",
            "black>=22.0.0",
            "isort>=5.0.0",
            "mypy>=1.0.0",
        ]
    },
    keywords=["error-handling", "logging", "exceptions", "validation", "debugging"],
    project_urls={
        "Bug Reports": "https://github.com/luxdb/luxerrors/issues",
        "Source": "https://github.com/luxdb/luxerrors",
        "Documentation": "https://luxerrors.readthedocs.io",
    }
)
