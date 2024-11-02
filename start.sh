#!/bin/bash

REPO_URL="https://github.com/danielamadori98/PACO.git"
APP_PATH="src/app.py"

if [ ! -d ".git" ]; then
    echo "Cloning the repository..."
    git clone --branch "$(git ls-remote --tags --refs --sort="v:refname" "$REPO_URL" | tail -n1 | sed 's|.*/||')" "$REPO_URL" .
else
    echo "Checking for the latest release..."
    LATEST_TAG=$(git ls-remote --tags --refs --sort="v:refname" "$REPO_URL" | tail -n1 | sed 's|.*/||')

    # Check if the latest tag differs from the current one
    CURRENT_TAG=$(git describe --tags --abbrev=0)
    if [ "$LATEST_TAG" != "$CURRENT_TAG" ]; then
        echo "New release found: $LATEST_TAG. Updating..."
        git fetch --tags
        git checkout "$LATEST_TAG"
    else
        echo "Already on the latest release: $CURRENT_TAG."
    fi
fi

# Execute the application
python3 "$APP_PATH"
