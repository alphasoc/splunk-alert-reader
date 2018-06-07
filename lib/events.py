from . import utils


class DNS(object):
    @staticmethod
    def format(result):
        event = {}

        event['ts'] = utils.Parser.date(result.get('ts'))
        event['srcIP'] = result.get('src_ip', '')
        event['query'] = result.get('dest', '')

        details = utils.Parser.spath_dict(result.get('details'))
        if 'record_type' in details:
            event['qtype'] = details['record_type']

        return event


class IP(object):
    @staticmethod
    def format(result):
        event = {}

        event['ts'] = utils.Parser.date(result.get('ts'))
        event['srcIP'] = result.get('src_ip', '')
        event['destIP'] = result.get('dest', '')

        src_port = utils.Parser.number(result.get('src_port'))
        if src_port is not None:
            event['srcPort'] = src_port

        dest_port = utils.Parser.number(result.get('dest_port'))
        if dest_port is not None:
            event['destPort'] = dest_port

        details = utils.Parser.spath_dict(result.get('details'))
        event['proto'] = details.get('transport', '')

        if 'bytes_in' in details:
            event['bytesIn'] = details['bytes_in']

        if 'bytes_out' in details:
            event['bytesOut'] = details['bytes_out']

        return event
