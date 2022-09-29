from ssrspeed.type.node.basis import BasisNode


class NodeVmess(BasisNode):
    def __init__(self, config: dict):
        super().__init__(config)
        self._type = "Vmess"
