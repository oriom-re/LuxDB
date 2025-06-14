from setuptools import setup, find_packages

setup(
    name="luxdb",
    version="0.1.0",
    author="Oriom (ΩO)",
    description="LuxDB — biblioteka z rodu astralnego, do zarządzania relacyjną pamięcią.",
    long_description=open("README.md").read(),
    long_description_content_type="text/markdown",
    url="https://github.com/oriom-re/luxdb",
    packages=find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "Operating System :: OS Independent",
    ],
    python_requires='>=3.7',
)
