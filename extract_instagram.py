
import json
import re

file_path = r'C:\Users\DARIO LUBISCO\.gemini\antigravity\brain\6fcf570c-595b-4990-a03b-84aa2c95bc17\.system_generated\logs\overview.txt'

with open(file_path, 'r', encoding='utf-8') as f:
    for line in f:
        if 'instagram' in line.lower():
            try:
                data = json.loads(line)
                content = data.get('content', '')
                if 'instagram' in content.lower():
                    print(f"--- Found in Step {data.get('step_index')} ---")
                    # Print the block around Instagram
                    parts = content.split('\n')
                    for i, p in enumerate(parts):
                        if 'instagram' in p.lower():
                            # Print a few lines before and after
                            start = max(0, i-2)
                            end = min(len(parts), i+10)
                            print('\n'.join(parts[start:end]))
                            print("-" * 20)
            except Exception as e:
                pass
