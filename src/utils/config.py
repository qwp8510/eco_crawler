from . import get_json_content


class Config():
    """ Global config class"""

    _instance = None
    _config_dir = None
    config = {}

    def __init__(self):
        if self._config_dir:
            self.config = get_json_content(self._config_dir)

    @classmethod
    def instance(cls):
        """ Get singleton instance"""
        if not cls._instance:
            cls._instance = cls()
        return cls._instance

    @classmethod
    def set_dir(cls, config_dir):
        """ Set config path
        Args:
            config_dir(str): config path

        """
        cls._config_dir = config_dir

    def get(self, key, fallback=None):
        """ Get config value by key
        Args:
            key(str): dict key name
            fallback: fall back value if key does not exist

        Returns:
            dict value

        """
        return self.config.get(key, fallback)
