import m5

class m5_GarnetNetwork(m5.objects.GarnetNetwork):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)

class m5_GarnetRouter(m5.objects.GarnetRouter):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)

class m5_GarnetExtLink(m5.objects.GarnetExtLink):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)

class m5_GarnetIntLink(m5.objects.GarnetIntLink):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)

class m5_GarnetNetworkInterface(m5.objects.GarnetNetworkInterface):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)

class m5_NetworkBridge(m5.objects.NetworkBridge):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
