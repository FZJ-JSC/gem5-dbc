from dataclasses import asdict, dataclass


@dataclass
class MemCtrlConfig:
    number_of_TBEs: int = 256
    data_channel_size: int = 64

    def to_dict(self) -> dict:
        return asdict(self)
