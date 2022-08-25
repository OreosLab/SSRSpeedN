class WebErrorBase(object):
    errMsg: str = ""
    errTag: str = ""

    def __init__(self):
        raise TypeError("Web Errors should not be instantiated.")
