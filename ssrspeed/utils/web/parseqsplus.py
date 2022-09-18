def parse_qs_plus(dict_) -> dict:
    data: dict = {}
    if not isinstance(dict_, dict):
        return dict_
    for k, v in dict_.items():
        if isinstance(v, list):
            if len(v) == 0:
                data[k] = []
            elif len(v) == 1:
                data[k] = v[0]
            else:
                list_ = []
                for item in v:
                    list_.append(parse_qs_plus(item))
                data[k] = list_
        else:
            data[k] = v
    return data
