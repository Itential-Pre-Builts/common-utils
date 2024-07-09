import traceback
import generate_readme_utils

try:
    generate_readme_utils.generate_readme()
    print("Generated README successfully")
except Exception as e:
    traceback.print_exc()
    print("An error occurred while generating readme:", e)
    exit(2)
