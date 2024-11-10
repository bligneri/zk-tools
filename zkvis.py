import json
import argparse
from typing import List, Dict
from string import Template

FORCE_GRAPH_TEMPLATE_NAME = "force_graph.html"
OUTPUT_FILE_NAME = "output.html"

def generate_force_graph(id_files_dict: Dict, id_title_dict: Dict, links: List, highlight: List = None) -> None:
    if not highlight:
        highlight = []

    nodes = [
        {"id": title if title else path, "group": 2 if uid in highlight else 1}
        for uid, (title, path) in id_title_dict.items()
    ]

    # Create links with consistent source and target IDs
    link_list = []
    path_to_title = {path: title for path, (title, _) in id_title_dict.items()}

    for link in links:
        source_path = link["sourcePath"]
        target_path = link["targetPath"]

        source_id = path_to_title.get(source_path, source_path)  # Use title if available, otherwise path
        target_id = path_to_title.get(target_path, target_path)  # Use title if available, otherwise path

        if source_id and target_id:
            print(f"Debug: Creating link from {source_id} to {target_id}")  # Debugging line
            link_list.append({"source": source_id, "target": target_id, "value": 2})
        else:
            print(f"Warning: Missing source or target ID for link from {source_path} to {target_path}")

    # Create Output and open it
    data = json.dumps({"nodes": nodes, "links": link_list})
    with open(FORCE_GRAPH_TEMPLATE_NAME, "r") as f:
        template = f.read()
        s = Template(template)
        with open(OUTPUT_FILE_NAME, "w") as out:
            out.write(s.substitute(data=data))

    print("Generated data:", data)
    print(f"Generated graph saved to {OUTPUT_FILE_NAME}")

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("json_file", help="Path to the input JSON file")
    parser.add_argument("--highlight", nargs='*', help="Highlight zettel ID")
    args = parser.parse_args()

    json_file_path = args.json_file
    try:
        with open(json_file_path, "r") as f:
            data = json.load(f)
            links = data.get("links", [])  # Extract links from the data if present
            if not links:
                print("Warning: No links found in the input data.")
            data = data["notes"]
    except (FileNotFoundError, json.JSONDecodeError, KeyError) as e:
        print(f"Error reading JSON file: {e}")
        exit(1)

    # Debugging: Print links to ensure they are loaded correctly
    print(f"Debug: Loaded {len(links)} links")
    for link in links:
        print(f"Debug: Link details - {link}")

    id_files_dict = {item["path"]: item for item in data}
    id_title_dict = {item["path"]: (item["title"] if item["title"] else item["filename"], item["path"]) for item in data}

    highlight = args.highlight if args.highlight else []

    # Call the function and pass the data
    generate_force_graph(id_files_dict, id_title_dict, links, highlight)

