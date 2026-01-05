"""
Sidebar widget that displays lists of UMLSL Queries, Cars, and Roads.
"""
from PySide6.QtWidgets import QWidget, QVBoxLayout, QTabWidget
from PySide6.QtCore import Signal

from pse.umlsl_editor.src.core.dataclasses.car import Car
from pse.umlsl_editor.src.core.dataclasses.road import Road
from pse.umlsl_editor.src.core.dataclasses.umlsl_query import UMLSLQuery
from pse.umlsl_editor.src.view.sidebar.cars_list_widget import CarsListWidget
from pse.umlsl_editor.src.view.sidebar.roads_list_widget import RoadsListWidget
from pse.umlsl_editor.src.view.sidebar.queries_list_widget import QueriesListWidget


class SidebarWidget(QWidget):
    """
    Main sidebar widget containing tabbed lists for queries, cars, and roads.
    """

    def __init__(self, parent=None):
        super().__init__(parent)
        self._setup_ui()

    def _setup_ui(self):
        """Initialize the UI components."""
        # layout = QVBoxLayout(self)

        # # Create tab widget
        # self.tab_widget = QTabWidget()
        #
        # # Create list widgets for each entity type
        self.queries_list = QueriesListWidget()
        self.cars_list = CarsListWidget()
        self.roads_list = RoadsListWidget()
        #
        # # Add tabs
        # self.tab_widget.addTab(self.queries_list, "UMLSL Queries")
        # self.tab_widget.addTab(self.cars_list, "Cars")
        # self.tab_widget.addTab(self.roads_list, "Roads")
        #
        # layout.addWidget(self.tab_widget)



    # Car management methods
    def add_car(self, car: Car) -> None:
        """Add a car to the cars list."""
        self.cars_list.add_car(car)

    def remove_car(self, car: Car) -> None:
        """Remove a car from the cars list."""
        self.cars_list.remove_car(car)

    def update_car(self, car: Car) -> None:
        """Update a car in the cars list."""
        self.cars_list.update_car(car)

    # Road management methods
    def add_road(self, road: Road) -> None:
        """Add a road to the roads list."""
        self.roads_list.add_road(road)

    def remove_road(self, road: Road) -> None:
        """Remove a road from the roads list."""
        self.roads_list.remove_road(road)

    def update_road(self, road: Road) -> None:
        """Update a road in the roads list."""
        self.roads_list.update_road(road)

    # Query management methods
    def add_query(self, query: UMLSLQuery) -> None:
        """Add a UMLSL query to the queries list."""
        self.queries_list.add_query(query)

    def remove_query(self, query: UMLSLQuery) -> None:
        """Remove a UMLSL query from the queries list."""
        self.queries_list.remove_query(query)

    def update_query(self, query: UMLSLQuery) -> None:
        """Update a UMLSL query in the queries list."""
        self.queries_list.update_query(query)

