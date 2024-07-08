#!/bin/bash

IS_MARKDOWN_GENERATION=$1

#-------------------#
# Get Semver Prefix #
#-------------------#
VERSION="$(git log --format=%s --merges -1|awk -F"'" '{print $2}'|awk -F "/" '{print $1}')"
echo "$VERSION"
case "$VERSION" in
    # if PATCH transform to patch
    patch|minor|major) SEMVER="$(echo "$VERSION" | awk '{print tolower($0)}')";;
    *) SEMVER="patch";;
esac
if [ -z "$VERSION" ]; then
    echo "No branch prefix detected. Defaulting to patch."
fi

if [ "$IS_MARKDOWN_GENERATION" == "true" ]; then
    SEMVER="patch"
fi

echo "Semver bump: $SEMVER"

#---------------------#
# Get Current Version #
#---------------------#
CURRENT_VERSION=$(node -p "require('./package.json').version")
echo "Current Version: $CURRENT_VERSION"

#---------------------------#
# Version & Release Package #
#---------------------------#
# bump version
# using -f to ignore the added release note
npm --no-git-tag-version version -f "$SEMVER" -m "Updating $SEMVER version to %s." --loglevel=error
echo "Version bump successful"

NEW_VERSION=$(node -p "require('./package.json').version")
echo "New version: $NEW_VERSION"

# create release note before versioning the project
wget https://gitlab.com/itentialopensource/pre-built-automations/common-utils/-/raw/master/scripts/create_release_script.sh
chmod +x create_release_script.sh
sh ./create_release_script.sh "$NEW_VERSION" "$IS_MARKDOWN_GENERATION"

