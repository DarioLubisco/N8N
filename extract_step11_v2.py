
import json

file_path = r'C:\Users\DARIO LUBISCO\.gemini\antigravity\brain\6fcf570c-595b-4990-a03b-84aa2c95bc17\.system_generated\logs\overview.txt'

with open(file_path, 'r', encoding='utf-8') as f:
    for line in f:
        try:
            data = json.loads(line)
            if data.get('step_index') == 11:
                content = data.get('content', '')
                # Find "3." which should be Instagram/Facebook
                idx = content.find('3.')
                if idx != -1:
                    print(content[idx:idx+1000])
                else:
                    # Search for "Instagram" specifically
                    idx = content.lower().find('instagram')
                    if idx != -1:
                        print(content[idx-100:idx+1000])
                    else:
                        print("No '3.' or 'Instagram' found in Step 11 content.")
        except Exception as e:
            pass
