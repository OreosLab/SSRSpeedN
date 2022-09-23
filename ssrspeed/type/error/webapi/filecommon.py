from ssrspeed.type.error.webapi.base import WebErrorBase


class WebFileCommonError(WebErrorBase):
    err_msg = "Upload failed."
    err_tag = "FILE_COMMON_ERROR"
