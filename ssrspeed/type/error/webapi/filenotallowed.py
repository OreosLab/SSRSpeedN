from ssrspeed.type.error.webapi.base import WebErrorBase


class FileNotAllowed(WebErrorBase):
    err_msg = "File type not allowed"
    err_tag = "FILE_NOT_ALLOWED"