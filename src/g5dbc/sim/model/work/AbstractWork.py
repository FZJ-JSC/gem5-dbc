from abc import ABC, ABCMeta, abstractmethod


class AbstractWork:

    __metaclass__ = ABCMeta

    @abstractmethod
    def get_bootloader(self, version: str) -> str:
        """Get bootloader

        Args:
            version (str): Bootloader version

        Returns:
            str: Bootloader file path
        """

    @abstractmethod
    def get_work_script(self) -> str:
        """Get workload script to execute

        Returns:
            str: File path of script to execute
        """

    @abstractmethod
    def get_dtb_file(self) -> str | None:
        """Get generated DTB file path (if defined)

        Returns:
            str|None: File path of generated DTB file or None if undefined
        """
