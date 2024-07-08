const path = require('path'),
      fs = require('fs-extra');

const args = process.argv.filter((element, index) => {
  return index >=2;
});
if (args.length <= 0) {
  const usage = `
  ==============================================================
    Simplified manifest schema validator, using ajv,
    that can be used for very quick schema validations.
    This will validate a json file against the schema
    found in manifest-schema.json

    Usage: node manifestTester.js someManifestFile.json

    NOTE: for a graphical JSON schema validator go to
    https://www.jsonschemavalidator.net/

  ==============================================================`;
  console.log(usage);
  process.exit(1);
}

async function runLinkValidation() {
  const filePath = path.normalize(args[0]);

  console.log(`Retrieving ${filePath}`);
  // Read in manifest.json file for IAP components in this Pre-Built
  const manifest = await fs.readFile(filePath, 'utf8');
  console.log('Converting to JSON object');
  const manifestData = JSON.parse(manifest);

  console.log('Iterating through artifacts...');
  // Initialize valid flag to true
  let valid=true;
  for (let i=0; i< manifestData.artifacts.length; i++){
    const current = manifestData.artifacts[i].location;
    if (current){
      if (fs.existsSync(`./${current}`)){
        // Read in IAP component as found in bundles folder or repository
        const bundle = await fs.readFile(`./${current}`, 'utf8');
        const bundleData = JSON.parse(bundle);
        if (manifestData.artifacts[i].type == 'transformation') {
          if (manifestData.artifacts[i].id == bundleData._id) {
            console.log(`\t✅  Validating ${current}`);
          } else {
            console.log(`\t❌  Validating ${current}`);
            console.log(`\t\t- Bundle ID (${bundleData._id}) is not equal to manifest artifact ID (${manifestData.artifacts[i].id}).`);
            valid = false;
          }
        } else if (manifestData.artifacts[i].type == 'golden-config') {
          if (manifestData.artifacts[i].name == bundleData.data[0].name) {
            console.log(`\t✅  Validating ${current}`);
          } else {
            console.log(`\t❌  Validating ${current}`);
            console.log(`\t\t- Bundle Name (${bundleData.data[0].name}) is not equal to manifest artifact ID (${manifestData.artifacts[i].id}).`);
            valid = false;
          }
        } else if (manifestData.artifacts[i].id == bundleData.name) {
          console.log(`\t✅  Validating ${current}`);
        } else {
          console.log(`\t❌  Validating ${current}`);
          console.log(`\t\t- Bundle Name (${bundleData.name}) is not equal to manifest artifact ID (${manifestData.artifacts[i].id}).`);
          valid = false;
        }
      }
      else{
        console.log(`\t❌  Validating ${current}`);
        console.log(`\t\t- File at path '${current}' does not exist.`);
        valid = false;
      }
    }
  }
  if (!valid) {
    // If not valid, force pipeline to error
    console.error('Validation Failed  👎');
    process.exit(1);
  }
  else {
    console.log('Validation passed  👍');
  }
}
try {
  runLinkValidation();
}
catch(error) {
  console.error(`Error occurred running the validator ${error}`);
}

