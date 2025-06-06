import m5


class m5_ArmSystem(m5.objects.ArmSystem):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)

        self.release = m5.objects.ArmDefaultRelease()


class m5_ArmFsLinux(m5.objects.ArmFsLinux):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
