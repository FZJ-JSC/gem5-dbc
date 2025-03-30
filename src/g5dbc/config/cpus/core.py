from dataclasses import asdict, dataclass, field


@dataclass
class CoreOpDesc:
    name: str
    latency: int = 1
    pipelined: bool = True


@dataclass
class CoreFUDesc:
    count: int = 0
    ops: list[CoreOpDesc] = field(default_factory=list)

    def __post_init__(self):
        for n, op in enumerate(self.ops):
            if isinstance(op, dict):
                self.ops[n] = CoreOpDesc(**op)
            if isinstance(op, list):
                args = dict(
                    name=op[0],
                    latency=1 if len(op) < 2 else op[1],
                    pipelined=True if len(op) < 3 else op[2],
                )
                self.ops[n] = CoreOpDesc(**args)


@dataclass
class CoreConfig:
    fetchBufferSize: int = 64
    fetchQueueSize: int = 64
    cacheStorePorts: int = 200
    cacheLoadPorts: int = 200
    LSQDepCheckShift: int = 0
    LSQCheckLoads: bool = True
    LFSTSize: int = 1024
    SSITSize: int = 1024
    LQEntries: int = 128
    SQEntries: int = 128
    numIQEntries: int = 128
    numPhysIntRegs: int = 256
    numPhysFloatRegs: int = 256
    numPhysVecPredRegs: int = 64
    numPhysVecRegs: int = 364
    numPhysMatRegs: int = 2
    numPhysCCRegs: int = 0
    numROBEntries: int = 512
    fetchWidth: int = 8
    decodeWidth: int = 8
    renameWidth: int = 8
    dispatchWidth: int = 16
    issueWidth: int = 16
    wbWidth: int = 8
    commitWidth: int = 16
    squashWidth: int = 8
    fetchToDecodeDelay: int = 1
    decodeToFetchDelay: int = 1
    decodeToRenameDelay: int = 1
    renameToFetchDelay: int = 1
    renameToDecodeDelay: int = 1
    renameToIEWDelay: int = 1
    renameToROBDelay: int = 1
    iewToFetchDelay: int = 1
    iewToDecodeDelay: int = 1
    iewToRenameDelay: int = 1
    iewToCommitDelay: int = 1
    commitToFetchDelay: int = 1
    commitToDecodeDelay: int = 1
    commitToRenameDelay: int = 1
    commitToIEWDelay: int = 1
    issueToExecuteDelay: int = 1
    backComSize: int = 32
    forwardComSize: int = 32
    trapLatency: int = 13
    fetchTrapLatency: int = 1
    store_set_clear_period: int = 250000
    numRobs: int = 1
    needsTSO: bool = False

    def to_dict(self) -> dict:
        return asdict(self)
