#!/bin/bash
set -euo pipefail
IFS=$'\n\t'


bl_info="$(head -n 10 BlenderLxrToolsAddon/__init__.py)"
version="$(python/bin/python3 -c "${bl_info}; print('.'.join(map(str, bl_info['version'])))")"

zip "BlenderLxrToolsAddon-${version}.zip" BlenderLxrToolsAddon/*.py