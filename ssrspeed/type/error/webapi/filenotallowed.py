from ssrspeed.type.error.webapi.basis import WebErrorBasis


class FileNotAllowed(WebErrorBasis):
    err_msg = "File type not allowed"
    err_tag = "FILE_NOT_ALLOWED"
