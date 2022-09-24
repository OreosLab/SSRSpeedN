from ssrspeed.type.node.basis import BasisNode


class NodeV2Ray(BasisNode):
    def __init__(self, config: dict):
        super().__init__(config)
        self._type = "V2Ray"
