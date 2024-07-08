import { PrebuiltRunner } from '@itential-tools/iap-cypress-testing-library/testRunner/testRunners';

describe('Default: Cypress Tests', function () {
  let prebuiltRunner;
  before(function () {
    //creates a prebuiltRunner for importing the Project
    cy.fixture(`../../../artifact.json`).then((data) => {
      prebuiltRunner = new PrebuiltRunner(data);
    });
  });

  describe('Default: Imports Project', function () {
    // eslint-disable-next-line mocha/no-hooks-for-single-case
    it('Default: Should import the Project into IAP', function () {
        prebuiltRunner.deletePrebuilt.single({ failOnStatusCode: false });
        prebuiltRunner.importPrebuilt.single({});
    });
  });
});