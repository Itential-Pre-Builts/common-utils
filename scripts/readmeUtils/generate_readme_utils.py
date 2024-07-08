from jinja2 import Environment, FileSystemLoader
from urllib.parse import quote
import json
import os
import glob

def get_documentation_mapping():
    """
    Helper function to assign to local variable documenation mappings.
    """
    documentation_mapping_file = './documentation/documentation_mapping.json'
    with open(documentation_mapping_file) as file:
        # Assign documentation mapping to local variable
        documentation_mapping = json.load(file)
        return documentation_mapping

def get_assets():
    """
    Returns an array of all data found in the assets
    """
    documentation_mapping = get_documentation_mapping()
    allFiles = []
    # Iterate across assets identified in documentation mapping
    for asset in documentation_mapping['assets']:
        # Read contents of asset readme file
        with open('.' + asset['path']) as asset_file:
            # Assign asset readme to local variable
            asset_data = json.load(asset_file)
            allFiles.append(asset_data)
    return allFiles

def get_example_data():
    """
    Returns the example object data found in the documentation_mapping
    """
    documentation_mapping = get_documentation_mapping()
    example = documentation_mapping['example']
    # Read contents of asset readme file
    if 'path' in example:
      with open('.' + example['path']) as example_file:
          # Assign example readme to local variable
          example_data = json.load(example_file)
          return example_data
    else:
      return {}

def get_readme_data():
    """
    Helper function to assign to local variable top level readme data.
    """
    documentation_mapping = get_documentation_mapping()
    readme_data_file = '.' + documentation_mapping['readme']
    with open(readme_data_file) as file:
        readme_data = json.load(file)
        return readme_data

def pretty_print_example_values(values):
    """
    Pretty format example input or output values of asset
    """
    updated_values = []
    for value in values:
        example_value = value.get('exampleValue', '')
        pretty_example_value = pretty_print_example_value(example_value)
        value['exampleValue'] = pretty_example_value
        updated_values.append(value)
    return updated_values

def pretty_print_example_value(example_value):
    """
    Pretty format an object or array value
    """
    if example_value != '' and (example_value[0] == '{' or example_value[0] == '['):
        pretty_example_value = json.loads(example_value)
        pretty_example_value = json.dumps(pretty_example_value, indent=2)
    else:
        pretty_example_value = example_value
    return pretty_example_value

def render_jinja_template(environment, jinja_template, template_data):
    """
    Helper function to render jinja template.
    """
    # Get Jinja2 template to render asset markdown READMEs
    environment = Environment(loader=FileSystemLoader(environment))
    template = environment.get_template(jinja_template)
    rendered_content = template.render(template_data)
    return rendered_content

def generate_asset_readmes():
    """
    Creates markdown readme files from asset documentation data.
    """
    environment = './readmeUtils'
    jinja_template = 'generate_asset_readmes.jinja2'
    readme_data = get_readme_data()
    documentation_mapping = get_documentation_mapping()
    # Iterate across assets identified in documenation mapping
    for asset in documentation_mapping['assets']:
        # Read contents of asset readme file
        with open('.' + asset['path']) as asset_file:
            # Assign asset readme to local variable
            asset_data = json.load(asset_file)
            asset_data['type'] = readme_data.get('type', '')
            asset_data['bundleType'] = readme_data.get('bundleType', 'pre-built')
            # Get Operations Manager Data if Project
            bundle_type = readme_data.get('bundleType', 'pre-built')
            asset_data['operationsManagerLink'] = ''
            if bundle_type == 'project':
              # Get data to construct hyperlink to asset readme generated
              github_branch = os.environ.get(
                  'GITHUB_REF_NAME', 'Could not locate branch')
              github_server_url = os.environ.get(
                  'GITHUB_SERVER_URL', 'Could not locate GitHub server URL')
              github_repository_path = os.environ.get(
                  'GITHUB_REPOSITORY', 'Could not locate GitHub repository path')
              encoded_project_file_name = None
              for file in glob.glob('./*.project.json'):
                encoded_project_file_name = quote(file[2:])
              asset_data['projectFileLink'] = '{}/{}/-/blob/{}/{}'.format(github_server_url, github_repository_path,
                github_branch, encoded_project_file_name)
              if asset_data['entryPoint']['type'] == 'Operations Manager Automation':
                # Build the url encoded link to the Operations Manager Automation 
                om_name = asset_data['entryPoint']['name']
                om_name_encoded = quote(om_name)
                asset_data['operationsManagerLink'] = '{}/{}/-/blob/{}/bundles/automations/{}.json'.format(github_server_url,
                  github_repository_path, github_branch, om_name_encoded)
            # Get only required adapters
            adapters = asset_data.get('adapters', [])
            required_adapters = []
            for adapter in adapters:
                if adapter['isDependency'] == True:
                    required_adapters.append(adapter)
            asset_data['adapters'] = required_adapters
            # Verify has necessary property to indicate asset readme
            if 'entryPoint' in asset_data:
                # Pretty format any input example values
                asset_inputs = asset_data.get('inputs', [])
                updated_asset_inputs = pretty_print_example_values(asset_inputs)
                asset_data['inputs'] = updated_asset_inputs
                if 'exampleInput' in asset_data:
                    asset_example_input = asset_data.get('exampleInput')
                    asset_example_input = pretty_print_example_value(asset_example_input)
                    asset_data['exampleInput'] = asset_example_input
                # Pretty format any output example values
                asset_outputs = asset_data.get('outputs', [])
                updated_asset_outputs = pretty_print_example_values(asset_outputs)
                asset_data['outputs'] = updated_asset_outputs
                if 'exampleOutput' in asset_data:
                    asset_inputs = asset_data.get('exampleOutput')
                    updated_asset_inputs = pretty_print_example_value(asset_inputs)
                    asset_data['exampleOutput'] = updated_asset_inputs
                # Render Jinja2 template for markdown file
                rendered_content = render_jinja_template(
                    environment, jinja_template, asset_data)
                # Assign path to markdown file
                asset_markdown_file = '.' + \
                    asset['path'].replace('.json', '.md')
                # Write content of markdown file
                with open(asset_markdown_file, mode='w', encoding='utf-8') as message:
                    message.write(rendered_content)

def normalize_related_project_adapter_integration(related_project_adapter_integration):
    """
    Orders properties of related project or adapter for deduplication
    """
    normalized_related_project_adapter_integration = {}
    normalized_related_project_adapter_integration['name'] = related_project_adapter_integration.get('name', '')
    normalized_related_project_adapter_integration['webName'] = related_project_adapter_integration.get('webName', '')
    normalized_related_project_adapter_integration['overview'] = related_project_adapter_integration.get('overview', '')
    normalized_related_project_adapter_integration['isDependency'] = related_project_adapter_integration.get('isDependency', False)
    normalized_related_project_adapter_integration['version'] = related_project_adapter_integration.get('version', '')
    normalized_related_project_adapter_integration['repoLink'] = related_project_adapter_integration.get('repoLink', '')
    normalized_related_project_adapter_integration['docLink'] = related_project_adapter_integration.get('docLink', '')
    normalized_related_project_adapter_integration['webLink'] = related_project_adapter_integration.get('webLink', '')
    return normalized_related_project_adapter_integration

def normalize_related_adapter(related_adapter):
    """
    Orders properties of related project or adapter for deduplication
    """
    normalized_related_adapter = {}
    normalized_related_adapter['name'] = related_adapter.get('name', '')
    normalized_related_adapter['webName'] = related_adapter.get('webName', '')
    normalized_related_adapter['overview'] = related_adapter.get('overview', '')
    normalized_related_adapter['isDependency'] = related_adapter.get('isDependency', False)
    normalized_related_adapter['version'] = related_adapter.get('version', '')
    normalized_related_adapter['repoLink'] = related_adapter.get('repoLink', '')
    normalized_related_adapter['docLink'] = related_adapter.get('docLink', '')
    normalized_related_adapter['webLink'] = related_adapter.get('webLink', '')
    normalized_related_adapter['configurationNotes'] = related_adapter.get('configurationNotes', '')
    return normalized_related_adapter

def normalize_ecosystem_application(ecosystem_application):
    """
    Orders properties of related ecosystem application for deduplication
    """
    normalized_ecosystem_application = {}
    normalized_ecosystem_application['name'] = ecosystem_application.get('name', '')
    normalized_ecosystem_application['webName'] = ecosystem_application.get('webName', '')
    normalized_ecosystem_application['overview'] = ecosystem_application.get('overview', '')
    normalized_ecosystem_application['isDependency'] = ecosystem_application.get('isDependency', False)
    normalized_ecosystem_application['version'] = ecosystem_application.get('version', '')
    normalized_ecosystem_application['storeLink'] = ecosystem_application.get('storeLink', '')
    normalized_ecosystem_application['docLink'] = ecosystem_application.get('docLink', '')
    normalized_ecosystem_application['webLink'] = ecosystem_application.get('webLink', '')
    return normalized_ecosystem_application

def normalize_api_link_item(api_link_item):
    normalized_api_link_item = {}
    normalized_api_link_item['title'] = api_link_item.get('title', '')
    normalized_api_link_item['link'] = api_link_item.get('link', '')
    normalized_api_link_item['public'] = api_link_item.get('public', True)
    return normalized_api_link_item

def normalize_external_dependency(external_dependency):
    """
    Orders properties of external dependency for deduplication
    """
    normalized_external_dependency = {}
    normalized_external_dependency['name'] = external_dependency.get('name', '')
    normalized_external_dependency['apiVersion'] = external_dependency.get('apiVersion', '')
    normalized_external_dependency['osVersion'] = external_dependency.get('osVersion', '')
    return normalized_external_dependency

def get_deduplicated_dependency_values(property_name, map, map_property=''):
    """
    Given a property, retrieves values from each found asset and
    returns list of values for each asset
    map is a boolean that will map return data to the map_property when true
    """
    documentation_mapping = get_documentation_mapping()
    asset_values = []
    for asset in documentation_mapping['assets']:
        # Read contents of asset readme file
        with open('.' + asset['path']) as asset_file:
            # Assign asset readme to local variable
            asset_data = json.load(asset_file)
            # Add each item stringified to the ongoing list
            if property_name in asset_data:
                if type(asset_data[property_name]) is list:
                    # Handle case where list of adapters
                    if property_name == 'adapters':
                       for adapter in asset_data[property_name]:
                            normalized_related_adapter = normalize_related_adapter(adapter)
                            asset_values.append(json.dumps(normalized_related_adapter))
                    elif property_name == 'transformationProjects' or property_name == 'workflowProjects' \
                    or property_name == 'exampleProjects' or property_name == 'integrations':
                        for project_adapter_integration in asset_data[property_name]:
                            normalized_related_project_adapter_integration = normalize_related_project_adapter_integration(project_adapter_integration)
                            asset_values.append(json.dumps(normalized_related_project_adapter_integration))
                    elif property_name == 'externalDependencyList':
                        for external_dependency in asset_data[property_name]:
                            normalized_external_dependency = normalize_external_dependency(external_dependency)
                            asset_values.append(json.dumps(normalized_external_dependency))
                    elif property_name == 'ecosystemApplications':
                        for ecosystem_application in asset_data[property_name]:
                            normalized_ecosystem_application = normalize_ecosystem_application(ecosystem_application)
                            asset_values.append(json.dumps(normalized_ecosystem_application))
                    elif property_name == 'apiLinks':
                        for api_link_item in asset_data[property_name]:
                            normalized_api_link_item = normalize_api_link_item(api_link_item)
                            asset_values.append(json.dumps(normalized_api_link_item))
                    else:
                        for item in asset_data[property_name]:
                            # Convert to string value found and add to list of asset values
                            asset_values.append(json.dumps(item))
                else:
                    asset_values.append(json.dumps(asset_data[property_name]))
    # Remove duplicate values found
    asset_values_stringified_duplicates_removed = [*set(asset_values)]
    # Convert stringified values back to objects and append to new list
    asset_values_duplicates_removed = []
    for asset in asset_values_stringified_duplicates_removed:
        asset_values_duplicates_removed.append(json.loads(asset))
    if map:
        deduplicated_map_values = []
        for item in asset_values_duplicates_removed:
            if map_property in item:
                deduplicated_map_values.append(item[map_property])
        deduplicated_map_values = [*set(deduplicated_map_values)]
        return deduplicated_map_values
    return asset_values_duplicates_removed

def generate_readme():
    """
    Creates top level readme file aggregating project overview 
    with hyperlinks to assets in project.
    """
    # Get data to construct hyperlink to asset readme generated
    github_branch = os.environ.get(
        'GITHUB_REF_NAME', 'Could not locate branch')
    github_server_url = os.environ.get(
        'GITHUB_SERVER_URL', 'Could not locate GitHub server URL')
    github_repository_path = os.environ.get(
        'GITHUB_REPOSITORY', 'Could not locate GitHub repository path')

    # Read in documentation mappings
    documentation_mapping = get_documentation_mapping()

    # Assign to local variable top level readme data
    readme_data = get_readme_data()
    readme_jinja_data = {}
    readme_jinja_data['projectREADME'] = readme_data
    readme_jinja_data['assetREADMEs'] = []
    readme_jinja_data['externalDependencyList'] = get_deduplicated_dependency_values("externalDependencyList", False)
    readme_jinja_data['adapters'] = get_deduplicated_dependency_values("adapters", False)
    readme_jinja_data['apiLinks'] = get_deduplicated_dependency_values("apiLinks", False)

    # Create asset jinja data
    for asset in documentation_mapping['assets']:
        with open('.' + asset['path']) as asset_file:
            # Assign asset readme to local variable
            asset_data = json.load(asset_file)
            # Create hyperlink to file
            asset_jinja_data = {}
            asset_jinja_data['name'] = asset['name']
            asset_jinja_data['overview'] = asset_data['overview']
            asset_md_path = asset['path'].replace('.json', '.md')
            asset_jinja_data['href'] = '{}/{}/-/blob/{}/{}'.format(github_server_url,
                github_repository_path, github_branch, asset_md_path)
            readme_jinja_data['assetREADMEs'].append(asset_jinja_data)

    # Render top level readme jinja template
    environment = './readmeUtils'
    jinja_template = 'generate_readme.jinja2'
    rendered_content = render_jinja_template(
        environment, jinja_template, readme_jinja_data)
    readme_file = './README.md'
    # Write content of markdown file
    with open(readme_file, mode='w', encoding='utf-8') as message:
        message.write(rendered_content)

def rename_property(metadata, property_name):
  """
  Converts all item for a given property in related items 
  from the string 'version' to the array 'versions'
  """
  index = 0
  for item in metadata['relatedItems'][property_name]:
    if 'version' in item:
      metadata['relatedItems'][property_name][index]['versions'] = [item['version']]
      metadata['relatedItems'][property_name][index].pop('version')
    else:
      metadata['relatedItems'][property_name][index]['versions'] = []
    index = index + 1
  return metadata

def generate_metadata():
  """
  Creates top level readme file aggregating project overview 
  with hyperlinks to assets in project.
  """
  metadata = {}
  readmeData = get_readme_data()
  assetData = get_assets()
  metadata['name'] = readmeData.get('name', '')
  metadata['webName'] = readmeData.get('webName', '')
  readmeSplit = None

  try:
    readmeSplit = os.environ.get('GITHUB_REPOSITORY').split('/')[1]('-')
  except:
    readmeSplit = 'Itential-IAP-Project'.split('-')
  metadata['type'] = readmeData.get('type', '')

  # If the readme data has vendor, product, or method defined, use
  # that value. Otherwise, attempt to infer vendor, product, and method
  # from name of GitHub repository
  try:
    if 'vendor' not in readmeData or readmeData['vendor'] == '':
      metadata['vendor'] = readmeSplit[0]
    else:
      metadata['vendor'] = readmeData['vendor']
  except:
    metadata['vendor'] = ''
  try:
    if 'product' not in readmeData or readmeData['product'] == '':
      metadata['product'] = readmeSplit[1]
    else:
      metadata['product'] = readmeData['product']
  except:
    metadata['product'] = ''
  try:
    if 'method' not in readmeData or readmeData['method'] == '':
      metadata['method'] = readmeSplit[2]
    else:
      metadata['method'] = readmeData['method']
  except:
    metadata['method'] = ''

  metadata['osVersions'] = get_deduplicated_dependency_values('externalDependencyList', True, 'osVersion')
  metadata['apiVersions'] = get_deduplicated_dependency_values('externalDependencyList', True, 'apiVersion')
  # Will need to revisit this logic and merge arrays of each asset. Look into adding elements of all arrays
  # to a set to remove duplicate elements
  metadata['iapVersions'] = get_deduplicated_dependency_values('iapVersions', False)
  metadata['domains'] = readmeData.get('domains', [])
  metadata['tags'] = readmeData.get('tags', [])
  metadata['useCases'] = readmeData.get('useCases', [])
  metadata['deprecated'] = readmeData['deprecated']
  metadata['brokerSince'] = ''
  metadata['documentation'] = {}
  metadata['documentation']['storeLink'] = readmeData.get('storeLink', '')

  if os.environ.get('GITHUB_SERVER_URL') and os.environ.get('GITHUB_REPOSITORY'):
    github_server_url = os.environ.get(
      'GITHUB_SERVER_URL', 'Could not locate GitHub server URL')
    github_repository_path = os.environ.get(
      'GITHUB_REPOSITORY', 'Could not locate GitHub repository path')
    metadata['documentation']['repoLink'] = '{}/{}'.format(github_server_url, github_repository_path)
  else:
    metadata['documentation']['repoLink'] = ''
  if os.environ.get('GITHUB_REPOSITORY'):
    npm_path = os.environ.get('GITHUB_REPOSITORY').split('/')[1]
    metadata['documentation']['npmLink'] = 'https://www.npmjs.com/package/@itentialopensource/' + npm_path
  else:
    metadata['documentation']['npmLink'] = ''

  metadata['documentation']['docLink'] = readmeData.get('docLink', '')
  metadata['documentation']['demoLinks'] = readmeData.get('demoLinks', [])
  metadata['documentation']['trainingLinks'] = readmeData.get('trainingLinks', [])
  metadata['documentation']['faqLink'] = readmeData.get('faqLink', '')
  metadata['documentation']['contributeLink'] = readmeData.get('contributeLink', '')
  metadata['documentation']['issueLink'] = readmeData.get('issueLink', '')
  metadata['documentation']['webLink'] = readmeData.get('webLink', '')
  metadata['documentation']['vendorLink'] = readmeData.get('vendorLink', '')
  metadata['documentation']['productLink'] = readmeData.get('productLink', '')
  metadata['documentation']['apiLinks'] = get_deduplicated_dependency_values('apiLinks', False)

  # Generate assets section
  metadata['assets'] = []

  for assetInstance in assetData:
    asset = {}
    asset['name'] = assetInstance['name']
    asset['webName'] = assetInstance.get('webName', '')
    asset['assetType'] = assetInstance.get('assetType', '')
    asset['overview'] = assetInstance.get('overview', '')
    asset['iapVersions'] = assetInstance.get('iapVersions', [])
    assetExampleInputsAndOutputs = assetInstance.get('exampleInputsAndOutputs', [{}])
    if len(assetExampleInputsAndOutputs) > 0:
      asset['exampleInput'] = assetExampleInputsAndOutputs[0].get('exampleInput', '')
      asset['exampleOutput'] = assetExampleInputsAndOutputs[0].get('exampleOutput', '')
    else: 
      asset['exampleInput'] = ''
      asset['exampleOutput'] = ''
    metadata['assets'].append(asset)

  # Generate relatedItems section
  metadata['relatedItems'] = {}

  # Generate adapters relatedItems section
  metadata['relatedItems']['adapters'] = get_deduplicated_dependency_values('adapters', False)
  metadata = rename_property(metadata, 'adapters')

  # Generate integrations relatedItems section
  metadata['relatedItems']['integrations'] = get_deduplicated_dependency_values('integrations', False)
  metadata = rename_property(metadata, 'integrations')

  # Generate ecosystemApplications relatedItems section
  metadata['relatedItems']['ecosystemApplications'] = get_deduplicated_dependency_values('ecosystemApplications', False)
  metadata = rename_property(metadata, 'ecosystemApplications')

  # Generate workflowProjects relatedItems section
  metadata['relatedItems']['workflowProjects'] = get_deduplicated_dependency_values('workflowProjects', False)
  metadata = rename_property(metadata, 'workflowProjects')

  # Generate transformationProjects relatedItems section
  metadata['relatedItems']['transformationProjects'] = get_deduplicated_dependency_values('transformationProjects', False)
  metadata = rename_property(metadata, 'transformationProjects')

  # Generate exampleProjects relatedItems section
  metadata['relatedItems']['exampleProjects'] = get_deduplicated_dependency_values('exampleProjects', False)
  metadata = rename_property(metadata, 'exampleProjects')

  with open('metadata.json', 'w') as f:
    json.dump(metadata, f, indent=2)
