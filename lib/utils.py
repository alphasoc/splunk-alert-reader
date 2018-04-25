import datetime


class Timezone(datetime.tzinfo):
    def __init__(self, tzstr=None):
        super(Timezone, self).__init__()

        hours, minutes = None, None
        if tzstr == 'Z' or tzstr is None:
            hours = 0
            minutes = 0

        elif is_string(tzstr):
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


def iso8601_to_local(datestr):
    try:
        dtime = datetime.datetime.strptime(datestr[:19], "%Y-%m-%dT%H:%M:%S")
        tzone = Timezone(datestr[19:])
    except (TypeError, ValueError):
        return None

    dtime = dtime.replace(tzinfo=tzone)
    return dtime


def is_string(value):
    try:
        return isinstance(value, basestring)
    except NameError:
        return isinstance(value, str)
