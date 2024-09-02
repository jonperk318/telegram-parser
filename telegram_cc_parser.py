"""
TELEGRAM CHAT CC PARSER

OSINT tool by Jonathan Perkins
contact at jonperk318@gmail.com for questions/bugs

This script takes in a JSON file exported from Telegram chat history and finds credit/debit card information 
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

import json
import csv
import re

file = input("Enter name of JSON file (excluding extension):\n")

f = open(("./" + file + ".json"), encoding="utf8")
data = json.loads(f.read())
f.close()

channel_id = str(data["id"])

keyword = input("Enter search keyword (bank/institution name, etc.) (case insensitive):\n")
keyword = keyword.lower()

def process_message(message):

    if message["type"] != "message":
        return None
    
    message_id = str(message["id"])
    timestamp = message["date"].split("T")
    date = timestamp[0].replace("-", "/")
    time = timestamp[1]
    from_chat = message["from"]
    from_id = message["from_id"]
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
                                        "from-channel-name": from_chat,
                                        "from-channel-id": from_id.removeprefix('channel'),
                                        "message-id": message_id,
                                        "date": date,
                                        "time": time,
                                        "bin": cc_number[:6], 
                                        "cc-number": cc_number,
                                        "expiration": exp,
                                        "cvv": cvv
                                        }
        
    return None


with open("./" + keyword + " - " + channel_id + ".csv", "w", encoding="utf-8-sig", newline="") as output_file:

    writer = csv.DictWriter(output_file, [
                                        "from-channel-name",
                                        "from-channel-id",
                                        "message-id",
                                        "date",
                                        "time",
                                        "bin",
                                        "cc-number",
                                        "expiration",
                                        "cvv"
                                          ], dialect="unix", quoting=csv.QUOTE_NONNUMERIC)
    writer.writeheader()

    for message in data["messages"]:
        row = process_message(message)
        if row is not None:
            writer.writerow(row)
    

print("Done")