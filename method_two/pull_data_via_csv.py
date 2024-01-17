import json

import loguru
import requests
from requests import HTTPError, Response
from selenium.webdriver.chrome.service import Service
from seleniumwire import webdriver
from webdriver_manager.chrome import ChromeDriverManager

from helpers.utility import construct_json, make_data_request

MAIN_URL = "https://sports.bwin.com/"

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
}

options = webdriver.ChromeOptions()
options.add_argument("--headless")

svc = Service(ChromeDriverManager().install())
driver = webdriver.Chrome(service=svc, options=options)

driver.get(MAIN_URL)

result: Response | None = None
api_url: str | None = None

for req in driver.requests:
    if req.response:
        links = req.url

    if "clientconfig" in links:
        client_url = f"{links}/partial?configNames=msConnection"
        try:
            result = requests.get(client_url, headers=HEADERS)
        except HTTPError as err:
            loguru.logger.error(
                f"Unable to make successful request, please try again later."
            )
        finally:
            break

if result:
    json_data = result.json()
    if "msConnection" in json_data:
        ms_connection_data = json_data["msConnection"]

        # Access specific values under 'msConnection'
        push_access_id = ms_connection_data.get("pushAccessId")
        public_access_id = ms_connection_data.get("publicAccessId")
        cds_url_base = ms_connection_data.get("cdsUrlBase")

        # Construct the URL to make the request to using the values above
        api_url = f"{cds_url_base}/bettingoffer/counts-fixtures?x-bwin-accessid={public_access_id}&lang=en&country=GB&userCountry=GB"

    response = make_data_request(api_url, HEADERS)
    response = response.json()

    for res in response["fixtures"]["fixtures"]:
        for x in res["games"]:
            final_json = construct_json(res, x["results"])
            load_to_csv = json.dumps(final_json)
            with open("output.json", "a") as f:
                f.write(load_to_csv + "\n")
