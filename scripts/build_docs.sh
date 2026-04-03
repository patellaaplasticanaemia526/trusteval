#!/bin/bash
# TrustEval — Enterprise LLM Evaluation Framework
# Author: Antrixsh Gupta | https://www.linkedin.com/in/antrixshgupta
# License: MIT

echo "Building TrustEval documentation..."

if ! command -v mkdocs &> /dev/null; then
    echo "Installing mkdocs..."
    pip install mkdocs mkdocs-material
fi

mkdocs build
echo "Documentation built successfully in site/"
