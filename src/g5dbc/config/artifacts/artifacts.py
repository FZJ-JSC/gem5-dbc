from dataclasses import dataclass, field
from enum import Enum

class ArchType(Enum):
    arm64 = 1

class BinaryType(Enum):
    GEM5   = 1
    DISK   = 2
    BOOT   = 3
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

@dataclass
class ArtifactList:
    path: str
    arch: dict[str, list[BinaryArtifact]] = field(default_factory=dict)
    default_arch = "arm64"
    def __post_init__(self):
        for name, items in self.arch.items():
            arch_type = ArchType[name]
            self.arch[arch_type.name] = [BinaryArtifact(**a) for a in items ]

    def search_type(self, typename: str, arch_name: str|None = None) -> dict[str,BinaryArtifact]:
        arch_name = self.default_arch if arch_name is None else arch_name
        artifacts = self.arch[arch_name]
        return dict([(a.name,a) for a in artifacts if a.bintype == typename])
