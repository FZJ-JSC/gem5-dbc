import m5

class m5_ArmO3CPU(m5.objects.ArmO3CPU):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)

class m5_AtomicSimpleCPU(m5.objects.AtomicSimpleCPU):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)

class m5_TimingSimpleCPU(m5.objects.TimingSimpleCPU):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)

class m5_OpDesc(m5.objects.OpDesc):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)

class m5_FUDesc(m5.objects.FUDesc):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)

class m5_FUPool(m5.objects.FUPool):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
