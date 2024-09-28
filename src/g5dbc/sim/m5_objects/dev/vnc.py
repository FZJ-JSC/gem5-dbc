import m5

class m5_VncServer(m5.objects.VncServer):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
