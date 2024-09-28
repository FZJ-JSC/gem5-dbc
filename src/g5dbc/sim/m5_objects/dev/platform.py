import m5

class m5_ArmDefaultRelease(m5.objects.ArmDefaultRelease):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)

class m5_VExpress_GEM5_V1(m5.objects.VExpress_GEM5_V1):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)

class m5_VExpress_GEM5_V2(m5.objects.VExpress_GEM5_V2):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
