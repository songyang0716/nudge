#!/bin/bash

# Nudge - Start Script
# This script starts the Nudge application

set -e

# Get the directory where this script is located
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

# Change to the project directory
cd "$SCRIPT_DIR"

# Check if poetry is installed
if ! command -v poetry &> /dev/null; then
    echo "❌ Poetry is not installed. Please install Poetry first:"
    echo "   https://python-poetry.org/docs/#installation"
    exit 1
fi

# Check if poetry.lock exists
if [ ! -f "poetry.lock" ]; then
    echo "⚠️  Dependencies not installed. Installing now..."
    poetry install
fi

# Start the application
echo "🚀 Starting Nudge..."
poetry run nudge
