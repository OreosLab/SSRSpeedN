class Sorter:
    @staticmethod
    def __sort_by_speed(result: dict) -> float:
        return result["dspeed"]

    @staticmethod
    def __sort_by_ping(result: dict) -> float:
        return result["ping"]

    def sort_result(self, result: list, sort_method: str) -> list:
        if sort_method == "PING":
            result.sort(key=self.__sort_by_ping)
        elif sort_method == "REVERSE_PING":
            result.sort(key=self.__sort_by_ping, reverse=True)
        elif sort_method == "REVERSE_SPEED":
            result.sort(key=self.__sort_by_speed)
        elif sort_method == "SPEED":
            result.sort(key=self.__sort_by_speed, reverse=True)
        return result
