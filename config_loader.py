import json
import os

def load_config():
    """
    Loads and returns the JSON configuration file as a Python dictionary.

    The config file is expected to be named 'config.json' and located in the
    same directory as this script. Uses UTF-8 encoding to support special characters.
    """
    # Build the full path to 'config.json' relative to the current file's location
    config_path = os.path.join(os.path.dirname(__file__), 'config.json')

    # Open the config file and load its contents into a Python dictionary
    with open(config_path, 'r', encoding='utf-8') as file:
        config = json.load(file)

    return config

config = load_config()

base_dir = os.path.dirname(os.path.abspath(__file__))

db_path = os.path.join(base_dir, config["paths"]["db_path"])
log_path = os.path.join(base_dir, config["paths"]["log_path"])
backup_folder = os.path.join(base_dir, config["paths"]["backup_folder"])

# Load configuration settings (keywords for tagging and favorites)
article_feeds = config["feeds"]
tag_keywords = config["tag_keywords"]
favorite_keywords = [kw.lower() for kw in config["favorite_keywords"]]
update_interval_minutes = config["scheduler"]["interval_minutes"]
custom_english_stopwords = config["custom_english_stopwords"]
custom_finnish_stopwords = config["custom_finnish_stopwords"]

