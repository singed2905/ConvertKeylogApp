"""Setup script for ConvertKeylogApp."""

from setuptools import setup, find_packages
from pathlib import Path

this_directory = Path(__file__).parent
long_description = (this_directory / "README.md").read_text(encoding='utf-8')

setup(
    name="ConvertKeylogApp",
    version="0.1.0",
    author="singed2905",
    author_email="your.email@example.com",
    description="Ứng dụng chuyển đổi keylog với architecture hiện đại",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/singed2905/ConvertKeylogApp",
    packages=find_packages(),
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Topic :: Software Development :: Libraries :: Python Modules",
        "Topic :: Utilities",
        "Environment :: X11 Applications",
        "Environment :: Win32 (MS Windows)",
        "Environment :: MacOS X",
    ],
    python_requires=">=3.8",
    install_requires=[
        "pandas>=1.5.0",
        "openpyxl>=3.0.0",
        "numpy>=1.21.0",
        "pydantic>=1.10.0",
        "loguru>=0.6.0",
        "orjson>=3.8.0",
        "python-dateutil>=2.8.0",
        "filetype>=1.2.0",
    ],
    extras_require={
        "dev": [
            "pytest>=7.0.0",
            "pytest-cov>=4.0.0",
            "black>=22.0.0",
            "flake8>=5.0.0",
            "mypy>=0.991",
            "sphinx>=5.0.0",
        ],
    },
    entry_points={
        "console_scripts": [
            "convertkeylogs=app.main:main",
        ],
        "gui_scripts": [
            "convertkeylogs-gui=app.main:main",
        ],
    },
    include_package_data=True,
    package_data={
        "config": ["*.json"],
        "resources": ["icons/*", "templates/*"],
    },
    zip_safe=False,
)
