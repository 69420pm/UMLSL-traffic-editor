from abc import abstractmethod, ABC

from PySide6.QtCore import QAbstractListModel, Qt, QModelIndex, Slot

from pse.umlsl_editor.src.model.entities.entity import Entity

class EntityModel(QAbstractListModel):
    def __init__(self,entities: list[Entity]):
        super().__init__()
        self._data = entities or []

    def add_entity(self, entity):
        if entity not in self._data:
            self.beginInsertRows(QModelIndex(), len(self._data), len(self._data))
            self._data.append(entity)
            self.endInsertRows()

    def remove_entity(self, entity):
        if entity in self._data:
            row = self._data.index(entity)
            self.beginRemoveRows(QModelIndex(), row, row)
            self._data.remove(entity)
            self.endRemoveRows()

    def update_entity(self, entity):
        if entity in self._data:
            row = self._data.index(entity)
            index = self.index(row)
            self.dataChanged.emit(index, index, self.roleNames().keys())

    @Slot(int)
    def handle_button_click(self, row):
        pass