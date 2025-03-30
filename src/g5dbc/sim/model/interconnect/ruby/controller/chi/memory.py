import math

from g5dbc.config.memory.controller import MemCtrlConfig
from g5dbc.sim.m5_objects import m5_AddrRange
from g5dbc.sim.m5_objects.ruby import m5_RubySystem
from g5dbc.sim.m5_objects.ruby.chi import m5_CHI_Memory_Controller
from g5dbc.sim.m5_objects.ruby.message import TriggerMessageBuffer, m5_MessageBuffer

from ...Sequencer import Sequencer
from ..AbstractController import AbstractController


class MemController(m5_CHI_Memory_Controller, AbstractController):
    """
    CHI Memory Controller
    """

    def __init__(self, config: MemCtrlConfig, ruby_system: m5_RubySystem):

        super().__init__(**config.to_dict())
        self.ruby_system = ruby_system

        self.triggerQueue = TriggerMessageBuffer()
        self.responseFromMemory = m5_MessageBuffer()
        self.requestToMemory = m5_MessageBuffer(ordered=True)
        self.reqRdy = TriggerMessageBuffer()

    def connect_network(self, network) -> None:
        """
        Connect CHI input/output ports to network
        """

        self.reqOut = m5_MessageBuffer()
        self.rspOut = m5_MessageBuffer()
        self.snpOut = m5_MessageBuffer()
        self.datOut = m5_MessageBuffer()
        self.reqIn = m5_MessageBuffer()
        self.rspIn = m5_MessageBuffer()
        self.snpIn = m5_MessageBuffer()
        self.datIn = m5_MessageBuffer()

        self.reqOut.out_port = network.in_port
        self.rspOut.out_port = network.in_port
        self.snpOut.out_port = network.in_port
        self.datOut.out_port = network.in_port
        self.reqIn.in_port = network.out_port
        self.rspIn.in_port = network.out_port
        self.snpIn.in_port = network.out_port
        self.datIn.in_port = network.out_port

    def connect_sequencer(self, sequencer: Sequencer, dcache: bool) -> None:
        raise NotImplementedError()

    def set_addr_ranges(self, addr_ranges: list[m5_AddrRange]) -> None:
        self.addr_ranges = addr_ranges

    def set_downstream(self, cntrls: list[AbstractController]) -> None:
        raise NotImplementedError()
