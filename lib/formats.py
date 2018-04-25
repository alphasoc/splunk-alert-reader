import os
import json

from . import utils

EVENTS_SOURCETYPE = "asoc:dns:event"


class Full(object):
    @staticmethod
    def get_query():
        return (
            'search index=* sourcetype="{0}" type="alert" threats{{}}=* _index_earliest=-5m '
            '| lookup asocthreats name AS threats{{}} OUTPUT title, severity, policy '
            '| eval policy=if(isnull(policy), 0, policy) '
            '| search title=* '
            '| eval ts=strftime(strptime(original_event, "%d-%b-%Y %H:%M:%S%z"), "%Y-%m-%dT%H:%M:%S%z")'
            '| rename flags{{}} AS flags, threats{{}} AS threats '
            '| table dest_host, flags, group, ts, record_type, src_ip, title, severity, policy, threats, type'
        ).format(EVENTS_SOURCETYPE)

    @staticmethod
    def alerts(alerts):
        return json.dumps({'events': alerts}) + os.linesep

    @staticmethod
    def date(timestamp):
        if not timestamp:
            return []

        try:
            return [utils.iso8601_to_local(timestamp).isoformat()]
        except:
            return []

    @staticmethod
    def groups(groups):
        if not groups:
            return []

        if utils.is_string(groups):
            groups = [groups]

        if not isinstance(groups, list):
            return []

        formatted = []
        for group in groups:
            formatted.append({'desc': group})

        return formatted

    @staticmethod
    def risk(severities):
        if not severities:
            return None

        if utils.is_string(severities):
            try:
                return int(severities)
            except:
                return None

        if isinstance(severities, int):
            return severities

        if not isinstance(severities, list):
            return None

        max_severity = -1
        for severity in severities:
            try:
                severity = int(severity)
                if severity > max_severity:
                    max_severity = severity
            except:
                continue

        return max_severity if max_severity >= 0 else None

    @staticmethod
    def flags(flags):
        if not flags:
            return []

        if utils.is_string(flags):
            flags = [flags]

        if not isinstance(flags, list):
            return []

        return flags

    @staticmethod
    def threats(labels, title, severity, policy):
        if not labels:
            return {}

        if utils.is_string(labels):
            labels = [labels]

        if utils.is_string(title):
            title = [title]

        if utils.is_string(severity):
            severity = [severity]

        if utils.is_string(policy):
            policy = [policy]

        threats = []
        for index, label in enumerate(labels):
            try:
                threat = {
                    'id': label,
                    'severity': int(severity[index]),
                    'desc': title[index],
                    'policy': bool(policy[index]),
                }
                threats.append(threat)
            except:
                continue

        return threats


class Unfold(Full):
    @staticmethod
    def get_query():
        return (
            'search index=* sourcetype="{0}" type="alert" threats{{}}=* _index_earliest=-5m '
            '| mvexpand threats{{}}'
            '| lookup asocthreats name AS threats{{}} OUTPUT title, severity, policy '
            '| eval policy=if(isnull(policy), 0, policy) '
            '| search title=* '
            '| eval ts=strftime(strptime(original_event, "%d-%b-%Y %H:%M:%S%z"), "%Y-%m-%dT%H:%M:%S%z")'
            '| rename flags{{}} AS flags, threats{{}} AS threats '
            '| table dest_host, flags, group, ts, record_type, src_ip, title, severity, policy, threats, type'
        ).format(EVENTS_SOURCETYPE)

    @staticmethod
    def alerts(alerts):
        alerts_json = ""
        for alert in alerts:
            alerts_json += json.dumps(alert) + os.linesep

        return alerts_json
