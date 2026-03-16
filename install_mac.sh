#!/bin/bash
cd "$(dirname "$0")"

echo "============================================================"
echo "  Zoho Create Invoice Automation by leonnel18"
echo "  Setup Wizard"
echo "============================================================"
echo ""

# Check Python 3 is available
if ! command -v python3 &>/dev/null; then
    echo "[ERROR] Python 3 is not installed."
    echo ""
    echo "Please install Python 3 from https://www.python.org/downloads/"
    echo "Or via Homebrew:  brew install python"
    exit 1
fi

echo "Python 3 found. Launching setup wizard..."
echo ""
python3 setup_wizard.py
