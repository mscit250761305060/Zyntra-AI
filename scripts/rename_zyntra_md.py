import os
from pathlib import Path

def replace_in_md(directory):
    for root, dirs, files in os.walk(directory):
        if '.venv' in dirs:
            dirs.remove('.venv')
        if '.git' in dirs:
            dirs.remove('.git')
        for file in files:
            if file.endswith('.md') or file.endswith('.txt'):
                path = Path(root) / file
                try:
                    content = path.read_text(encoding='utf-8')
                    modified = False
                    
                    if 'ADK Multi-Agent Chatbot' in content:
                        content = content.replace('ADK Multi-Agent Chatbot', 'Zyntra AI')
                        modified = True
                        
                    if 'ADK Nexus' in content:
                        content = content.replace('ADK Nexus', 'Zyntra AI')
                        modified = True
                        
                    if 'zyntra_agent' in content:
                        content = content.replace('zyntra_agent', 'zyntra_agent')
                        modified = True
                        
                    if modified:
                        path.write_text(content, encoding='utf-8')
                        print(f"Updated {path}")
                except Exception as e:
                    print(f"Error reading {path}: {e}")

replace_in_md('d:/chatbot/code')
