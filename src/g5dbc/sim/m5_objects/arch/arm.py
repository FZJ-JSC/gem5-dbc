import m5

from pathlib import Path

class m5_ArmSystem(m5.objects.ArmSystem):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)

        self.release = m5.objects.ArmDefaultRelease()

class m5_ArmFsLinux(m5.objects.ArmFsLinux):
    def __init__(self, output_dir: str, command_line: str, kernel_path: str, **kwargs):
        super().__init__(**kwargs)

        self.dtb_filename = Path(output_dir).joinpath("system.dtb")
        self.machine_type = "DTOnly"
        self.command_line = command_line
        self.object_file  = kernel_path
