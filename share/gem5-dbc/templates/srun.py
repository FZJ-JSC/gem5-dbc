#!/usr/bin/python3
import sys
import sysconfig

sys.path.append(sysconfig.get_path("purelib", "posix_user"))
if __name__ == "__m5_main__":
    from g5dbc.sim import srun

    sys.exit(srun())
