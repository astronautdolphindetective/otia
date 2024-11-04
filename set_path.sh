#!/bin/bash

# Load the JSON file and extract the path value using `jq`
path=$(jq -r '.path' config.json)

# Find all Python files and update the `project_root` line
find . -name "*.py" | while read -r file; do
    # Use `sed` to replace the `project_root` line in each file
    sed -i "/#begin preprocessing/,/#end preprocessing/ s|project_root = .*|project_root = \"$path\"|" "$file"
done
