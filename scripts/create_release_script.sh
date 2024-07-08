#!/bin/bash
#---------------------#
# Create release note #
#---------------------#

NEW_VERSION=$1
IS_MARKDOWN_GENERATION=$2

create_release_note() {
    # Create a changelog file if there isn't one
    if [ ! -e CHANGELOG.md ]; then
        touch CHANGELOG.md
    fi
    echo "Creating release note..."

    #----------------#
    # Changelog Body #
    #----------------#
    # Get the merge request info
    # See https://git-scm.com/docs/git-log for documentation on formatting git log
    CHANGELOG_BODY="$(git log --merges -1 --format=%b%n%n%ci%n)"
    if [ -z "$CHANGELOG_BODY" ]; then
        CHANGELOG_BODY="$(git log -1 --format='Bug fixes and performance improvements'%n%n'See commit '%h%n%n%ci%n)"
    fi

    if [ "$IS_MARKDOWN_GENERATION" == "true" ]; then
        CHANGELOG_BODY="$(git log -1 --format='Regenerate documentation and metadata.json files'%n%n'See commit '%h%n%n%ci%n)"
    fi

    #--------------------#
    # Write Release Note #
    #--------------------#

    # get the current date
    DATE=$(date +%m-%d-%Y)
    # create the release note
    RELEASE_NOTE="
## $NEW_VERSION [$DATE]

$CHANGELOG_BODY

---
"

    # append Release Note to Top of CHANGELOG
    if ! echo "$RELEASE_NOTE$(cat CHANGELOG.md)\n" > CHANGELOG.md; then
        echo -e "\\033[0;31mERROR: ***********************************************************************************"
        echo "ERROR: Unable to append release note information to changelog."
        echo -e "ERROR: ***********************************************************************************\\033[0m"
    else
        echo "Created release note:"
        echo "$RELEASE_NOTE"
    fi
}

create_release_note "$NEW_VERSION"
