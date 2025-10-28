# User Guide - ConvertKeylogApp

## Table of Contents

1. [Introduction](#introduction)
2. [Installation](#installation)
3. [Getting Started](#getting-started)
4. [Features](#features)
5. [Troubleshooting](#troubleshooting)

## Introduction

ConvertKeylogApp is a modern desktop application for converting keylog data with support for multiple input/output formats and advanced processing capabilities.

## Installation

### Requirements

- Python 3.8 or higher
- Windows/macOS/Linux

### Installation Steps

```bash
# Clone the repository
git clone https://github.com/singed2905/ConvertKeylogApp.git
cd ConvertKeylogApp

# Install dependencies
pip install -r requirements.txt

# Run the application
python -m app.main
```

## Getting Started

### Basic Workflow

1. **Launch Application**: Run `python -m app.main`
2. **Select Input File**: Choose your keylog file (Excel, CSV, or JSON)
3. **Configure Conversion**: Select conversion type and options
4. **Process Data**: Click convert to start processing
5. **Save Results**: Export converted data to desired format

### Supported File Formats

#### Input Formats
- Excel (.xlsx, .xls)
- CSV (.csv)
- JSON (.json)

#### Output Formats
- Excel (.xlsx)
- CSV (.csv)
- JSON (.json)

## Features

### Conversion Types

1. **Keylog Conversion**: Main keylog data conversion
2. **Equation Conversion**: Mathematical equation processing
3. **Geometry Conversion**: Geometric data transformation

### Advanced Features

- **Batch Processing**: Process multiple files at once
- **Data Validation**: Automatic input validation
- **Progress Tracking**: Real-time progress monitoring
- **Error Handling**: Comprehensive error reporting
- **Theme Support**: Light and dark themes

## Troubleshooting

### Common Issues

**Q: Application won't start**
A: Ensure Python 3.8+ is installed and all dependencies are met

**Q: File format not supported**
A: Check the supported formats list and ensure file is not corrupted

**Q: Conversion fails**
A: Check the log files in the logs/ directory for detailed error information

### Getting Help

For additional support:
1. Check the [Developer Guide](developer_guide.md)
2. Review log files for error details
3. Submit issues on GitHub repository
