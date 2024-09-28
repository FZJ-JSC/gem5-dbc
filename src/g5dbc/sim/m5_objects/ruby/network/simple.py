import m5

class m5_SimpleNetwork(m5.objects.SimpleNetwork):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)

class m5_Switch(m5.objects.Switch):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)

class m5_SimpleExtLink(m5.objects.SimpleExtLink):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)

class m5_SimpleIntLink(m5.objects.SimpleIntLink):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
