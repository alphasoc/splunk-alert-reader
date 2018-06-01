EVENTS_SOURCETYPE_DNSA = "asoc:dns:event"
EVENTS_SOURCETYPE_NBA = "asoc:nba:event"


class DNSA(object):
    @staticmethod
    def get(params, last_indextime):
        mvexpand = "| mvexpand threats{} " if params.unfold else ""

        return (
            'search index="{0}" sourcetype="{1}" type="alert" threats{{}}=* '
            '_indextime > {2} _index_earliest=-{3}m {4}'
            '| lookup asocthreats name AS threats{{}} OUTPUT title, severity, policy '
            '| eval policy=if(isnull(policy), 0, policy) '
            '| search title=* '
            '| eval ts=strftime(strptime(original_event, "%d-%b-%Y %H:%M:%S%z"), "%Y-%m-%dT%H:%M:%S%z") '
            '| rename flags{{}} AS flags, threats{{}} AS threats '
            '| sort _indextime '
            '| table _indextime, dest_host, flags, group, ts, record_type, src_ip, '
            'title, severity, policy, threats, type'
        ).format(params.index, EVENTS_SOURCETYPE_DNSA, last_indextime, params.earliest, mvexpand)


class NBA(object):
    @staticmethod
    def get(params, last_indextime):
        mvexpand = "| mvexpand threats " if params.unfold else ""

        return (
            'search index="{0}" sourcetype="{1}" type="alert" threats=* '
            '_indextime > {2} _index_earliest=-{3}m {4}'
            '| lookup asocnbathreats name AS threats OUTPUT title, severity, policy '
            '| eval policy=if(isnull(policy), 0, policy) '
            '| search title=* '
            '| eval ts=strftime(strptime(original_event, "%d-%b-%Y %H:%M:%S%z"), "%Y-%m-%dT%H:%M:%S%z") '
            '| spath details '
            '| spath wisdom '
            '| sort _indextime '
            '| table _indextime, dest, dest_port, src_groups, ts, details, src_ip, src_port, wisdom, '
            'title, severity, policy, threats, section'
        ).format(params.index, EVENTS_SOURCETYPE_NBA, last_indextime, params.earliest, mvexpand)
