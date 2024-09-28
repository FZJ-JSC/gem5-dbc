from g5dbc.sim.m5_objects.storage import m5_CowDiskImage, m5_IdeDisk

class FileDiskImage(m5_CowDiskImage):
    def __init__(self, child_image_file: str, **kwargs):
        super().__init__(**kwargs)
        self.child.image_file = child_image_file

class CowIdeDisk(m5_IdeDisk):
    def __init__(self, child_image_file: str, **kwargs):
        super().__init__(**kwargs)
        self.image = FileDiskImage(child_image_file)
