from .base_node import BaseNode


class NodeV2Ray(BaseNode):
    def __init__(self, config: dict):
        super(NodeV2Ray, self).__init__(config)
        self._type = "V2Ray"
