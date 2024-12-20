"""
TELEGRAM CHAT CREDENTIAL PARSER

OSINT tool by Jonathan Perkins
contact at jonperk318@gmail.com for questions/bugs

This tool takes in TXT files downloaded from Telegram and parses out credentials using keyword matches. 
This is to be used to search dumps for sensitive data so the victims can be made aware of the breach 
and the credentials can be deactivated. This is ONLY created to PREVENT further exploitation.

Enter the path to a directory of TXT files downloaded from the target Telegram channel. The results will
be output into a CSV file titled "credentials."
"""

import os
from pathlib import Path
import sys
import csv

# Input path and keyword from user
path = Path(input("\nEnter path of directory to recursively search for TXT files:\n").strip('"'))
if not path:
    path = Path("./")
keyword = input("Enter search keyword (bank/institution name, etc.) (case insensitive):\n")
keyword = keyword.lower()

# Parse individual line (can create a single row in output CSV)
def process_line(line):

    if keyword in line.lower():

        line, url = if_line(line)

        if line == None:
            return None

        try: username = line[1]
        except: username = ""
        try: password = line[2]
        except: password = ""

        return {
            "URL": url,
            "Username": username,
            "Password": password
            }
        
    return None

def if_line(line): # all if-else statements to catch edge cases

    if "mercadoli" in line:
        return None, None
        
    if line[:4] == "HPID":
        return None, None
    
    if line[:4] == "http":
    
        line = line.replace(" ", ":").split(":")[1:]
        try: url = line[0].replace("//", "")
        except: url = ""
        return line, url

    if "|" in line:

        line = line.replace(" ", "|").split("|")
        try: url = line[0]
        except: url = ""
        return line, url

    else:

        line = line.replace(" ", ":").split(":")
        try: url = line[0]
        except: url = ""
        return line, url

# Create filewriter object for CSV
def file_writer(output_file):
    return csv.DictWriter(output_file, [
        "URL",
        "Username",
        "Password"
        ], dialect="unix", quoting=csv.QUOTE_NONNUMERIC)


if os.path.isdir(path): # DIRECTORY INPUT

    output_path = Path.joinpath(path, "parser_output")
    if not output_path.exists(): # Create output directory if it doesn't exist
        output_path.mkdir(parents=True, exist_ok=True)

    with open(str(output_path) + "/credentials.csv", 
              "w", encoding="utf-8-sig", newline="") as output_file:

        writer = file_writer(output_file)
        writer.writeheader()

        for file in Path(path).rglob('*.txt'): # Search recursively for all TXT files in directory

            with open(file, encoding="utf8") as data:

                for line in data: # Each line is checked

                    row = process_line(line.rstrip())
                    if row is not None:
                        writer.writerow(row)

else:
    sys.exit("Please enter a valid directory path")

print("Finished\n")