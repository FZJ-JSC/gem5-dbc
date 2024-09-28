import m5

class m5_L2XBar(m5.objects.L2XBar):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)

class m5_SnoopFilter(m5.objects.SnoopFilter):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)

class m5_Cache(m5.objects.Cache):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)

        # Set prefetcher NULL by default
        self.prefetcher = m5.objects.NULL
