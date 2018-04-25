import os
import sys
import argparse

from splunklib import client
from splunklib import binding
from lib import getter

if sys.version_info[0] == 2:
    from ConfigParser import ConfigParser
else:
    from configparser import ConfigParser


def main():
    parser = argparse.ArgumentParser(description='Get alerts from Splunk and write to specific destination.')

    parser.add_argument('--config', help='path to configuration file')
    parser.add_argument('--output', help='path to output file')
    parser.add_argument("--unfold", help="split threats", action='store_true')

    args = parser.parse_args()
    if not args.config:
        raise ValueError("configuration file is required")

    if not os.path.exists(args.config):
        raise ValueError("configuration file not found")
    else:
        config = ConfigParser()
        config.read(args.config)

    config_args = connection_settings(config)
    proc_settings = processing_settings(config)

    service = connect(config_args)

    if proc_settings['timeout'] and proc_settings['timeout'] > 0:
        service.http = binding.HttpLib(binding.handler(timeout=proc_settings['timeout']))

    if proc_settings['output'] and not os.path.exists(proc_settings['output']):
        raise ValueError("output file not found")
    elif proc_settings['output']:
        proc_settings['output'] = open(proc_settings['output'], 'a')

    g = getter.Getter(service, proc_settings)
    g.run()


def connect(settings):
    return client.connect(
        host=settings['host'],
        port=settings['port'],
        username=settings['username'],
        password=settings['password'],
    )


def connection_settings(config):
    return {
        'host': config.get('connection', 'host'),
        'port': config.get('connection', 'port'),
        'username': config.get('connection', 'user'),
        'password': config.get('connection', 'password'),
    }


def processing_settings(config):
    return {
        'unfold': config.getboolean('processing', 'unfold'),
        'timeout': config.getint('processing', 'timeout'),
        'max_batch_items': config.getint('processing', 'max_batch_items'),
        'output': config.get('processing', 'output'),
    }


if __name__ == "__main__":
    main()
