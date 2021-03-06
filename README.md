# Splunk Alert Reader

> Output AlphaSOC alerts indexed in Splunk to stdout

Splunk Alert Reader retrieves alerts generated by [AlphaSOC applications for Splunk](https://splunkbase.splunk.com/apps/#/search/alphasoc/) and outputs them to `stdout` in a JSON format that can be ingested easily by SIEM products (e.g. IBM QRadar, AlienVault USM), SOAR platforms (e.g. Demisto), and custom scripts that users may create to work with and escalate AlphaSOC alerts.

At the first run, the tool retrieves alerts which are at most 60 minutes old from Splunk (this can be modified in the config file). The subsequent runs return new alerts only. This behavior makes it easy to schedule it with cron at any interval. The emitted alerts may be then processed further and escalated.

## Requirements

The tool requires Python >=2.7 or >=3.1. No 3rd party Python libraries are required. The [Splunk SDK for Python](http://dev.splunk.com/python) is included in the repository. It doesn't have to be run from the Search Head, as it connects to the Splunk's service port over the network.

## Installation and usage example

```sh
git clone https://github.com/alphasoc/splunk-alert-reader.git
cd splunk-alert-reader
cp example.ini config.ini
```

After completing the steps above, update `config.ini` with your Splunk credentials and adjust other configuration options as needed. Ensure that the tool can connect to the Splunk's service port (default 8089). After doing that, you may run the script:

```sh
python main.py --config config.ini
```

## Alert format

The tool returns AlphaSOC alerts in a JSON format, one alert per line. Alerts can be received from two apps: DNS Analytics for Splunk and Network Behavior Analytics for Splunk. There are significant differences between the output returned by these apps so alerts can't be fetched from both applications at single run. You can choose the application in the configuration file by setting `format_version` option. 

### DNS Analytics alert

If you'd like to receive alerts from DNS Analytics, please set `format_version=1`. By default, DNS Analytics alerts may consist of more than one corresponding raw DNS event and/or assigned threat. You can change this behavior by adjusting the `unfold` config option. When changed to 1, the tool will emit one entry per network event and threat.

```json
{
  "threats": [
    {
      "policy": true,
      "desc": "Multiple requests for DGA domains indicating infection",
      "id": "dga_volume",
      "severity": 4
    },
    {
      "policy": true,
      "desc": "Multiple requests to unreachable domains",
      "id": "unreachable_domain_volume",
      "severity": 2
    }
  ],
  "risk": 4,
  "ip": "10.14.1.39",
  "fqdn": "rproahjondxj.net",
  "ts": ["2018-04-26T12:40:41+00:00", "2018-04-26T12:39:21+00:00"],
  "record_type": "A",
  "flags": ["perplexing_domain", "unreachable_domain"],
  "groups": [
    {
      "desc": "Zurich"
    }
  ],
  "type": "alert"
}
```

Note: the above would be unfolded to 4 separate alerts (as it contains two raw DNS event timestamps, and two assigned threats)

### Network Behavior Analytics alert

To receive alerts from Network Behavior Analytics, please set `format_version=2` in the configuration file. Currently Network Behavior Analytics can render alerts with two types of corresponding events: `dns` or `ip`. If you'd like to emit one entry per threat, please change `unfold` option to 1.

```json
{
  "threats": {
    "conn_unusual_port_volume": {
      "policy": false,
      "severity": 3,
      "desc": "Multiple outbound connections to an unusual server port"
    },
    "c2_communication": {
      "policy": false,
      "severity": 5,
      "desc": "C2 communication attempt indicating infection"
    }
  },
  "risk": 5,
  "eventType": "ip",
  "wisdom": {
    "c2Proto": "DarkComet",
    "flags": ["c2"]
  },
  "groups": {
    "london": {
      "desc": "London"
    }
  },
  "event": {
    "proto": "tcp",
    "bytesOut": 9866,
    "srcPort": 64329,
    "ts": "2018-06-06T07:33:04+00:00",
    "destIP": "94.188.103.122",
    "srcIP": "10.100.91.3",
    "destPort": 1604,
    "bytesIn": 21357
  }
}
```

In the above format, `event` object can contains raw DNS or IP event depending on `eventType` value. 

#### DNS event

```json
{
  "event": {
    "srcIP": "10.14.1.43",
    "query": "rproahjondxj.net",
    "qtype": "A",
    "ts": "2018-06-06T09:17:00+00:00"
  }
}
```

#### IP event

```json
{
  "event": {
    "proto": "tcp",
    "bytesOut": 9866,
    "srcPort": 64329,
    "ts": "2018-06-06T07:33:04+00:00",
    "destIP": "94.188.103.122",
    "srcIP": "10.100.91.3",
    "destPort": 1604,
    "bytesIn": 21357
  }
}
```

## Release History

* 0.0.1
  * Initial release
* 0.0.2
  * Network Behavior Analytics compatibility

## License

Distributed under the MIT license. See `LICENSE` for more information.
