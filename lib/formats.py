import os
import json

from . import queries
from . import events
from . import utils


class Formatter(object):
    @staticmethod
    def init(config_output):
        if config_output.format_version == 1:
            return JsonDNSA()

        return JsonNBA()

    @staticmethod
    def get_indextime(result):
        try:
            return int(result.get('_indextime'))
        except:
            return 0

    @staticmethod
    def format_flags(flags):
        return utils.Parser.mvfield(flags)

    @staticmethod
    def format_risk(severities):
        if utils.Parser.is_string(severities):
            try:
                return int(severities)
            except:
                raise ValueError("Unable to transform risk score to number")

        if isinstance(severities, int):
            return severities

        if not isinstance(severities, list):
            raise ValueError("Risk score has unexpected format")

        max_severity = -1
        for severity in severities:
            try:
                max_severity = max(max_severity, int(severity))
            except:
                continue

        if max_severity < 0:
            raise ValueError("Risk score not found in parsed result")

        return max_severity

    @staticmethod
    def format_wisdom(wisdom):
        wisdom = utils.Parser.spath_dict(wisdom)
        if 'flags' not in wisdom:
            wisdom['flags'] = []

        return wisdom

    @classmethod
    def dumps(cls, alerts, unfold=False):
        if unfold:
            return cls._dumps_unfold(alerts)

        return cls._dumps_full(alerts)

    @staticmethod
    def _dumps_unfold(alerts):
        alerts_json = ""
        for alert in alerts:
            alerts_json += json.dumps(alert) + os.linesep

        return alerts_json

    @staticmethod
    def _dumps_full(alerts):
        return json.dumps({'events': alerts}) + os.linesep


class JsonDNSA(Formatter):
    def __init__(self):
        self._query = queries.DNSA

    def get_query(self, params, last_indextime):
        return self._query.get(params, last_indextime)

    @classmethod
    def format(cls, result):
        alert = {}

        alert['type'] = result.get('type', '')
        alert['ip'] = result.get('src_ip', '')
        alert['fqdn'] = result.get('dest_host', '')
        alert['record_type'] = result.get('record_type', '')

        alert['ts'] = [utils.Parser.date(result.get('ts'))]
        alert['groups'] = cls.format_groups(result.get('group'))
        alert['flags'] = cls.format_flags(result.get('flags'))
        alert['risk'] = cls.format_risk(result.get('severity'))

        alert['threats'] = cls.format_threats(
            result.get('threats'),
            result.get('title'),
            result.get('severity'),
            result.get('policy'),
        )

        return alert

    @staticmethod
    def format_groups(groups):
        groups = utils.Parser.mvfield(groups)

        formatted = []
        for group in groups:
            if not utils.Parser.is_string(group):
                continue

            formatted.append({'label': group.lower(), 'desc': group})

        return formatted

    @staticmethod
    def format_threats(labels, title, severity, policy):
        labels = utils.Parser.mvfield(labels)
        title = utils.Parser.mvfield(title)
        severity = utils.Parser.mvfield(severity)
        policy = utils.Parser.mvfield(policy)

        threats = []
        for index, label in enumerate(labels):
            try:
                threat = {
                    'id': label,
                    'severity': int(severity[index]),
                    'desc': title[index],
                    'policy': utils.Parser.str_to_bool(policy[index]),
                }
                threats.append(threat)
            except:
                continue

        return threats


class JsonNBA(Formatter):
    def __init__(self):
        self._query = queries.NBA

    def get_query(self, params, last_indextime):
        return self._query.get(params, last_indextime)

    @classmethod
    def format(cls, result):
        alert = {}

        alert['eventType'] = result.get('section', '')
        alert['event'] = cls._format_event(result, alert['eventType'])
        alert['groups'] = cls.format_groups(result.get('src_groups'))
        alert['risk'] = cls.format_risk(result.get('severity'))
        alert['wisdom'] = cls.format_wisdom(result.get('wisdom'))

        alert['threats'] = cls.format_threats(
            result.get('threats'),
            result.get('title'),
            result.get('severity'),
            result.get('policy'),
        )

        return alert

    @staticmethod
    def _format_event(result, section):
        if section == "dns":
            return events.DNS.format(result)
        elif section == "ip":
            return events.IP.format(result)
        else:
            raise ValueError("Unsupported event type")

    @staticmethod
    def format_groups(groups):
        groups = utils.Parser.mvfield(groups)

        formatted = {}
        for group in groups:
            if not utils.Parser.is_string(group):
                continue

            formatted[group.lower()] = {'desc': group}

        return formatted

    @staticmethod
    def format_threats(labels, title, severity, policy):
        labels = utils.Parser.mvfield(labels)
        title = utils.Parser.mvfield(title)
        severity = utils.Parser.mvfield(severity)
        policy = utils.Parser.mvfield(policy)

        threats = {}
        for index, label in enumerate(labels):
            try:
                threat = {
                    'severity': int(severity[index]),
                    'desc': title[index],
                    'policy': utils.Parser.str_to_bool(policy[index]),
                }
                threats[label] = threat
            except:
                continue

        return threats
