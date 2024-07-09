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

#-----------------------------------------------------#
# Get Current Version and strip off IAP major version #
#-----------------------------------------------------#
CURRENT_VERSION=$(node -p "require('./package.json').version")
echo "Current Version: $CURRENT_VERSION"

INTERMEDIATE_VERSION=${CURRENT_VERSION%-*}
echo "Intermediate Version: $INTERMEDIATE_VERSION"

INTERMEDIATE_RELEASE=$(echo $CURRENT_VERSION | awk -F '-' '{print $2}')
INTERMEDIATE_RELEASE=${INTERMEDIATE_RELEASE:-""}
echo "Intermediate Release: $INTERMEDIATE_RELEASE"

# Set package version to just X.Y.Z without 20XX.Y.Z
npm install -g json
json -I -f package.json -e "this.version='$INTERMEDIATE_VERSION'"

#---------------------------#
# Version & Release Package #
#---------------------------#

# bump package version using semver
# using -f to ignore the added release note
npm --no-git-tag-version version -f "$SEMVER" -m "Updating $SEMVER version to %s." --loglevel=error
echo "Version bump successful"

NEW_VERSION=$(node -p "require('./package.json').version")
echo "New version: $NEW_VERSION"

# append release to end of version if branch or merge branch is release
if [[ -z "${CI_MERGE_REQUEST_SOURCE_BRANCH_NAME}" ]]; then
  echo "Commit reference name: ${CI_COMMIT_BRANCH}"
  CI_BRANCH_SOURCE=${CI_COMMIT_BRANCH}
else
  echo "Merge request source branch name:${CI_MERGE_REQUEST_SOURCE_BRANCH_NAME}"
  CI_BRANCH_SOURCE=${CI_MERGE_REQUEST_SOURCE_BRANCH_NAME}
fi

echo "Intermediate Release: $INTERMEDIATE_RELEASE"

# Checks if branch version is in version X.Y.Z
if [[ $INTERMEDIATE_RELEASE =~ ^[0-9]*\.[0-9]*\.[0-9]*$ ]]; then
  #  Version is in X.Y.Z, so increment Z plus 1
  read -r major minor patch <<< "${INTERMEDIATE_RELEASE//./ }"

  patch=$(expr $patch + 1)
  END_OF_BRANCH="$major.$minor.$patch"
  echo "Incremented release version: $END_OF_BRANCH"
  NEW_VERSION_FOR_TAG="${NEW_VERSION}-${END_OF_BRANCH}"
else
  #  Version is in X.Y, so append .0 to the end: X.Y.0
  END_OF_BRANCH=${CI_BRANCH_SOURCE#*/}
  NEW_VERSION_FOR_TAG="${NEW_VERSION}-${END_OF_BRANCH}.0"
  echo "Created new release branch at version ${END_OF_BRANCH}.0"
fi


echo "New version: $NEW_VERSION_FOR_TAG"

# Set package version to X.Y.Z with 20AA.B.C, so X.Y.Z-20AA.B.C
json -I -f package.json -e "this.version='$NEW_VERSION_FOR_TAG'"
npm ci

# create release note before versioning the project
wget https://raw.githubusercontent.com/Itential-Pre-Builts/common-utils/main/scripts/create_release_script.sh
bash ./create_release_script.sh "$NEW_VERSION_FOR_TAG" "$IS_MARKDOWN_GENERATION"

