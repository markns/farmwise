#!/bin/bash

# Base directory
BASE_DIR="apps/farmbase/src/farmbase/static/farmbase/src/farmer"

# 1. Rename files and directories that contain 'Farmer' in the name
find "$BASE_DIR" -depth -name '*Farmer*' | while read filepath; do
  newpath=$(echo "$filepath" | sed 's/Farmer/Contact/g')
  mv "$filepath" "$newpath"
done
