import configparser
from os import path

SETTINGS_FILE_NAME = "config.ini"

def main():
    configuration = configparser.ConfigParser()

    try:
        config_path = path.join(path.dirname(__file__), SETTINGS_FILE_NAME)
        configuration.read_file(open(config_path))
    except FileNotFoundError:
        print("The settings file wasn't found. Aborting...")
        return

    print(configuration.sections())

if __name__ == "__main__":
    main()

