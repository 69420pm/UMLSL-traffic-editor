from typing import List

from PySide6.QtCore import QModelIndex, QAbstractListModel, Qt

from pse.umlsl_editor.src.model.entities.entity import Entity


class EntityListModel(QAbstractListModel):
    EntityRole = Qt.UserRole + 1

    def __init__(self, parent=None):
        super().__init__(parent)
        self._entities: list[Entity] = []

    def rowCount(self, parent: QModelIndex = QModelIndex()) -> int:
        return len(self._entities)

    def data(self, index: QModelIndex, role: int = Qt.DisplayRole):
        if not index.isValid() or not (0 <= index.row() < len(self._entities)):
            return None

        entity = self._entities[index.row()]

        if role == self.EntityRole:
            return entity
        if role == Qt.DisplayRole:
            return entity.uid  # Basic display, can be enhanced

        return None

    def add_entity(self, entity: Entity) -> None:
        self.beginInsertRows(QModelIndex(), len(self._entities), len(self._entities))
        self._entities.append(entity)
        self.endInsertRows()

    def remove_entity(self, entity: Entity) -> None:
        for i, e in enumerate(self._entities):
            if e.uid == entity.uid:
                self.beginRemoveRows(QModelIndex(), i, i)
                self._entities.pop(i)
                self.endRemoveRows()
                break

    def update_entity(self, entity: Entity) -> None:
        for i, e in enumerate(self._entities):
            if e.uid == entity.uid:
                self._entities[i] = entity
                self.dataChanged.emit(self.index(i), self.index(i), [self.EntityRole, Qt.DisplayRole])
                break
