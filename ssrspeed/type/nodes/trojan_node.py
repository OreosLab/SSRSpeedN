from .base_node import BaseNode


class NodeTrojan(BaseNode):
    def __init__(self, config: dict):
        super(NodeTrojan, self).__init__(config)
        self._type = "Trojan"
