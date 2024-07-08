const fs = require('fs');
const Ajv = require('ajv');

/**
 * @summary Gets file paths of documentation files in project
 *
 * @returns  {Object} List of file paths for asset documentation and readme.json file
 */
function getDocumentationFilePaths() {
  documentationMappingFile = JSON.parse(fs.readFileSync('./documentation/documentation_mapping.json'));
  const assetFilePaths = [];
  for (let asset of documentationMappingFile.assets) {
    if (!asset.path.includes(asset.name)) {
      throw new Error(`Asset name ${asset.name} not found in file path to asset documentation ${asset.path}`);
    }
    assetFilePaths.push(`.${asset.path}`);
  }
  const readmeFilePath = `.${documentationMappingFile.readme}`;
  const documentationFilePaths = {
    assetFilePaths,
    readmeFilePath
  }
  return documentationFilePaths;
}

/**
 * @summary Performs schema validation for all asset and readme documentation files
 *
 */
function validateDocumentationFiles() {
  const assetDocumentationSchema = JSON.parse(fs.readFileSync('./readmeUtils/assetDocumentationSchema.json'));
  const readmeDocumentationSchema = JSON.parse(fs.readFileSync('./readmeUtils/readmeDocumentationSchema.json'));
  const documentationFilePaths = getDocumentationFilePaths();
  const assetFilePaths = documentationFilePaths.assetFilePaths;
  const readmeFilePath = documentationFilePaths.readmeFilePath;
  const validationResults = [];
  let validationFailureFound = false;
  for (let assetFilePath of assetFilePaths) {
    let assetValidationResult = {
      "file": assetFilePath
    }
    assetDocumentationJSON = JSON.parse(fs.readFileSync(assetFilePath));
    assetValidationResult.validationResult = validateJSON(assetDocumentationJSON, assetDocumentationSchema, assetFilePath)
    if (assetValidationResult.validationResult != "success") {
      validationFailureFound = true;
    }
    validationResults.push(assetValidationResult);
  }
  readmeDocumentationJSON = JSON.parse(fs.readFileSync(readmeFilePath));
  let readmeValidationResult = {
    "file": readmeFilePath
  }
  readmeValidationResult.validationResult = validateJSON(readmeDocumentationJSON, readmeDocumentationSchema, readmeFilePath);
  if (readmeValidationResult.validationResult != "success") {
    validationFailureFound = true;
  }
  validationResults.push(readmeValidationResult);
  if (validationFailureFound == true) {
    console.log("One or more invalid documentation files were encountered. See error message output above to resolve issue in file noted.")
    process.exit(1);
  }
  return validationResults;
}


/**
 * @summary Takes in a JSON object representing documentation data and 
 * JSON schema and attempts to validate the object against the schema. 
 * Throws an error and returns false if failure. Returns true if success.
 *
 * @function validateJSON
 * @param {Object} jsonToValidate - the documentation object
 * @param {Object} jsonSchema - the json schema to compare to
 * @param {String} jsonFilePath - file path to the json object to validate
 *
 * @return {String} "success" if validation passed or an error message if validation
 * failed
 */
function validateJSON(jsonToValidate, jsonSchema, jsonFilePath) {
  let ajvInstance = new Ajv({allErrors: true, verbose: true});
  // validate the entity against the schema
  const validator = ajvInstance.compile(jsonSchema);
  const result = validator(jsonToValidate);
  // if invalid properties throw an error
  if (!result) {
    let resultMessage = `File "${jsonFilePath}" failed schema validation`
    for (let i = 0; i < validator.errors.length; i++) {
      const error = validator.errors[i];
      resultMessage += `
    Error ${i+1}
        message: ${error.message}
        data path: ${error.dataPath}
        schema path: ${error.schemaPath}`
    }
    console.log(resultMessage);
    return resultMessage;
  } else {
    let resultMessage = 'success';
    console.log(`File "${jsonFilePath}" passed schema validation`)
    return resultMessage
  }
}

validateDocumentationFiles();

module.exports = validateDocumentationFiles;