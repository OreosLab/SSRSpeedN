from ssrspeed.type.node.base import BaseNode


class NodeV2Ray(BaseNode):
    def __init__(self, config: dict):
        super().__init__(config)
        self._type = "V2Ray"
