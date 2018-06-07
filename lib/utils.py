import datetime
import json


class Parser(object):
    @staticmethod
    def number(value):
        try:
            return int(value)
        except:
            return None

    @staticmethod
    def is_string(value):
        try:
            return isinstance(value, basestring)
        except NameError:
            return isinstance(value, str)

    @staticmethod
    def mvfield(value):
        if value is None or value == "":
            return []

        if Parser.is_string(value):
            return [value]

        if not isinstance(value, list):
            return []

        return value

    @staticmethod
    def str_to_bool(value):
        if Parser.is_string(value):
            value = value.lower()

        return value in ['true', '1', 1, True]

    @staticmethod
    def date(timestamp):
        try:
            dtime = datetime.datetime.strptime(timestamp[:19], "%Y-%m-%dT%H:%M:%S")
            tzone = Timezone(timestamp[19:])

            return dtime.replace(tzinfo=tzone).isoformat()
        except:
            return ""

    @staticmethod
    def spath_dict(value):
        try:
            value = json.loads(value)
        except:
            value = {}

        if not isinstance(value, dict):
            value = {}

        return value


class Timezone(datetime.tzinfo):
    def __init__(self, tzstr=None):
        super(Timezone, self).__init__()

        hours, minutes = None, None
        if tzstr == 'Z' or tzstr is None:
            hours = 0
            minutes = 0

        elif Parser.is_string(tzstr):
            tzstrlen = len(tzstr)
            if tzstrlen == 6:
                colon = 1
            elif tzstrlen == 5:
                colon = 0
            elif tzstrlen != 0:
                raise ValueError("Unrecognized timezone format")

            if tzstrlen == 0:
                hours, minutes = 0, 0
            else:
                hours = int(tzstr[:3])
                minutes = int(tzstr[3 + colon:])

        elif isinstance(tzstr, (list, tuple)):
            hours, minutes = tzstr
            assert minutes >= 0

        if hours is None or minutes is None:
            raise ValueError("Unrecognized timezone format")
        else:
            if hours < 0:
                self.offset = -datetime.timedelta(hours=abs(hours), minutes=minutes)
                sign = '-'
            else:
                self.offset = datetime.timedelta(hours=abs(hours), minutes=minutes)
                sign = '+'

            self.name = "%s%02i:%02i" % (sign, abs(hours), minutes)

    def utcoffset(self, dt):
        return self.offset

    def tzname(self, dt):
        return self.name

    def dst(self, dt):
        return datetime.timedelta(0)

    def __repr__(self):
        return u"<TZ: %s>" % self.name
