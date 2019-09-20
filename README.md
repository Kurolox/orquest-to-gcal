# Orquest to GCal

## Description

This is a small script that fetches my work shifts from Orquest, an employee management software used at work, to my Google Calendar account.

## Usage

The script should be straightforward to use. All that you need to do is to create a `config.ini` file in the folder where the script is located, similar to the example one [(`config.ini.example`)](src/config.ini.example)

```ini
[orquest]
url = the endpoint URL that was provided by orquest
username = Your orquest username
password = Your orquest password

[google_calendar]
```