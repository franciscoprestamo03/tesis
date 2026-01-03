
import json
import glob
import os

def flatten_json(y):
    out = {}

    def flatten(x, name=''):
        if type(x) is dict:
            for a in x:
                flatten(x[a], name + a + '.')
        elif type(x) is list:
            out[name[:-1]] = x
        else:
            out[name[:-1]] = x

    flatten(y)
    return out

def get_headers(schema_path):
    with open(schema_path, 'r') as f:
        schema = json.load(f)
    
    # We want to preserve the order and structure, but flatten it for columns
    # Using the recursive flatten function to get keys
    flat_schema = flatten_json(schema)
    return list(flat_schema.keys())

def extract_value(data, key_path):
    keys = key_path.split('.')
    val = data
    try:
        for key in keys:
            val = val[key]
        
        if isinstance(val, list):
            return ", ".join([str(v) for v in val])
        return str(val).replace('\n', ' ').replace('|', '\|') # Escape pipes for markdown
    except (KeyError, TypeError):
        return ""

def generate_table(schema_path, features_dir, output_file):
    headers = get_headers(schema_path)
    # Add 'Paper Name' as the first column (from filename)
    all_headers = ['Paper Name'] + headers
    
    rows = []
    
    files = glob.glob(os.path.join(features_dir, "*.json"))
    files.sort()
    
    for file_path in files:
        file_name = os.path.basename(file_path).replace('.json', '')
        with open(file_path, 'r') as f:
            try:
                data = json.load(f)
            except json.JSONDecodeError:
                print(f"Error decoding {file_path}")
                continue
                
        row = [file_name]
        for header in headers:
            row.append(extract_value(data, header))
        rows.append(row)
        
    # Generate Markdown
    with open(output_file, 'w') as f:
        # Header row
        f.write("| " + " | ".join(all_headers) + " |\n")
        # Separator row
        f.write("| " + " | ".join(['---'] * len(all_headers)) + " |\n")
        # Data rows
        for row in rows:
            f.write("| " + " | ".join(row) + " |\n")

    print(f"Table written to {output_file}")

if __name__ == "__main__":
    SCHEMA_PATH = "last_schema.json"
    FEATURES_DIR = "extracted-features-from-papers"
    OUTPUT_FILE = "state_of_the_art.md"
    
    generate_table(SCHEMA_PATH, FEATURES_DIR, OUTPUT_FILE)
