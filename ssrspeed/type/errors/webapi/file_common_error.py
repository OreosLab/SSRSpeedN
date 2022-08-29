from ssrspeed.type.errors.webapi import WebErrorBase


class WebFileCommonError(WebErrorBase):
    errMsg = "Upload failed."
    errTag = "FILE_COMMON_ERROR"

    def __init__(self):
        super(WebFileCommonError, self).__init__()
