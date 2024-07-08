import generate_readme_utils
import traceback

try:
    generate_readme_utils.generate_asset_readmes()
except Exception as e:
    traceback.print_exc()
    print("An error occurred while generating assets:", e)
    exit(2)