import m5

class m5_PciVirtIO(m5.objects.PciVirtIO):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)

class m5_VirtIOBlock(m5.objects.VirtIOBlock):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)

class m5_VirtIO9PDiod(m5.objects.VirtIO9PDiod):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
