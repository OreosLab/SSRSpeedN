from ssrspeed.type.nodes.base_node import BaseNode


class NodeV2Ray(BaseNode):
    def __init__(self, config: dict):
        super().__init__(config)
        self._type = "V2Ray"
