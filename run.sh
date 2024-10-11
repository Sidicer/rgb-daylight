#!/usr/bin/bash

_script_dir=$( cd -- "$( dirname -- "${BASH_SOURCE[0]}" )" &> /dev/null && pwd )

# Check if python & pip is installed
hash python 2>/dev/null || exit 1
hash python3 2>/dev/null || exit 1

if [ ! -e "${_script_dir}/pyvenv.cfg" ]; then
    echo "[Error] Python virtual environment not found... Run ./prepare.sh"
    exit 1
fi

echo "Activating python virtual environment."
source ${_script_dir}/bin/activate

${_script_dir}/bin/python3 ${_script_dir}/src/rgb-daylight.py