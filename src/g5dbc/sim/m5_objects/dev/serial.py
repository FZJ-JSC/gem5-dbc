import m5

class m5_Terminal(m5.objects.Terminal):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
