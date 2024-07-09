import generate_readme_utils
import traceback

try:
    generate_readme_utils.generate_metadata()
    print("Generated metadata successfully")
except Exception as e:
    traceback.print_exc()
    print("An error occurred while generating metadata:", e)
    exit(2)