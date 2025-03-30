import m5


class m5_MemCtrl(m5.objects.MemCtrl):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)


class m5_DRAMInterface(m5.objects.DRAMInterface):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)

    def get_device_size(self) -> int:
        return (
            self.device_size.value
            * self.devices_per_rank.value
            * self.ranks_per_channel.value
        )

    def get_rowbuffer_size(self) -> int:
        return self.device_rowbuffer_size.value * self.devices_per_rank.value

    def get_addr_mapping(self) -> str:
        return self.addr_mapping.value


class m5_SimpleMemory(m5.objects.SimpleMemory):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
