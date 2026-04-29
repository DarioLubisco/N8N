
import json

file_path = r'C:\Users\DARIO LUBISCO\.gemini\antigravity\brain\6fcf570c-595b-4990-a03b-84aa2c95bc17\.system_generated\logs\overview.txt'

with open(file_path, 'r', encoding='utf-8') as f:
    for line in f:
        try:
            data = json.loads(line)
            content = data.get('content', '')
            if 'instagram' in content.lower():
                print(f"--- Step {data.get('step_index')} ({data.get('source')}) ---")
                # Look for the section about Instagram
                idx = content.lower().find('instagram')
                start = max(0, idx - 200)
                end = min(len(content), idx + 1000)
                print(content[start:end])
                print("-" * 40)
        except:
            pass
