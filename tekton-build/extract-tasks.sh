#!/bin/bash
# Tekton Pipeline Task Extractor - Shell Wrapper
#
# This script provides a convenient wrapper for the Python task extractor.
# It checks for dependencies and runs the Python script.
#
# Usage:
#   ./extract-tasks.sh <pipeline-file> [output-dir]

set -e

# Check if Python 3 is available
if ! command -v python3 &> /dev/null; then
    echo "Error: python3 is required but not found"
    exit 1
fi

# Check if PyYAML is installed
if ! python3 -c "import yaml" 2>/dev/null; then
    echo "Error: PyYAML is required but not installed"
    echo "Install it with: pip install PyYAML"
    exit 1
fi

# Get the directory where this script is located
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"

# Run the Python script
python3 "$SCRIPT_DIR/extract-tasks.py" "$@"