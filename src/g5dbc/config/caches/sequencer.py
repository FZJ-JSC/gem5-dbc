from dataclasses import dataclass

@dataclass
class Sequencer:
    max_outstanding_requests: int = 256
