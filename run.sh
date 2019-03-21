#!/usr/bin/env bash

set -e  # Stop if any command fails

chmod +x Core/RadioT_RPi.py  # Change execution permissions for the file
Core/RadioTelescopeRPi.py  # Execute the main program file