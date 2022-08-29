class Sorter(object):
    def __init__(self):
        pass

    @staticmethod
    def __sort_by_speed(result) -> float:
        return result["dspeed"]

    @staticmethod
    def __sort_by_ping(result) -> float:
        return result["ping"]

    def sort_result(self, result, sort_method: str) -> dict:
        if sort_method != "":
            if sort_method == "SPEED":
                result.sort(key=self.__sort_by_speed, reverse=True)
            elif sort_method == "REVERSE_SPEED":
                result.sort(key=self.__sort_by_speed)
            elif sort_method == "PING":
                result.sort(key=self.__sort_by_ping)
            elif sort_method == "REVERSE_PING":
                result.sort(key=self.__sort_by_ping, reverse=True)
        return result
