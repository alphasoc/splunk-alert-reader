import sys
import json

from . import search
from . import formats
from . import params


class Getter(object):
    def __init__(self, client, config, config_path, params_query, params_output):
        self._config = config
        self._config_path = config_path

        self._config_query = params_query
        self._config_output = params_output

        self._formatter = formats.Formatter.init(self._config_output)

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
            result = json.loads(row)['result']
            alert = self._formatter.format(result)
            self._update_indextime(result)
        except:
            alert = None

        return alert

    def _update_indextime(self, result):
        indextime = self._formatter.get_indextime(result)
        if indextime > self._last_indextime:
            self._last_indextime = indextime

    def print_alerts(self, alerts):
        formatted_alerts = self._formatter.dumps(alerts, self._config_query.unfold)
        self._output.write(formatted_alerts)
