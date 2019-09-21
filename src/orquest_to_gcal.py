import configparser
import datetime
import calendar
from os import path
import requests

SETTINGS_FILE_NAME = "config.ini"


def main():
    config = configparser.ConfigParser()

    try:
        # Get absolute path to script, append settings file to path
        config_path = path.join(path.dirname(__file__), SETTINGS_FILE_NAME)
        config.read_file(open(config_path))
    except FileNotFoundError:
        print("The settings file wasn't found. Aborting...")
        return

    try:
        work_json = get_orquest_data(**config["orquest"])
    except KeyError:  # [orquest] section is missing from the config file
        print(
            "The settings file is missing the [orquest] section. Aborting...")
        return

    # TODO: Use Google Calendar API to add work shifts to calendar


def get_orquest_data(url, username, password):
    """Given the orquest endpoint URL, an username and a password, retrieve
    all work shifts from the given account in JSON format."""

    session = requests.Session()
    login_payload = {
        "j_username":   username,
        "j_password":   password,
        "remember-me": 	None,
        "submit":       "Login"}
    session.post(url + "/authentication", data=login_payload)

    current_date = datetime.datetime.today()

    date = calendar_month_range(current_date)

    month_schedule = session.get(
        url + f"/rest/User/AssignmentsInfo/{date[0]}/{date[1]}")
    return month_schedule.json()


def calendar_month_range(date):
    """Given a Datetime.date object, returns a tuple containing the first
    monday and the last sunday of the given month, in format YYYY-MM-DD."""

    # TODO: Properly calculate first monday and last sunday.
    # Last sunday has to be the sunday of the last week of the month, while
    # first monday has be the monday of the first week of the month.
    first_monday = min(week[-1]
                       for week in calendar.monthcalendar(date.year, date.month))
    last_sunday = max(week[-1]
                      for week in calendar.monthcalendar(date.year, date.month))

    monday_date = None
    sunday_date = date.replace(day=last_sunday).isoformat()

    return monday_date, sunday_date


if __name__ == "__main__":
    main()
