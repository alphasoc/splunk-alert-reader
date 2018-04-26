import sys
import json

from . import search
from . import formats
from . import params


class Getter(object):
    def __init__(self, client, config, config_path, params_query):
        self._config = config
        self._config_path = config_path

        self._config_query = params_query

        self._formatter = formats.Unfold if self._config_query.unfold else formats.Full

        self._client = client
        self._output = sys.stdout

        self._last_indextime = 0

    def run(self):
        response = self._run_search()

        for raw in response.content:
            alert = self._create_alert(raw)
            if alert is not None:
                yield alert

        if self._last_indextime > 0:
            self._save_last_indextime()

    def _run_search(self):
        export = search.Export(self._client)
        last_indextime = self._get_last_indextime()

        query = self._formatter.get_query(self._config_query, last_indextime)
        response = export.run(query)
        return response

    def _get_last_indextime(self):
        if not self._config.has_section('processing'):
            self._config.add_section('processing')

        try:
            last_indextime = params.Query.get_positive_int(self._config, 'last_indextime', section='processing')
        except:
            last_indextime = 0

        return last_indextime

    def _save_last_indextime(self):
        if not self._config.has_section('processing'):
            self._config.add_section('processing')

        try:
            self._config.set('processing', 'last_indextime', str(self._last_indextime))

            with open(self._config_path, 'w') as configfile:
                self._config.write(configfile)
        except:
            pass

    def _create_alert(self, row):
        try:
            parsed_row = json.loads(row)
            alert = self._format_alert(parsed_row['result'])
        except:
            alert = None

        return alert

    def _format_alert(self, result):
        alert = {}

        alert['type'] = result.get('type', '')
        alert['ip'] = result.get('src_ip', '')
        alert['fqdn'] = result.get('dest_host', '')
        alert['record_type'] = result.get('record_type', '')

        alert['ts'] = self._formatter.date(result.get('ts'))
        alert['groups'] = self._formatter.groups(result.get('group'))
        alert['flags'] = self._formatter.flags(result.get('flags'))

        risk = self._formatter.risk(result.get('severity'))
        if risk:
            alert['risk'] = risk

        threats = result.get('threats')
        title = result.get('title')
        severity = result.get('severity')
        policy = result.get('policy')

        alert['threats'] = self._formatter.threats(threats, title, severity, policy)

        indextime = self._parse_last_indextime(result.get('_indextime'))
        if indextime > self._last_indextime:
            self._last_indextime = indextime

        return alert

    @staticmethod
    def _parse_last_indextime(indextime):
        try:
            indextime = int(indextime)
        except:
            indextime = 0

        return indextime

    def print_alerts(self, alerts):
        formatted_alerts = self._formatter.alerts(alerts)
        self._output.write(formatted_alerts)
