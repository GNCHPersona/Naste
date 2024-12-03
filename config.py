from dataclasses import dataclass
from environs import Env


@dataclass
class DbConfig:
    """
    Database configuration class.
    This class holds the settings for the database, such as host, password, port, etc.

    Attributes
    ----------
    host : str
        The host where the database server is located.
    password : str
        The password used to authenticate with the database.
    user : str
        The username used to authenticate with the database.
    database : str
        The name of the database.
    port : int
        The port where the database server is listening.
    """

    host: str
    password: str
    user: str
    database: str
    port: int = 5432

    @staticmethod
    def from_env(env: Env):
        """
        Creates the DbConfig object from environment variables.
        """
        host = env.str("DB_HOST")
        password = env.str("DB_PASS")
        user = env.str("DB_USER")
        database = env.str("DB_NAME")
        port = env.int("DB_PORT", 5432)
        return DbConfig(
            host=host, password=password, user=user, database=database, port=port
        )

@dataclass
class ServerConfig:
    """
    Server configuration class.
    This class holds the settings for the database, such as host, port.

    Attributes
    ----------
    host : str
        The host where the server is located.
    port : int
        The port where the server is listening.
    """

    host: str
    port: int

    @staticmethod
    def from_env(env: Env):
        """
        Creates the ServerConfig object from environment variables.
        """
        host = env.str("SERVER_HOST")
        port = env.int("SERVER_PORT")
        return ServerConfig(
            host=host, port=port
        )

@dataclass
class Config:
    """
    The main configuration class that integrates all the other configuration classes.

    This class holds the other configuration classes, providing a centralized point of access for all settings.

    Attributes
    ----------
    db : Optional[DbConfig]
        Holds the settings specific to the database (default is None).
    """

    db: DbConfig
    server: ServerConfig


def load_config(path: str = None) -> Config:
    """
    This function takes an optional file path as input and returns a Config object.
    :param path: The path of env file from where to load the configuration variables.
    It reads environment variables from a .env file if provided, else from the process environment.
    :return: Config object with attributes set as per environment variables.
    """

    # Create an Env object.
    # The Env object will be used to read environment variables.
    env = Env()
    env.read_env(path)

    return Config(
        db=DbConfig.from_env(env), server=ServerConfig.from_env(env)
    )
