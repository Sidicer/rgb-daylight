#!/usr/bin/bash

_script_dir=$( cd -- "$( dirname -- "${BASH_SOURCE[0]}" )" &> /dev/null && pwd )

# Check if python & pip is installed
hash python 2>/dev/null || exit 1
hash python3 2>/dev/null || exit 1

echo "Creating python virtual environment."
python3 -m venv ${_script_dir}/

echo "Activating python virtual environment."
source ${_script_dir}/bin/activate

echo "Installing required python dependencies."
pip install -r ${_script_dir}/requirements.txt
