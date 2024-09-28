from ..config import Config
from .driver import SimulationDriver
from .factory.board  import BoardFactory
from .factory.cpu    import ProcessorFactory
from .factory.interconnect import InterconnectFactory
from .factory.memory import MemSystemFactory

def simulate(config: Config) -> int:

    system = (
        BoardFactory
        .create(config)
        .connect_processor(ProcessorFactory.create(config))
        .connect_memory(MemSystemFactory.create(config))
        .connect_interconnect(InterconnectFactory.create(config))
    )

    simulation = SimulationDriver(config=config, system=system)

    simulation.run()
    
    return 0
