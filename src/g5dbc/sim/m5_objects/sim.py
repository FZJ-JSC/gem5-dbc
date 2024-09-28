import m5

class m5_Root(m5.objects.Root):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)

class m5_SubSystem(m5.objects.SubSystem):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
