import sqlite3

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

# Create the database table
conn = sqlite3.connect("tennis_data.db")
cursor = conn.cursor()
cursor.execute(
    """
    CREATE TABLE IF NOT EXISTS tennis_data (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        tournament_name TEXT,
        last_updated TEXT,
        event_name TEXT,
        start_time TEXT,
        outcome_name1 TEXT,
        odds1 TEXT,
        outcome_name2 TEXT,
        odds2 TEXT
    )
"""
)
conn.commit()

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

    i = 0
    for res in response["fixtures"]["fixtures"]:
        for x in res["games"]:
            final_json = construct_json(res, x["results"])

            cursor.execute(
                """
                SELECT * FROM tennis_data WHERE event_name=?
            """,
                (final_json["events"][0]["event_name"],),
            )

            existing_record = cursor.fetchone()

            if existing_record:
                # Update the existing record
                i += 1
                cursor.execute(
                    """
                    UPDATE tennis_data
                    SET tournament_name=?, last_updated=?, start_time=?, outcome_name1=?, odds1=?, outcome_name2=?, odds2=?
                    WHERE event_name=?
                """,
                    (
                        final_json["tournament_name"],
                        final_json["last_updated"],
                        final_json["events"][0]["start_time"],
                        final_json["events"][0]["outcomes"][0]["outcome_name"],
                        final_json["events"][0]["outcomes"][0]["odds"],
                        final_json["events"][0]["outcomes"][1]["outcome_name"],
                        final_json["events"][0]["outcomes"][1]["odds"],
                        final_json["events"][0]["event_name"],
                    ),
                )
            else:
                # Insert a new record
                i += 1
                cursor.execute(
                    """
                    INSERT INTO tennis_data (tournament_name, last_updated, event_name, start_time, outcome_name1, odds1, outcome_name2, odds2)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                """,
                    (
                        final_json["tournament_name"],
                        final_json["last_updated"],
                        final_json["events"][0]["event_name"],
                        final_json["events"][0]["start_time"],
                        final_json["events"][0]["outcomes"][0]["outcome_name"],
                        final_json["events"][0]["outcomes"][0]["odds"],
                        final_json["events"][0]["outcomes"][1]["outcome_name"],
                        final_json["events"][0]["outcomes"][1]["odds"],
                    ),
                )
                conn.commit()
    if i > 0:
        loguru.logger.info(f"Amount of new records inserted/ updated: {i}")
    else:
        loguru.logger.info("No new records inserted")

    # Close the database connection
    conn.close()
