#!/usr/bin/env python3

from zOS import zOS

zSpark = {
    "zEnv": "Production",
    "zLog": "PROD",
    "zMode": "zCLI",  # Use zCLI mode for testing
    "zPersist": True,
    "zVaFolder": "@",
    "zVaFile": "zUI.lists",
    "zBlock": "Lists_block",
}
# Initialize zOS and run init sequence
z = zOS(zSpark)
z.run()
