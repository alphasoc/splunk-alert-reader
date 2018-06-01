import os
import sys

if sys.version_info[0] == 2:
    import ConfigParser
    import urlparse
else:
    import configparser as ConfigParser
    import urllib.parse as urlparse

DEFAULT_SPLUNK_SERVICE_PORT = 8089
MAX_OUTPUT_JSON_VERSION = 2


class Connection(object):
    def __init__(self, scheme, host, port, username, password):
        self.scheme = scheme
        self.host = host
        self.port = port
        self.username = username
        self.password = password

    @classmethod
    def from_config(cls, config):
        if not config.has_section('connection'):
            config.add_section('connection')

        username = config.get('connection', 'username')
        password = config.get('connection', 'password')

        url = urlparse.urlparse(config.get('connection', 'address'))

        scheme = url.scheme
        if not scheme:
            raise ValueError("Unrecognized url scheme (possible values https:// or http://)")

        host = url.hostname
        if not host:
            raise ValueError("Unrecognized hostname")

        try:
            port = url.port if url.port else DEFAULT_SPLUNK_SERVICE_PORT
        except ValueError:
            raise ValueError("Port number in url address must be an integer")

        return cls(scheme, host, port, username, password)


class Output(object):
    def __init__(self, format_version):
        self.format_version = format_version

    @classmethod
    def from_config(cls, config):
        if not config.has_section('output'):
            config.add_section('output')

        format_version = cls.get_format_version(config, 'format_version', max_version=MAX_OUTPUT_JSON_VERSION)

        return cls(format_version)

    @staticmethod
    def get_format_version(config, option, section='output', max_version=1):
        if not config.has_option(section, option):
            return max_version

        value = config.get(section, option)
        if not value:
            return max_version

        try:
            value = int(value)
        except ValueError:
            raise ValueError("Wrong {0} value in configuration file (required integer)".format(option))

        if value < 1 or value > max_version:
            raise ValueError(
                "Wrong {0} value in configuration file (required >= 1 and <= {1})".format(option, max_version))

        return value


class Query(object):
    def __init__(self, timeout, unfold, earliest, index):
        self.timeout = timeout
        self.unfold = unfold

        self.earliest = earliest
        self.index = index

    @classmethod
    def from_config(cls, config):
        if not config.has_section('query'):
            config.add_section('query')

        timeout = cls.get_positive_int(config, 'timeout')
        unfold = cls.get_boolean(config, 'unfold')

        earliest = cls.get_positive_int(config, 'earliest_minutes', default=5, include_zero=False)
        index = cls.get_index(config)

        return cls(timeout, unfold, earliest, index)

    @staticmethod
    def get_positive_int(config, option, section='query', default=0, include_zero=True):
        if not config.has_option(section, option):
            return default

        value = config.get(section, option)
        if not value:
            return default

        try:
            value = int(value)
        except ValueError:
            raise ValueError("Wrong {0} value in configuration file (required integer)".format(option))

        minimum = 0 if include_zero else 1
        if value < minimum:
            raise ValueError("Wrong {0} value in configuration file (required >= {1})".format(option, minimum))

        return value

    @staticmethod
    def get_boolean(config, option, section='query', default=False):
        if not config.has_option(section, option):
            return default

        value = config.get(section, option)
        if not value:
            return default

        try:
            value = config.getboolean(section, option)
        except ValueError:
            raise ValueError("Wrong {0} value in configuration file (required 0 or 1)".format(option))

        return value

    @staticmethod
    def get_index(config):
        if not config.has_option('query', 'index'):
            return "*"

        index = config.get('query', 'index')
        if not index:
            return "*"

        index = config.get('query', 'index')
        return index


def create_config(config_path):
    if not config_path:
        raise ValueError("Configuration file is required")

    if not os.path.exists(config_path):
        raise ValueError("Configuration file not found")
    else:
        try:
            with open(config_path, mode="r+"):
                pass
        except IOError:
            raise ValueError("Could not open configuration file")

        config = ConfigParser.ConfigParser(allow_no_value=True)
        config.read(config_path)

        return config
