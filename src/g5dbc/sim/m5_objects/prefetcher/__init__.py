import m5


class m5_TaggedPrefetcher(m5.objects.TaggedPrefetcher):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)


class m5_StridePrefetcher(m5.objects.StridePrefetcher):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)


class m5_IndirectMemoryPrefetcher(m5.objects.IndirectMemoryPrefetcher):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)


class m5_SignaturePathPrefetcher(m5.objects.SignaturePathPrefetcher):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)


class m5_SignaturePathPrefetcherV2(m5.objects.SignaturePathPrefetcherV2):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)


class m5_AMPMPrefetcher(m5.objects.AMPMPrefetcher):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)


class m5_DCPTPrefetcher(m5.objects.DCPTPrefetcher):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)


class m5_IrregularStreamBufferPrefetcher(m5.objects.IrregularStreamBufferPrefetcher):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)


class m5_SlimAMPMPrefetcher(m5.objects.SlimAMPMPrefetcher):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)


class m5_BOPPrefetcher(m5.objects.BOPPrefetcher):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)


class m5_SmsPrefetcher(m5.objects.SmsPrefetcher):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)


class m5_SBOOEPrefetcher(m5.objects.SBOOEPrefetcher):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)


class m5_STeMSPrefetcher(m5.objects.STeMSPrefetcher):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)


class m5_PIFPrefetcher(m5.objects.PIFPrefetcher):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
