import calendar
import configparser
import datetime
import pickle
from os import path

import requests
from google.auth.transport.requests import Request
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build

SETTINGS_FILE_NAME = "config.ini"
SCOPES = ["https://www.googleapis.com/auth/calendar"]


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

    add_shifts_to_calendar(work_json, **config["google_calendar"])


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

    calendar_range = calendar_month_range(datetime.datetime.today())

    month_schedule = session.get(
        url + f"/rest/User/AssignmentsInfo/{calendar_range[0]}/{calendar_range[1]}")

    return month_schedule.json()


def calendar_month_range(date):
    """Given a Datetime.date object, returns a tuple containing the first
    monday and the last sunday of the given month, in format YYYY-MM-DD."""

    # Get day 1 from current month, then get monday of that week
    first_monday = date.replace(day=1).date()
    first_monday += datetime.timedelta(days=-first_monday.weekday())

    # Get last day from current month, then get sunday of that week
    last_sunday = date.replace(
        day=calendar.monthlen(date.year, date.month)).date()
    last_sunday += datetime.timedelta(days=6 - date.weekday())

    return first_monday.isoformat(), last_sunday.isoformat()


def add_shifts_to_calendar(work_json, json_path, calendar_id):
    """Shows basic usage of the Google Calendar API.
    Prints the start and name of the next 10 events on the user"s calendar.
    """
    creds = None
    # The file token.pickle stores the user's access and refresh tokens, and is
    # created automatically when the authorization flow completes for the first
    # time.
    if path.exists("token.pickle"):
        with open("token.pickle", "rb") as token:
            creds = pickle.load(token)
    # If there are no (valid) credentials available, let the user log in.
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(
                path.join(path.dirname(__file__), json_path), SCOPES)
            creds = flow.run_local_server(port=0)
        # Save the credentials for the next run
        with open("token.pickle", "wb") as token:
            pickle.dump(creds, token)

    service = build("calendar", "v3", credentials=creds)

    # Shifts where I've been included as a worker
    for shift in [day for day in work_json["assignments"] if day["presence"]["worked"]]:
        if not check_existing_event(calendar_id, service, shift["day"]):
            create_event(calendar_id, service, shift["day"], shift["presence"])


def check_existing_event(calendar, service, day):
    """Checks if there's already an event (or events) in any given day.
    Returns a list with all of the event ID's."""

    # Create a datetime object from the ISO 8601 string

    start = datetime.datetime(*[int(field) for field in day.split("-")],
                              0, 0, tzinfo=datetime.datetime.utcnow().astimezone().tzinfo)
    end = start + datetime.timedelta(days=1) - datetime.timedelta(seconds=1)

    query = service.events().list(calendarId=calendar, singleEvents=True,
                                  timeMin=start.isoformat(), timeMax=end.isoformat()).execute()

    return query.get("items", [])


def create_event(calendar, service, day, shift_info):
    """Adds an event to the configured calendar."""

    for frame in shift_info["timeFrames"]:

        start = datetime.datetime(*[int(field) for field in day.split("-")],
                                  int(frame["startMinuteDay"] / 60),
                                  frame["startMinuteDay"] % 60,
                                  tzinfo=datetime.datetime.utcnow().astimezone().tzinfo)
        end = start + datetime.timedelta(minutes=frame["duration"])

        payload = {
            "summary": "Work",
            "description": "Work shift generated automatically.",
            "start": {
                "dateTime": start.isoformat(),
            },
            "end": {
                "dateTime": end.isoformat(),
            }
        }

        service.events().insert(calendarId=calendar, body=payload).execute()
        print(f"Created calendar event between {start.isoformat()} and {end.isoformat()}")


if __name__ == "__main__":
    main()
