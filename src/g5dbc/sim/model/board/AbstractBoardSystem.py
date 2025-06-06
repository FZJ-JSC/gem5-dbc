from __future__ import annotations

from abc import ABC, ABCMeta, abstractmethod

from g5dbc.sim.model.cpu import AbstractProcessor
from g5dbc.sim.model.cpu.AbstractCore import AbstractCore
from g5dbc.sim.model.interconnect import CoherentInterconnect
from g5dbc.sim.model.memory import AbstractMemSystem
from g5dbc.sim.model.work import AbstractWork


class AbstractBoardSystem:
    """Abstract System Board"""

    __metaclass__ = ABCMeta

    @abstractmethod
    def connect_processor(self, processor: AbstractProcessor) -> AbstractBoardSystem:
        """Connect processor to system board

        Args:
            processor (AbstractProcessor): Processor instance to connect

        Returns:
            AbstractBoardSystem: Self instance for method chaining
        """

    @abstractmethod
    def connect_memory(self, memory: AbstractMemSystem) -> AbstractBoardSystem:
        """Connect memory system to system board

        Args:
            memory (AbstractMemSystem): Memory system to connect

        Returns:
            AbstractBoardSystem: Self instance for method chaining
        """

    @abstractmethod
    def connect_interconnect(self, ic: CoherentInterconnect) -> AbstractBoardSystem:
        """Configure system board interconnect

        Args:
            ic (CoherentInterconnect): Interconnect instance to configure

        Returns:
            AbstractBoardSystem: Self instance for method chaining
        """

    @abstractmethod
    def get_board_procesor(self) -> AbstractProcessor:
        """Get system board processor

        Returns:
            AbstractProcessor: Processor instance
        """

    @abstractmethod
    def assign_workload(self, work: AbstractWork) -> AbstractBoardSystem:
        """Assign workload

        Args:
            work (AbstractWork): Workload to assign

        Returns:
            AbstractBoardSystem: Self instance for method chaining
        """

    def switch_cpus(self) -> list[tuple[AbstractCore, AbstractCore]]:
        """Return a list of current and next core tuples to switch

        Returns:
            list[tuple[AbstractCore, AbstractCore]]: A list of current and next core tuples
        """
        processor = self.get_board_procesor()
        return processor.switch_next()
