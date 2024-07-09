#!/bin/bash

# running git config
echo "Started setting git config"
git config --global user.email "github-action@users.noreply.github.com"
git config --global user.name "$GITHUB_ACTOR"

# Move all readme_metadata_artifacts into expected location
echo "Started move of readme_metadata_artifacts files"
mv readme_metadata_artifacts/README.md .
mv readme_metadata_artifacts/documentation .
mv readme_metadata_artifacts/metadata.json .
mv readme_metadata_artifacts/TAB1.md .
mv readme_metadata_artifacts/TAB2.md .

# Move all version bump artifacts into expected location
echo "Started move of version_bump_artifacts files"
mv version_bump_artifacts/artifact.json .
mv version_bump_artifacts/CHANGELOG.md .
mv version_bump_artifacts/package.json .
mv version_bump_artifacts/package-lock.json .

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

# add all files to be commited
echo "Started git add of files files"
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

#  commit files
echo "Started commit of files"
git commit -m "Updating package, artifact, and cypress [skip ci]"
NEW_VERSION=$(node -p "require('./artifact.json').metadata.version")
git tag -a v"$NEW_VERSION" -m "Bumping versions for package and artifact"

#  push files and tag using access token
git remote set-url origin https://x-access-token:"$GITHUB_TOKEN"@github.com/"$GITHUB_REPOSITORY"
if git push -f HEAD:"$CI_COMMIT_BRANCH" --follow-tags --no-verify; then
  echo "Push files successfully"
else
  echo "Failed to push files to remote"
  exit 1
fi

# if [ "${CI_PROJECT_NAMESPACE}"	== "itentialopensource/pre-built-automations" ]; then
#   if npm publish --registry=https://registry.npmjs.org --access=public; then
#     echo "Project published to npmjs.com successfully."
#   else
#     echo "Project failed to publish to npmjs.com."
#     exit 1
#   fi
# else
#   echo "Skipping NPM publish step."
# fi