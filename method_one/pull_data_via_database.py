import sqlite3

import loguru

from method_one.helpers.utility import construct_json, make_data_request

URL = "https://sports.bwin.com/cds-api/bettingoffer/counts-fixtures?x-bwin-accessid=NTZiMjk3OGMtNjU5Mi00NjA5LWI2MWItZmU4MDRhN2QxZmEz&lang=en&country=GB&userCountry=GB"

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
}

response = make_data_request(URL, HEADERS)
response = response.json()

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
