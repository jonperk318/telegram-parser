"""
TELEGRAM CHAT CC PARSER

OSINT tool by Jonathan Perkins
contact at jonperk318@gmail.com for questions/bugs

This script takes in JSON files exported from Telegram chat history and finds credit/debit card information 
in posts with keyword mentions. This is to be used to search dumps for sensitive data so the victims
can be made aware of the breach and the cards can be canceled. This is ONLY created to PREVENT 
further exploitation.

Accepted cc formats:
0000000000000000|MM|YY|000
0000000000000000|MM|YY|0000
0000000000000000|MM|YYYY|000
0000000000000000|MM|YYYY|0000
The | can also be a :
"""

import os
from pathlib import Path
import sys
import json
import csv
import re


path = input("Enter path of directory to recursively search for JSON files OR a specific file:\n")
path += "./"
output_path = path + "/parser_output/"
keyword = input("Enter search keyword (bank/institution name, etc.) (case insensitive):\n")
keyword = keyword.lower()


def process_message(message):

    if message["type"] != "message":
        return None
    
    message_id = str(message["id"])
    timestamp = message["date"].split("T")
    date = timestamp[0].replace("-", "/")
    time = timestamp[1]
    chat_name = message["from"]
    chat_id = message["from_id"].removeprefix('channel')
    content = message.get("text_entities", "")
    cc_regex = re.compile(r"(\d{16}(\||\:)\d{2}(\||\:)(\d{2}|\d{4})(\||\:)(\d{3}|\d{4}))")

    if isinstance(content, list):
        for text in content:
            if isinstance(text, dict):
                if keyword in text["text"].lower():
                    for i in content:
                        if isinstance(i, dict):
                            ccs = re.findall(cc_regex, i["text"])
                            for cc in ccs:
                                cc = re.split(r"[|:]+", cc[0])
                                cc_number = cc[0]
                                exp = (cc[1] + "/" + cc[2])
                                cvv = cc[3]
                                return {
                                        "from-channel-name": chat_name,
                                        "from-channel-id": chat_id,
                                        "message-id": message_id,
                                        "date": date,
                                        "time": time,
                                        "bin": cc_number[:6], 
                                        "cc-number": cc_number,
                                        "expiration": exp,
                                        "cvv": cvv,
                                        "link": ("https://t.me/c/" + chat_id + "/" + message_id)
                                        }
        
    return None


def file_writer(output_file):
    return csv.DictWriter(output_file, [
                                        "from-channel-name",
                                        "from-channel-id",
                                        "message-id",
                                        "date",
                                        "time",
                                        "bin",
                                        "cc-number",
                                        "expiration",
                                        "cvv",
                                        "link"
                                          ], dialect="unix", quoting=csv.QUOTE_NONNUMERIC)


if os.path.isdir(path): # DIRECTORY

    # Search recursively for all CSV files in directory
    files = []
    for subpath in Path(path).rglob('*.json'):
        files.append(subpath.name)

    if not os.path.exists(output_path):
        os.mkdir(output_path)

    with open(output_path + keyword + ".csv", "w", encoding="utf-8-sig", newline="") as output_file:

        writer = file_writer(output_file)
        writer.writeheader()

        for file in files:

            f = open((file), encoding="utf8")
            data = json.loads(f.read())
            f.close()

            for message in data["messages"]:
                row = process_message(message)
                if row is not None:
                    writer.writerow(row)

elif os.path.isfile(path): #FILE

    if not os.path.exists("./parser_output/"):
        os.mkdir("./parser_output/")

    f = open((path), encoding="utf8")
    data = json.loads(f.read())
    f.close()
    channel_id = str(data["id"])

    with open("./parser_output/" + keyword + " - " + channel_id + ".csv", "w", encoding="utf-8-sig", newline="") as output_file:

        writer = file_writer(output_file)
        writer.writeheader()

        for message in data["messages"]:
            row = process_message(message)
            if row is not None:
                writer.writerow(row)

else:
    sys.exit("Please enter a valid file path or directory")
    

print("Finished")