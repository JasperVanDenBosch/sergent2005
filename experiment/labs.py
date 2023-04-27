"""Read the lab-specific configuration from file

"""
from __future__ import annotations
from typing import Dict, Any
from vendor.tomli import load


def getLabConfiguration() -> Dict[str, Any]:
    with open('lab.toml', 'rb') as fhandle:
        config = load(fhandle)
    return config
