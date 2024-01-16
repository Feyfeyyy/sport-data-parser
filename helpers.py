import datetime
from typing import Dict

import loguru
import requests
from requests import HTTPError, Response


def make_data_request(url: str, headers: Dict, data: Dict) -> Response:
    """
    Make a request to the given URL with the given headers and data.

    :param url: URL to make the request to
    :param headers: Headers to use for the request
    :param data: Data to send with the request
    :raises SystemExit: If the request was not successful
    :return: Response object
    """

    try:
        result = requests.post(url, headers=headers, json=data)
        result.raise_for_status()
        return result
    except HTTPError as err:
        loguru.logger.error(
            f"Unable to make successful request, please try again later."
        )
        raise SystemExit(err)


def construct_json(data: Dict, odds: Dict) -> Dict:
    """
    Construct a custom JSON from a response call.

    :param data: Data to construct the JSON from
    :param odds: Odds to construct the JSON from
    :return: Custom JSON format
    """
    return {
        "tournament_name": data["competition"]["name"]["value"],
        "last_updated": datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "events": [
            {
                "event_name": data["name"]["value"],
                "start_time": datetime.datetime.strptime(
                    data["startDate"], "%Y-%m-%dT%H:%M:%SZ"
                ).strftime("%Y-%m-%d %H:%M:%S"),
                "outcomes": [
                    {
                        "outcome_name": data["participants"][0]["name"]["value"],
                        "odds": odds[0]["odds"],
                    },
                    {
                        "outcome_name": data["participants"][1]["name"]["value"],
                        "odds": odds[1]["odds"],
                    },
                ],
            }
        ],
    }
