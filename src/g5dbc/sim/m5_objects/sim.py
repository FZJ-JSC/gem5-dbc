import m5
from m5.objects import Process, SEWorkload


def find_SEWorkload(path: str):
    return SEWorkload.init_compatible(path)


class m5_System(m5.objects.System):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)


class m5_Root(m5.objects.Root):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)


class m5_SubSystem(m5.objects.SubSystem):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)


class m5_Process(m5.objects.Process):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
