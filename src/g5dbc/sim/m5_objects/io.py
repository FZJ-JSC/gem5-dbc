import m5

class m5_IOXBar(m5.objects.IOXBar):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)

class m5_Bridge(m5.objects.Bridge):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)

class m5_SystemXBar(m5.objects.SystemXBar):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)

class m5_BadAddr(m5.objects.BadAddr):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
