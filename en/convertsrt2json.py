import json
import re

def srt_time_to_seconds(time_str):
    """Converts HH:MM:SS,ms to total seconds (float)"""
    hours, minutes, seconds = time_str.split(':')
    seconds, milliseconds = seconds.split(',')
    total = int(hours) * 3600 + int(minutes) * 60 + int(seconds) + int(milliseconds) / 1000
    return round(total, 3)

def convert_srt_to_json(input_file, output_file):
    with open(input_file, 'r', encoding='utf-8') as f:
        content = f.read()

    # Regex to find: ID, Timestamp Range, and the Text lines
    pattern = re.compile(r'(\d+)\n(\d{2}:\d{2}:\d{2},\d{3}) --> (\d{2}:\d{2}:\d{2},\d{3})\n(.*?)(?=\n\n|\n$|$)', re.DOTALL)
    
    matches = pattern.findall(content)
    
    json_data = []
    
    for match in matches:
        line_id = match[0]
        start_time = srt_time_to_seconds(match[1])
        end_time = srt_time_to_seconds(match[2])
        # Clean up text (remove newlines if the subtitle has 2 lines)
        text = match[3].replace('\n', ' ').strip()
        
        json_data.append({
            "id": int(line_id),
            "start": start_time,
            "end": end_time,
            "text": text,
            "emoji": "💬"  # Placeholder for your Semantic Emoji idea!
        })

    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(json_data, f, ensure_ascii=False, indent=4)
    
    print(f"Success! {len(json_data)} lines converted to {output_file}")

# Usage
convert_srt_to_json('Pewdipie-90-Day-Fiance.srt', 'Pewdipie-90-Day-Fiance_en.json')