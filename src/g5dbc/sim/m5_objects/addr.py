import m5

class m5_AddrRange(m5.objects.AddrRange):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

class m5_Addr(m5.objects.Addr):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
