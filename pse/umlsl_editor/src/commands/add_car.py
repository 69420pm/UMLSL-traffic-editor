from pse.umlsl_editor.src.commands.command import Command, ReturnValue
from pse.umlsl_editor.src.core.dataclasses.car import Car
from pse.umlsl_editor.src.core.traffic_snapshot_reader import TrafficSnapshotReader
from pse.umlsl_editor.src.core.traffic_snapshot_writer import TrafficSnapshotWriter


class AddCarCommand(Command[bool]):

    def __init__(self, car: Car, traffic_snapshot_reader: TrafficSnapshotReader, traffic_snapshot_writer: TrafficSnapshotWriter):
        self.car = car
        self.traffic_snapshot_writer = traffic_snapshot_writer
        self.traffic_snapshot_reader = traffic_snapshot_reader

    def execute(self) -> bool:
        pass