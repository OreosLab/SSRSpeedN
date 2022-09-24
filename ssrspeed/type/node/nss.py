from ssrspeed.type.node.basis import BasisNode


class NodeShadowsocks(BasisNode):
    def __init__(self, config: dict):
        super().__init__(config)
        self._type = "Shadowsocks"
