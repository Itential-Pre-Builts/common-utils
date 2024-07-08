const fs = require("fs").promises;

(async () => {
  const filename = "CONFIG.json";

  const artifactJSON = await fs.readFile('./artifact.json');
  artifact = JSON.parse(artifactJSON);
  tempArray = [];

  //loops through dependencies found within the artifact.json
  Object.keys(artifact.metadata.IAPDependencies).forEach(function(key, index) {
    obj = {};
    if (typeof(artifact.metadata.IAPDependencies[key]) == 'object') {
      Object.keys(artifact.metadata.IAPDependencies[key]).forEach(function(key,value) {
        tempArray.push(key);
      });
    } else {
      tempArray.push(key);
    }
  });

  //loops through adapter names and grabs properties from masterList
  for (const adapt of tempArray) {
    const masterList = await fs.readFile("masterAdapterConfigs.json");
    masterListJSON = JSON.parse(masterList);
    adapter = masterListJSON[adapt];
    if (adapter != null) {
      console.log("Configuring Adapter: " + adapter.id);
      const file = await fs.readFile(filename);
      config = JSON.parse(file);
      config.adapterProps.adapters.push(adapter);
      await fs.writeFile(filename, JSON.stringify(config, null, 4));
    }
  }
})();