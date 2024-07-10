#!/bin/bash

# Read in input parameter to denote which artifact files to move for commit
WORKFLOW_TYPE=$1

# Set-Up git config
echo "Started setting git config"
git config --global user.email "github-action@users.noreply.github.com"
git config --global user.name "$GITHUB_ACTOR"

# Move all readme_metadata_artifacts into expected location
echo "Started move of readme_metadata_artifacts files"
cp readme_metadata_artifacts/README.md .
cp -r readme_metadata_artifacts/documentation .
cp readme_metadata_artifacts/metadata.json .
cp readme_metadata_artifacts/TAB1.md .
cp readme_metadata_artifacts/TAB2.md .

if [ "$WORKFLOW_TYPE" = "release_branch_primary" ]; then
  # Move all version bump and generate artifacts into expected location
  echo "Started move of version_bump_artifacts files"
  cp version_bump_artifacts/artifact.json .
  cp version_bump_artifacts/CHANGELOG.md .
  cp version_bump_artifacts/package.json .
  cp version_bump_artifacts/package-lock.json .
fi

if [ "$WORKFLOW_TYPE" = "release_branch_secondary" ]; then
  # Move all generate artifacts into expected location
  echo "Started move of generate_artifacts files"
  cp generate_artifacts/artifact.json .
fi

# Conditionally removes the old manifest files
echo "Started update of manifest files"
if [ -f test/manifest-schema.json ]; then
  rm -f test/manifest-schema.json
  git add test/manifest-schema.json
fi

if [ -f test/manifestTester.js ]; then
  rm -f test/manifestTester.js
  git add test/manifestTester.js
fi

if [ -f test/manifestLinkTester.js ]; then
  rm -f test/manifestLinkTester.js
  git add test/manifestLinkTester.js
fi

# Add all files to be commited
echo "Started git add of all files"
git add test/cypress/integration
git add test/cypress/plugins/index.js
git add test/cypress/support
git add test/cypress.json
git add package.json
git add package-lock.json
git add artifact.json
git add CHANGELOG.md
git add README.md
if [ -e "documentation/documentation_mapping.json" ]; then
  git add documentation
  git add metadata.json
  git add TAB1.md
  git add TAB2.md
else
  echo "Skipping git add of documentation"
fi

# commit files
echo "Started commit of all files"
git commit -m "Updating package, artifact, and cypress [skip ci]"
NEW_VERSION=$(node -p "require('./artifact.json').metadata.version")
git tag -a v"$NEW_VERSION" -m "Bumping versions for package and artifact"

# Push files and tag using access token
echo "Started push of all files"
git remote set-url origin https://x-access-token:"$GITHUB_TOKEN"@github.com/"$GITHUB_REPOSITORY"
if git push -f --follow-tags --no-verify; then
  echo "Push files successfully"
else
  echo "Failed to push files to remote"
  exit 1
fi

# If the repository is public and GitHub is primary, do npm publish of Pre-Built
if [ "$WORKFLOW_TYPE" = "release_branch_primary" ]; then
  echo "Running NPM publish"
  # if npm publish --registry=https://registry.npmjs.org --access=public; then
  #   echo "Project published to npmjs.com successfully."
  # else
  #   echo "Project failed to publish to npmjs.com."
  #   exit 1
  # fi
else
  echo "Skipping NPM publish step as GitHub is secondary to GitLab"
fi