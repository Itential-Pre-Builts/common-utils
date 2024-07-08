const iapCypressLibrary = require('@itential-tools/iap-cypress-testing-library');

module.exports = (on, config) => {
  return new Promise((resolve) => {
    // eslint-disable-next-line no-shadow
    iapCypressLibrary(config).then((config) => {
      return resolve(config);
    });
  });
};


