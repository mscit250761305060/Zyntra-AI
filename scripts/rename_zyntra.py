import os
from pathlib import Path

def replace_in_files(directory, search, replace):
    for root, dirs, files in os.walk(directory):
        if '.venv' in dirs:
            dirs.remove('.venv')
        if '.git' in dirs:
            dirs.remove('.git')
        for file in files:
            if file.endswith('.py'):
                path = Path(root) / file
                try:
                    content = path.read_text(encoding='utf-8')
                    if search in content:
                        content = content.replace(search, replace)
                        path.write_text(content, encoding='utf-8')
                        print(f"Updated {path}")
                except Exception as e:
                    print(f"Error reading {path}: {e}")

replace_in_files('d:/chatbot/code', 'logging.getLogger("zyntra', 'logging.getLogger("zyntra')
replace_in_files('d:/chatbot/code', 'zyntra_agent', 'zyntra_agent')
replace_in_files('d:/chatbot/code', 'app_name="zyntra"', 'app_name="zyntra"')
