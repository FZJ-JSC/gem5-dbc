import m5
import os, sys

from modules.system import System
from modules.options import Options
from modules.simulation import Simulation

if m5.defines.buildEnv['TARGET_ISA'] != "arm":
    print("Error: Target ISA must be ARM")
    sys.exit(1)

options = Options()

if options.disable_listeners:
    print("Disabling Listeners")
    m5.disableAllListeners()

init_system = System(options)

root = m5.objects.Root(system=init_system, full_system=options.simulation.fs_mode) 

if options.simulation.fs_mode:
    if options.simulation.timesync:
        root.time_sync_enable = True

    if not options.bare_metal and not options.dtb_filename:
        if options.architecture.system.model not in [
                                    "VExpress_GEM5",
                                    "VExpress_GEM5_V1",
                                    "VExpress_GEM5_V2",
                                    "VExpress_GEM5_Foundation"]:
            print("Can only correctly generate a dtb for VExpress_GEM5")
            sys.exit(1)
        root.system.workload.dtb_filename = os.path.join(m5.options.outdir, '%s.dtb' % "system")
        root.system.generateDtb(root.system.workload.dtb_filename)


Simulation(root, init_system, options)

sys.exit(0)
