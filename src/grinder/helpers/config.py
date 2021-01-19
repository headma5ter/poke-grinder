import configparser
import pathlib
import os

PARENT_DIR = pathlib.Path(__file__).parents[1].resolve()
CONFIG_PATH = os.environ.get("CONFIG_PATH", PARENT_DIR / "config.ini")


class ConfigStorage:
    def __init__(self):
        self._config_path: pathlib.Path = self._pathify(CONFIG_PATH, required=True)
        self._config: configparser.ConfigParser = self._open_config()

        # path settings
        self._cache_dir: pathlib.Path = self._pathify(
            self._read_config_entry("paths", "cache_dir")
        )
        self._moves_file: pathlib.Path = self._cache_dir / self._read_config_entry(
            "paths", "moves_file"
        )
        self._pokemon_file: pathlib.Path = self._cache_dir / self._read_config_entry(
            "paths", "pokemon_file"
        )
        self._routes_file: pathlib.Path = self._cache_dir / self._read_config_entry(
            "paths", "routes_file"
        )

        # general information
        self._cache_data: bool = self._boolify(
            self._read_config_entry("general", "cache_data")
        )
        self._overwrite_data: bool = self._boolify(
            self._read_config_entry("general", "overwrite_data")
        )
        self._game: str = self._read_config_entry(
            "general",
            "game",
            value_options=("Ultra Moon", "Ultra Sun"),  # TODO: expand value options
        )
        self._pokemon: str = self._read_config_entry("general", "pokemon")
        self._last_badge: str = self._read_config_entry("general", "last_badge")

    @property
    def moves_file(self) -> pathlib.Path:
        return self._moves_file

    @property
    def pokemon_file(self) -> pathlib.Path:
        return self._pokemon_file

    @property
    def routes_file(self) -> pathlib.Path:
        return self._routes_file

    @property
    def cache_data(self) -> bool:
        return self._cache_data

    @property
    def overwrite_data(self) -> bool:
        return self._overwrite_data

    @property
    def generation(self) -> str:
        return self._generation

    @property
    def pokemon(self) -> str:
        return self._pokemon

    @property
    def last_badge(self) -> str:
        return self._last_badge

    def _read_config_entry(
        self, section: str, key: str, required: bool = True, value_options: tuple = ()
    ) -> str:
        """
        Read entry from config file.
        """
        if not required and (
            section not in self._config or key not in self._config[section]
        ):
            return ""

        try:
            value = self._config[section][key]
        except KeyError as e:
            msg = f"A required config section/key not found ({e})"
            # self._logger.error(msg, extra={"stage": "config"})
            raise ValueError(msg)

        if value_options and value not in value_options:
            msg = f"The config value ({value}) must be one of the following: {value_options}"
            # self._logger.error(msg, extra={"stage": "config"})
            raise ValueError(msg)

        return value

    @staticmethod
    def _pathify(path: str, required: bool = True,) -> pathlib.Path:
        """
        Convert string to pathlib.Path
        """
        path = pathlib.Path(path)
        if not path.is_absolute():
            path = pathlib.Path(__file__).parents[1] / path

        if required and not path.is_file() and not path.is_dir():
            msg = f"Required file not found ('{path}')"
            # self._logger.error(msg)
            raise FileNotFoundError(msg)

        return path.resolve()

    @staticmethod
    def _boolify(string_to_bool: str) -> bool:
        """
        Convert string to bool
        """
        return string_to_bool.lower() in ("t", "true", "y", "yes")

    def _open_config(self) -> configparser.ConfigParser:
        """
        Open config object
        """
        config = configparser.ConfigParser()
        config.read(self._config_path)
        return config
