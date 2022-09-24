from ssrspeed.type.error.webapi.basis import WebErrorBasis


class WebFileCommonError(WebErrorBasis):
    err_msg = "Upload failed."
    err_tag = "FILE_COMMON_ERROR"
