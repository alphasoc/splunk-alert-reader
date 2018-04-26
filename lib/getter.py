import sys
import json

from . import search
from . import batch
from . import formats


class Getter(object):
    def __init__(self, client, params_query):
        self._config_query = params_query

        self._formatter = formats.Unfold if self._config_query.unfold else formats.Full
        self._batch = batch.Batch()

        self._client = client
        self._output = sys.stdout

    def run(self):
        response = self._run_search()

        for row in response.content:
            alert = self._create_alert(row)
            if alert is not None:
                self._batch.add(alert)

        if not self._batch.is_empty():
            self._flush()

    def _run_search(self):
        export = search.Export(self._client)
        query = self._formatter.get_query(self._config_query)

        response = export.run(query)
        return response

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

        return alert

    def _flush(self):
        alerts = self._batch.get_list()
        formatted_alerts = self._formatter.alerts(alerts)

        self._output.write(formatted_alerts)
        self._batch.clear()
