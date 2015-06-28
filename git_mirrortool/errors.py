
class RequestFailed(Exception):

    def __init__(self, response):
        self.response = response
        Exception.__init__(self, "HTTP Request Failed: %r" % response)


class UnexpectedResponse(Exception):

    def __init__(self, response, message):
        self.response = response
        Exception.__init__(self, message)
