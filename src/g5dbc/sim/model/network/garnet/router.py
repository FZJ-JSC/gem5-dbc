from g5dbc.sim.m5_objects.ruby.network import m5_GarnetRouter

from ...network.NetworkRouter import NetworkRouter


class Garnet_Router(m5_GarnetRouter, NetworkRouter):

    def __init__(self, router_id: int, **kwargs):
        super().__init__(
            router_id=router_id,
            **{k: v for k, v in kwargs.items() if hasattr(m5_GarnetRouter, k)},
        )
        self._router_id = router_id

    def get_router_id(self) -> int:
        return self._router_id
