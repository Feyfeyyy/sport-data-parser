# Sport-Data-Parser


## Description

This is a simple python script to parse data from the [Sport Data API](https://sportdataapi.com/).

---

## How to use

1. Clone the repository
2. Choose whether you want method you like to execute the scripts.
2. Run the ```pull_data_via_csv.py``` file or the ```pull_data_via_database.py``` file
4. Enjoy!

## Additional Information

The ```pull_data_via_csv.py``` file will pull data from the API and store it in a CSV file in the same directory as the script.

The ```pull_data_via_database.py``` file will pull data from the API and store it in a SQLite database in the same directory as the script.

## Prerequisites

Before you begin, ensure you have met the following requirements:

- [Python](https://www.python.org/downloads/) (3.9+)
- [requests](https://pypi.org/project/requests/) (2.26+)
- [loguru](https://pypi.org/project/loguru/) (0.5+) (optional)

## Dependency Management

This project uses [Poetry](https://python-poetry.org/) for dependency management.

## Formatting

This project uses Black & isort for formatting.

---