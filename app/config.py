import os
from pathlib import Path

import yaml


class Settings:
    def __init__(self):
        config_path = Path(os.getenv("CONFIG_PATH", "/app/config.yaml"))
        with open(config_path) as f:
            data = yaml.safe_load(f)

        self.auth_key: str = data["auth_key"]
        self.rf_server_url: str = data["rf_server_url"].rstrip("/")


settings = Settings()
