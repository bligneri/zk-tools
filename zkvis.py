import json
import argparse
from typing import List, Dict
from string import Template

FORCE_GRAPH_TEMPLATE_NAME = "force_graph.html"
OUTPUT_FILE_NAME = "output.html"

def generate_force_graph(id_files_dict: Dict, id_title_dict: Dict, links: List, highlight: List = None) -> None:
    if not highlight:
        highlight = []


    # Debugging logs for inputs
    print("Debug: Starting generate_force_graph")
    print(f"Debug: id_files_dict length: {len(id_files_dict)}")
    print(f"Debug: id_title_dict length: {len(id_title_dict)}")
    print(f"Debug: Highlighted IDs: {highlight}")

    # Create nodes
    nodes = []
    for uid, (title, path) in id_title_dict.items():
        group = 2 if uid in highlight else 1
        node_id = title if title else path
        nodes.append({"id": node_id, "group": group})
        print(f"Debug: Created node - ID: {node_id}, Group: {group}")

    link_list = []
    for uid, file in id_files_dict.items():
        file_links = file.get("links", [])
        for link in file_links:
            if "targetPath" in link:
                target_path = link["targetPath"]
                source_id = id_title_dict.get(uid, ("", uid))[1]
                target_id = id_title_dict.get(target_path, ("", target_path))[1]

                if source_id and target_id:
                    link_data = {"source": source_id, "target": target_id, "value": 2}
                    link_list.append(link_data)
                    print(f"Debug: Created link - Source: {source_id}, Target: {target_id}, Value: 2")
                else:
                    print(f"Warning: Missing source or target for link - Source: {uid}, Target Path: {target_path}")

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
            data = data["notes"]
    except (FileNotFoundError, json.JSONDecodeError, KeyError) as e:
        print(f"Error reading JSON file: {e}")
        exit(1)

    id_files_dict = {item["path"]: item for item in data}
    id_title_dict = {item["path"]: (item["title"] if item["title"] else item["filename"], item["path"]) for item in data}

    highlight = args.highlight if args.highlight else []

    generate_force_graph(id_files_dict, id_title_dict, [], highlight)

