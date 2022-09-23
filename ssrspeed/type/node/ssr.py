from ssrspeed.type.node.base import BaseNode


class NodeShadowsocksR(BaseNode):
    def __init__(self, config: dict):
        super().__init__(config)
        self._type = "ShadowsocksR"
