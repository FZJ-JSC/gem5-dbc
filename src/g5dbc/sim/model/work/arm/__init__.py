from pathlib import Path

from g5dbc.config import Config
from g5dbc.sim.m5_objects.arch import m5_ArmFsLinux

from ..AbstractWork import AbstractWork


class ArmLinuxWorkload(m5_ArmFsLinux, AbstractWork):
    def __init__(self, config: Config):

        output_dir = Path(config.simulation.output_dir)
        dtb_filename = str(output_dir.joinpath("system.dtb"))
        work_script = str(output_dir.joinpath(config.simulation.work_script))

        disk_images = config.search_artifacts("DISK")
        if not disk_images:
            raise ValueError(f"Disk image list empty.")

        kernels = config.search_artifacts(
            "KERNEL",
            name=config.simulation.linux_binary,
            version=config.simulation.linux_version,
        )
        if not kernels:
            raise ValueError(f"Linux Kernel list empty.")

        # Assume first disk in list to be root disk
        super().__init__(
            dtb_filename=dtb_filename,
            command_line=f"{kernels[0].metadata} root={disk_images[0].metadata}",
            object_file=kernels[0].path,
            machine_type="DTOnly",
        )

        self._bootloaders = dict(
            [
                (b.version, b)
                for b in config.search_artifacts(
                    "BOOT",
                    name=config.simulation.bootloader_binary,
                )
            ]
        )
        self._dtb_file = dtb_filename
        self._script = work_script

    def get_bootloader(self, version: str) -> str:
        return self._bootloaders[version].path

    def get_work_script(self) -> str:
        return self._script

    def get_dtb_file(self) -> str:
        return self._dtb_file
