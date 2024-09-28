import m5

class CHI_Version:
    _version = {}
    @classmethod
    def getVersion(cls, tp):
        if tp not in cls._version:
            cls._version[tp] = 0
        val = cls._version[tp]
        cls._version[tp] = val + 1
        return val

class m5_Cache_Controller(m5.objects.Cache_Controller):
    def __init__(self, **kwargs):
        super().__init__(
            version = CHI_Version.getVersion(m5.objects.Cache_Controller),
            **kwargs
        )

class m5_Memory_Controller(m5.objects.Memory_Controller):
    def __init__(self, **kwargs):
        super().__init__(
            version = CHI_Version.getVersion(m5.objects.Memory_Controller),
            **kwargs
        )

class m5_MiscNode_Controller(m5.objects.MiscNode_Controller):
    def __init__(self, **kwargs):
        super().__init__(
            version = CHI_Version.getVersion(m5.objects.MiscNode_Controller),
            **kwargs
        )
