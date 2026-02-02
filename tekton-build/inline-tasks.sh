#!/bin/bash
# Tekton Pipeline Task Inliner - Shell Wrapper
#
# This script provides a convenient wrapper for the Python task inliner.
# It checks for dependencies and runs the Python script.
#
# Usage:
#   ./inline-tasks.sh <pipeline-file> [output-file]

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
python3 "$SCRIPT_DIR/inline-tasks.py" "$@"