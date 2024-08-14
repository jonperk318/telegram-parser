# Telegram Chat CC Parser

This script takes in a JSON file exported from Telegram chat history and finds credit/debit card information 
in posts with keyword mentions. This is to be used to search dumps for sensitive data so the victims
can be made aware of the breach and the cards can be canceled. This is ONLY created to PREVENT 
further exploitation.

Accepted cc formats:\
0000000000000000|MM|YY|000\
0000000000000000|MM|YY|0000\
0000000000000000|MM|YYYY|000\
0000000000000000|MM|YYYY|0000

## How to use

This script is written Python 3.12.0.

1. Find a Telegram channel with credit/debit card dumps in a format shown above.
2. Export chat history as a JSON (machine readable) format by navigating to the top right menu of the Telegram desktop app. Deselect all boxes and change `html` to `json`.

![demo.png](demo.png)

3. Download `telegram-cc-parser.py` and place the script in the same directory as the `result.json` file from the Telegram chat export.
4. Run the following command from terminal:

```python
python3 telegram_cc_parser.py result [keyword]
```
5. After a short time, the results will be exported to a `csv` file with the following format:

- `from-channel-name`: channel name post originated from
- `from-channel-id`: channel ID
- `message-id`: unique message ID (to find exact message by appending to Telegram chat URL)
- `date`: MM/DD/YYYY
- `time`: 00:00:00
- `bin`: first 6 digits of card number
- `cc-number`: card number
- `expiration`: expiration date
- `cvv`: pin

## Notes

Please use responsibly! This is an open-source intelligence (OSINT) tool, and as any of these tools, it should be used to counteract criminal activity and protect victim data.

I originally created this for a more narrow use case and didn't intend to share it, but I realized its potential to help a researcher/analyst that stumbles accross it. If you have any suggestions on further features, or if you encounter bugs, please open an issue. Also feel free to contact me directly!
