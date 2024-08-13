"""
TELEGRAM CHAT CC PARSER

OSINT tool by Jonathan Perkins
contact at jonperk318@gmail.com for questions/bugs

This script takes in a JSON file exported from Telegram chat history and finds credit/debit card information 
in posts with keyword mentions. This is to be used to search dumps for sensitive data so the victims
can be made aware of the breach and the cards can be canceled. This is ONLY created to PREVENT 
further exploitation.
"""


import json
import csv

file = input("Enter name of JSON file (excluding extension):\n")

f = open(("./" + file + ".json"), encoding="utf8")
data = json.loads(f.read())
f.close()

channel_id = str(data["id"])

keyword = input("Enter search keyword (bank/institution name, etc.) (case insensitive):\n")

def process_message(message):

    if message["type"] != "message":
        return None
    
    message_id = str(message["id"])
    timestamp = message["date"].replace("T", " ")
    from_chat = message["from"]
    from_id = message["from_id"]
    content = message.get("text", "")

    if isinstance(content, list):

        for text in content:
            if isinstance(text, dict):
                if keyword in text["text"].lower():
                    for i in content:
                        if isinstance(i, dict):
                            if i["type"] == "code":
                                ccs = i["text"]
                                ccs = ccs.split("\n")
                                for cc in ccs:
                                    cc = cc.split("|")
                                    cc_number = cc[0]
                                    exp = ("" + cc[1] + "/" + cc[2])
                                    cvv = cc[3]
                                    return {
                                            "from-channel-name": from_chat,
                                            "from-channel-id": from_id.removeprefix('channel'),
                                            "message-id": message_id,
                                            "timestamp": timestamp,
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
                                        "timestamp",
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