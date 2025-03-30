import m5


class m5_TaggedPrefetcher(m5.objects.TaggedPrefetcher):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)


class m5_StridePrefetcher(m5.objects.StridePrefetcher):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
