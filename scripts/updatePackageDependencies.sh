#!/bin/bash

echo "Installing json for file parsing"
npm install -g json
echo "Installed JSON successfully"

NEW_SCRIPTS='{
    "setup-hooks": "sh ./scripts/setup-hooks.sh",
    "test": "echo \"Error: no test specified\" && exit 1",
    "deploy": "echo not needed npm publish --access=public --registry=http://registry.npmjs.org",
    "validateSchema": "node test/manifestTester.js manifest.json manifest-schema.json",
    "validateSchemaLinks": "node test/manifestLinkTester.js manifest.json",
    "generateImageLinks": "node utils/generateImageLinks.js",
    "junit-merge": "npx junit-merge -d test/cypress/reports/junit -o test/cypress/reports/junit/junit-results.xml",
    "test:integration": "cypress run --config-file ./test/cypress.json --spec \"./test/cypress/integration/cypressTests.spec.js\"",
    "cypress:open": "cypress open --config-file ./test/cypress.json"
  }'

echo "Updating package.json to have correct scripts"
json -I -f package.json -e "this.scripts=$NEW_SCRIPTS"

NEW_REPOSITORY='{
    "type": "gitlab",
    "hostname": "gitlab.com",
    "path": "itentialopensource/pre-built-automations"
  }'
echo "Updating package.json to have correct repository config"
json -I -f package.json -e "this.repository=$NEW_REPOSITORY"

NEW_DEV_DEPENDENCIES='{
    "@itential-tools/iap-cypress-testing-library": "^4.1.0",
    "ajv": "6.10.0",
    "better-ajv-errors": "^0.6.1",
    "cypress": "^9.7.0",
    "cypress-failed-log": "^2.9.5",
    "cypress-mochawesome-reporter": "^3.2.0",
    "cypress-multi-reporters": "^1.6.1",
    "fs-extra": "^7.0.1",
    "junit-report-merger": "^4.0.0",
    "mocha": "^10.0.0",
    "mocha-junit-reporter": "^2.0.2",
    "r2": "^2.0.1"
  }'

echo "Updating package.json to have correct devDependencies"
json -I -f package.json -e "this.devDependencies=$NEW_DEV_DEPENDENCIES"

echo "Running npm install"
npm install