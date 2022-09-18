from ssrspeed.type.errors.webapi.base_error import WebErrorBase


class WebFileCommonError(WebErrorBase):
    err_msg = "Upload failed."
    err_tag = "FILE_COMMON_ERROR"
