from ssrspeed.type.node.basis import BasisNode


class NodeShadowsocksR(BasisNode):
    def __init__(self, config: dict):
        super().__init__(config)
        self._type = "ShadowsocksR"
