from dataclasses import dataclass


@dataclass
class SequencerConf:
    max_outstanding_requests: int = 256
