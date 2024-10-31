from modules.system.system import EPISystem
from modules.system.system_se import EPISystemSE

def System(options):
    init_system = EPISystem(options) if options.simulation.fs_mode else EPISystemSE(options)
    return init_system

#from modules.system.options import add_options