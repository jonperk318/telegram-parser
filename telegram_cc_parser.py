"""
TELEGRAM CHAT CC PARSER

OSINT tool by Jonathan Perkins
contact at jonperk318@gmail.com for questions/bugs

This script takes in JSON files exported from Telegram chat history and finds credit/debit card information 
in posts using keyword matches. This is to be used to search dumps for sensitive data so the victims
can be made aware of the breach and the cards can be canceled. This is ONLY created to PREVENT 
further exploitation.

Enter either a path to a single JSON file to parse OR a directory. If a file is input, the results will be 
output into a CSV file named using the chat ID. If a directory is input, the directory will be recursively 
searched for any JSON files and the results from all channels will be output into a single CSV. The results
will be output into a parser_output directory within the working directory.

Accepted cc formats:
0000000000000000|MM|YY|000
0000000000000000|MM|YY|0000
0000000000000000|MM|YYYY|000
0000000000000000|MM|YYYY|0000
0000000000000000|MM/YY|000
0000000000000000|MM/YY|0000
0000000000000000|MM/YYYY|000
0000000000000000|MM/YYYY|0000
The | can also be a :
"""

import os
from pathlib import Path
import sys
import json
import csv
import re
from typing import Dict, Optional

def process_message(message: Dict, writer) -> Optional[Dict]:

    if message["type"] != "message":
        return
    
    message_id = str(message["id"])
    timestamp = message["date"].split("T")
    date, time = timestamp[0].replace("-", "/"), timestamp[1]
    chat_name = message["from"]
    chat_id = message["from_id"].removeprefix('channel')
    content = message.get("text_entities", "")
    cc_regex = re.compile(r"(\d{16}(\||\:)\d{2}(\||\:|\/)(\d{2}|\d{4})(\||\:)(\d{3}|\d{4}))")

    if not isinstance(content, list):
        return

    for text in content:
        if not isinstance(text, dict) or keyword not in text["text"].lower():
            continue
            
        for item in content:
            if not isinstance(item, dict):
                continue
                
            ccs = re.findall(cc_regex, item["text"])
            for cc in ccs:
                cc_parts = re.split(r"[|:/]+", cc[0])
                writer.writerow({
                    "from-channel-name": chat_name,
                    "from-channel-id": chat_id,
                    "message-id": message_id,
                    "date": date,
                    "time": time,
                    "bin": cc_parts[0][:6],
                    "cc-number": cc_parts[0],
                    "expiration": f"{cc_parts[1]}/{cc_parts[2]}",
                    "cvv": cc_parts[3],
                    "link": f"https://t.me/c/{chat_id}/{message_id}"
                })
    
    return

def get_csv_writer(output_file):
    fieldnames = [
        "from-channel-name", "from-channel-id", "message-id", "date",
        "time", "bin", "cc-number", "expiration", "cvv", "link"
    ]
    return csv.DictWriter(
        output_file,
        fieldnames=fieldnames,
        dialect="unix",
        quoting=csv.QUOTE_NONNUMERIC
    )

def process_json_file(json_path: Path, writer):
    with open(json_path, encoding="utf8") as f:
        data = json.load(f)
    
    if writer is not None:
        for message in data["messages"]:
            process_message(message, writer)
    
    return data.get("id")

def setup_output_directory(base_path: Path) -> Path:
    output_path = base_path / "parser_output"
    output_path.mkdir(parents=True, exist_ok=True)
    return output_path

def check_path(path, keyword):

    output_path = setup_output_directory(path.parent if path.is_file() else path)

    if path.is_dir():
        output_file_path = output_path / f"{keyword}.csv"
        with open(output_file_path, "w", encoding="utf-8-sig", newline="") as output_file:
            writer = get_csv_writer(output_file)
            writer.writeheader()
            
            for json_file in path.rglob('*.json'):
                process_json_file(json_file, writer)
                
    elif path.is_file():
        channel_id = process_json_file(path, None)
        output_file_path = output_path / f"{keyword} - {channel_id}.csv"
        
        with open(output_file_path, "w", encoding="utf-8-sig", newline="") as output_file:
            writer = get_csv_writer(output_file)
            writer.writeheader()
            process_json_file(path, writer)
            
    else:
        sys.exit("Please enter a valid file path or directory")

def main():

    path = Path(input("\nEnter path of directory to recursively search for JSON files OR a specific file:\n").strip('"'))
    if not path:
        path = Path("./")
    
    global keyword
    keyword = input("Enter case insensitive keyword OR a TXT file containing one keyword per line:\n").lower()

    if Path(keyword).is_file():
        with open(Path(keyword), "r") as keywords:
            for k in keywords:
                keyword = k.strip("\n")
                check_path(path, keyword)
    else:
        check_path(path, keyword)
    
    
    print("Finished\n")

if __name__ == "__main__":
    main()