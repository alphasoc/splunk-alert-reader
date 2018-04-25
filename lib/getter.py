import sys
import json

from . import search
from . import batch
from . import formats


class Getter(object):
    def __init__(self, client, settings):
        self._batch = batch.Batch(settings['max_batch_items'])
        self._unfold = True if settings['unfold'] else False
        self._formatter = formats.Unfold if self._unfold else formats.Full

        self._client = client
        self._output = settings['output'] if settings['output'] else sys.stdout

    def run(self):
        response = self._run_search()

        for row in response.content:
            alert = self._create_alert(row)
            if alert is not None:
                self._batch.add(alert)

            if self._batch.is_ready():
                self._flush()

        if not self._batch.is_empty():
            self._flush()

    def _run_search(self):
        export = search.Export(self._client)
        query = self._formatter.get_query()

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
        alert['fqdn'] = result.get('dest_host', '')
        alert['record_type'] = result.get('record_type', '')

        alert['ts'] = self._formatter.date(result.get('ts'))
        alert['groups'] = self._formatter.groups(result.get('group'))
        alert['flags'] = self._formatter.flags(result.get('flags'))

        risk = self._formatter.risk(result.get('severity'))
        if risk:
            alert['risk'] = risk

        th_id = result.get('threats')
        th_title = result.get('title')
        th_severity = result.get('severity')
        th_policy = result.get('policy')

        alert['threats'] = self._formatter.threats(th_id, th_title, th_severity, th_policy)

        return alert

    def _flush(self):
        alerts = self._batch.get_list()
        formatted_alerts = self._formatter.alerts(alerts)

        self._output.write(formatted_alerts)
        self._batch.clear()
