from copy import deepcopy


class BasisNode:
    def __init__(self, config: dict):
        self._type: str = ""
        if not isinstance(config, dict):
            raise TypeError("The 'config' parameter must be dict")
        self._config: dict = config

    def __repr__(self) -> str:
        return f"<{self.__class__.__name__}>, Proxy Type: {self.node_type}"

    @property
    def node_type(self) -> str:
        if not self._type:
            raise NotImplementedError
        return self._type

    @property
    def config(self) -> dict:
        return deepcopy(self._config)

    def update_config(self, new_cfg: dict):
        if new_cfg:
            self._config.update(new_cfg)

    def __key(self):
        return self._config["server"], self._config["server_port"]

    def __hash__(self):
        return hash(self.__key())

    def __eq__(self, other) -> bool:
        if isinstance(other, BasisNode):
            return self.__key() == other.__key()
        return NotImplemented
