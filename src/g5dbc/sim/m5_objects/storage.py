import m5

class m5_CowDiskImage(m5.objects.CowDiskImage):
    def __init__(self, **kwargs):
        super(m5_CowDiskImage, self).__init__(**kwargs)

class m5_IdeDisk(m5.objects.IdeDisk):
    def __init__(self, **kwargs):
        super(m5_IdeDisk, self).__init__(**kwargs)

class m5_RedirectPath(m5.objects.RedirectPath):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
