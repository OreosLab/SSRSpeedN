class WebErrorBasis:
    err_msg: str = ""
    err_tag: str = ""

    def __init__(self):
        raise TypeError("Web Errors should not be instantiated.")
