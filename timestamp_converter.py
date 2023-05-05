__author__ = "Maxwell Twente"
__copyright__ = ""
__credits__ = ["Maxwell Twente, "]
__license__ = ""
__version__ = ""
__maintainer__ = "Maxwell Twente"
__email__ = "mtwente@colsa.com"
__status__ = "development"
#UNCLASSIFIED
#file@timestamp_converter.py
#############################################################
# purpose: converts timestamp field in json files to ISO 8601 format
#
#
#
##############################################################

import os
import json
from dateutil import parser
from datetime import datetime

def convert_time(timestamp):
    # Convert timestamp to datetime object
    dt = parser.parse(timestamp)

    # Convert datetime object to ISO 8601 format
    return dt.isoformat()

def format_json_time(json_obj):
    # Check if input is a dictionary
    if isinstance(json_obj, dict):
        for key, value in json_obj.items():
            # If the key is 'timestamp', reformat the time value
            if key == 'timestamp':
                json_obj[key] = convert_time(value)
            # If the value is another dictionary, recursively call format_json_time
            elif isinstance(value, dict):
                format_json_time(value)
            # If the value is a list, loop through the list and recursively call format_json_time
            elif isinstance(value, list):
                for item in value:
                    format_json_time(item)

    # Check if input is a list
    elif isinstance(json_obj, list):
        for item in json_obj:
            # Recursively call format_json_time on each item in the list
            format_json_time(item)

    # Return the modified JSON object
    return json_obj

# Get the input directory path from the user
dir_path = input("Enter the path to the input directory: ")

# Loop through all files in the directory
for file_name in os.listdir(dir_path):
    # Check if file is a JSON file
    if file_name.endswith('.json'):
        # Construct the input file path
        file_path = os.path.join(dir_path, file_name)

        # Load the input JSON file
        with open(file_path, 'r') as f:
            json_data = json.load(f)

        # Reformat timestamps in JSON data
        json_data = format_json_time(json_data)

        # Create a subdirectory called 'modified' if it doesn't exist
        if not os.path.exists(os.path.join(dir_path, 'modified')):
            os.mkdir(os.path.join(dir_path, 'modified'))

        # Construct the output file path
        output_path = os.path.join(dir_path, 'modified', file_name)

        # Write modified JSON data to the output file
        with open(output_path, 'w') as f:
            json.dump(json_data, f)

        print(f"Modified file saved to {output_path}")

print("All JSON files in directory converted successfully.")
#UNCLASSIFIED