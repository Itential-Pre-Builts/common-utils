#!/bin/bash

# check node version:
echo "node version: $(node --version)"
echo "npm version: $(npm --version)"

# Add npm credentials to container's .npmrc
echo "Setting up npm credentials..."
wget https://raw.githubusercontent.com/Itential-Pre-Builts/common-utils/main/scripts/.npmrc
chmod +x .npmrc
echo "npm credentials configured."

echo "Installing dependencies..."
if [ ! -f package-lock.json ]; then
    echo "No package-lock.json... running npm install"
    npm install
    if [ ! -f package-lock.json ]; then
        echo "npm install failed"
        exit 1
    fi
else 
    echo "running npm ci"
    npm ci
    if [[ $? -ne 0 ]]; then
        echo "npm ci failed."
        exit 1
    fi
fi

echo "Dependencies installed."
