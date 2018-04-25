class Export(object):
    def __init__(self, client):
        self._client = client

    def run(self, query):
        result = self._client.post(
            "/services/search/jobs/export/",
            output_mode='json',
            search=query,
        )

        return Response.from_rest_string(result)


class Response(object):
    def __init__(self, code, content):
        self.code = code
        self.content = content

    @classmethod
    def from_rest_string(cls, result):
        return cls(result.status, result.body)
