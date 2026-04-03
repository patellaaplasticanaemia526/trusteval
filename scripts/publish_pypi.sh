#!/bin/bash
# TrustEval — Enterprise LLM Evaluation Framework
# Author: Antrixsh Gupta | https://www.linkedin.com/in/antrixshgupta
# License: MIT

set -e

echo "Publishing TrustEval to PyPI..."

# Clean previous builds
rm -rf dist/ build/ *.egg-info

# Install build tools
pip install build twine

# Build the package
python -m build

# Check the package
twine check dist/*

echo ""
echo "Package built successfully."
echo "To upload to PyPI, run:"
echo "  twine upload dist/*"
echo ""
echo "To upload to TestPyPI first:"
echo "  twine upload --repository testpypi dist/*"
