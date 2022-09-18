from ssrspeed.type.nodes.base_node import BaseNode


class NodeTrojan(BaseNode):
    def __init__(self, config: dict):
        super().__init__(config)
        self._type = "Trojan"
