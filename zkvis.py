import json
import argparse
from typing import List, Dict
from string import Template

FORCE_GRAPH_TEMPLATE_NAME = "force_graph.html"
OUTPUT_FILE_NAME = "output.html"

def generate_force_graph(id_files_dict: Dict, id_title_dict: Dict, links: List[Dict], highlight: List = None) -> None:
    if not highlight:
        highlight = []

    # Create nodes
    nodes = [
        {"id": title, "group": 2 if uid in highlight else 1}
        for uid, title in id_title_dict.items()
    ]

    # Create a mapping of filenames or unique identifiers to node IDs
    # filename_to_id = {value: key for key, value in id_title_dict.items()}


  # Create a mapping of filenames or unique identifiers to node titles
    title_to_id = {value: key for key, value in id_title_dict.items()}


    # Transform links to use node titles instead of sourcePath/targetPath
    transformed_links = []
    for link in links:
        source_title = id_title_dict.get(link["sourcePath"].split("/")[-1].replace(".md", "").strip(), None)
        target_title = id_title_dict.get(link["targetPath"].split("/")[-1].replace(".md", "").strip(), None)
        if source_title and target_title:
            transformed_links.append({
                "source": source_title,
                "target": target_title,
                "value": 1  # Assign a default value or modify as needed
            })

    # Create Output and open it
    data = json.dumps({"nodes": nodes, "links": transformed_links})
    with open(FORCE_GRAPH_TEMPLATE_NAME, "r") as f:
        template = f.read()
        s = Template(template)
        with open(OUTPUT_FILE_NAME, "w") as out:
            out.write(s.substitute(data=data))

    print(f"Generated graph saved to {OUTPUT_FILE_NAME}")

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("json_file", help="Path to the input JSON file")
    parser.add_argument("--highlight", nargs='*', help="Highlight zettel ID")
    args = parser.parse_args()

    json_file_path = args.json_file
    try:
        with open(json_file_path, "r") as f:
            data = json.load(f)  # Correctly load the JSON data
            notes = data["notes"]  # Access the "notes" key
            links = data["links"]  # Access the "links" key
    except (FileNotFoundError, json.JSONDecodeError, KeyError) as e:
        print(f"Error reading JSON file: {e}")
        exit(1)

    # Parse data from JSON
    id_files_dict = {item["filenameStem"]: item for item in notes}
    id_title_dict = {
        item["filenameStem"]: item["title"] if item["title"].strip() else item["filename"]
        for item in notes
    }

    highlight = args.highlight if args.highlight else []

    generate_force_graph(id_files_dict, id_title_dict, links, highlight=highlight)
