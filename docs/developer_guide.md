# Developer Guide - ConvertKeylogApp

## Table of Contents

1. [Development Setup](#development-setup)
2. [Project Structure](#project-structure)
3. [Architecture](#architecture)
4. [Contributing](#contributing)
5. [Testing](#testing)
6. [Deployment](#deployment)

## Development Setup

### Prerequisites

- Python 3.8+
- Git
- Virtual environment (recommended)

### Setup Steps

```bash
# Clone repository
git clone https://github.com/singed2905/ConvertKeylogApp.git
cd ConvertKeylogApp

# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Install development dependencies
pip install -r requirements-dev.txt

# Run tests
python -m pytest tests/

# Run application
python -m app.main
```

## Project Structure

```
ConvertKeylogApp/
├── app/                    # Main application
├── core/                   # Business logic
│   ├── converters/         # Conversion engines
│   ├── processors/         # Data processors
│   └── models/            # Data models
├── gui/                   # User interface
│   ├── components/        # Reusable components
│   ├── windows/           # Application windows
│   └── styles/            # Themes and styling
├── config/                # Configuration files
├── utils/                 # Utility functions
├── tests/                 # Test suite
├── docs/                  # Documentation
└── resources/             # Static resources
```

## Architecture

### Design Principles

1. **Clean Architecture**: Separation of concerns with clear layers
2. **SOLID Principles**: Single responsibility, open/closed, etc.
3. **Testability**: All components are unit testable
4. **Modularity**: Loosely coupled, highly cohesive modules

### Layer Structure

```
GUI Layer (gui/)
    ↓
Application Layer (app/)
    ↓
Core Business Logic (core/)
    ↓
Utilities & Infrastructure (utils/)
```

### Key Components

- **Converters**: Handle data transformation logic
- **Processors**: Manage file I/O and data processing
- **Models**: Define data structures and schemas
- **GUI Components**: Reusable UI elements
- **Configuration**: JSON-based configuration management

## Contributing

### Code Style

- Follow PEP 8 guidelines
- Use type hints throughout
- Document all public methods
- Maximum line length: 88 characters

### Development Workflow

1. Create feature branch: `git checkout -b feature/new-feature`
2. Make changes and add tests
3. Run test suite: `python -m pytest`
4. Run linting: `flake8 .`
5. Run formatting: `black .`
6. Commit changes: `git commit -m "Add new feature"`
7. Push branch: `git push origin feature/new-feature`
8. Create pull request

### Commit Guidelines

- Use present tense: "Add feature" not "Added feature"
- Keep first line under 50 characters
- Reference issues and pull requests when applicable

## Testing

### Test Structure

```
tests/
├── unit/              # Unit tests
├── integration/       # Integration tests
└── fixtures/          # Test data
```

### Running Tests

```bash
# Run all tests
python -m pytest

# Run with coverage
python -m pytest --cov=.

# Run specific test file
python -m pytest tests/unit/test_converters.py

# Run with verbose output
python -m pytest -v
```

### Writing Tests

- Write tests for all new functionality
- Use descriptive test method names
- Follow AAA pattern: Arrange, Act, Assert
- Mock external dependencies

## Deployment

### Building Distribution

```bash
# Build wheel
python setup.py bdist_wheel

# Build source distribution
python setup.py sdist
```

### Creating Executable

```bash
# Install PyInstaller
pip install pyinstaller

# Create executable
pyinstaller --onefile --windowed app/main.py
```

### Environment Configuration

- Development: Use `config/app_config.json`
- Production: Override with environment-specific configs
- Logging: Configure in `utils/logger.py`
