from dataclasses import asdict, dataclass
from enum import Enum


class ArchType(Enum):
    arm64 = 1


class BinaryType(Enum):
    GEM5 = 1
    DISK = 2
    BOOT = 3
    KERNEL = 4


@dataclass
class BinaryArtifact:
    name: str
    path: str
    md5hash: str
    version: str
    bintype: str
    metadata: str = ""

    def __post_init__(self):
        bintype = BinaryType[self.bintype]
        self.bintype = bintype.name

    def to_dict(self) -> dict:
        return asdict(self)
