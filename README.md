# Orquest to GCal

## Description

This is a small script that fetches my work shifts from Orquest, an employee management software used at work, to my Google Calendar account.

## Installation

1. Clone this repository and cd into it
```bash
git clone https://github.com/Kurolox/orquest-to-gcal && cd orquest-to-gcal
```

2. Install any dependencies using the provided Pipfile
```bash
pipenv install
```

3. Run the script using the generated virtualenv
```bash
pipenv run python src/orquest_to_gcal.py
```

## Usage

The script should be straightforward to use. All that you need to do is to create a `config.ini` file in the folder where the script is located, similar to the example one [(`config.ini.example`)](src/config.ini.example)

```ini
[orquest]
url = the endpoint URL that was provided by orquest
username = Your orquest username
password = Your orquest password

[google_calendar]
```