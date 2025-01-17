import m5


def m5_curTick():
    return m5.curTick()


def m5_simulate(*args, **kwargs):
    return m5.simulate(*args, **kwargs)


def m5_instantiate(ckpt_dir: str | None = None):
    m5.instantiate(ckpt_dir)


def m5_switchCpus(system, cpuList: list, verbose: bool = True):
    m5.switchCpus(system, cpuList, verbose)


def m5_checkpoint(ckpt_dir):
    m5.checkpoint(ckpt_dir)


def m5_MaxTick():
    return m5.MaxTick


def m5_ticks_fromSeconds(seconds):
    return m5.ticks.fromSeconds(seconds)


def m5_disableAllListeners():
    m5.disableAllListeners()


def m5_buildEnv(key: str):
    return m5.defines.buildEnv[key]


def m5_inform(message: str):
    m5.util.inform(message)


def m5_panic(message: str):
    m5.panic(message)


def m5_fatal(message: str):
    m5.fatal(message)


def m5_outdir() -> str:
    return m5.options.outdir


def m5_convert_toMemorySize(val: str):
    return m5.util.convert.toMemorySize(val)


def m5_convert_toFrequency(val: str):
    return m5.util.convert.toFrequency(val)
