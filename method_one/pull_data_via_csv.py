import json

from helpers import construct_json, make_data_request

URL = "https://sports.bwin.com/cds-api/bettingoffer/counts-fixtures?x-bwin-accessid=NTZiMjk3OGMtNjU5Mi00NjA5LWI2MWItZmU4MDRhN2QxZmEz&lang=en&country=GB&userCountry=GB"

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
}

response = make_data_request(URL, HEADERS)
response = response.json()

for res in response["fixtures"]["fixtures"]:
    for x in res["games"]:
        final_json = construct_json(res, x["results"])
        load_to_csv = json.dumps(final_json)
        with open("output.json", "a") as f:
            f.write(load_to_csv + "\n")
