# UMLSL Traffic Editor - Architecture Documentation

## Overview

This document describes the high-level architecture of the sidebar and canvas implementation for the UMLSL Traffic Editor using PySide6 and the Model-View-Controller (MVC) pattern with signal-based communication.

## Architecture Pattern: MVC with Signals

### Signal Flow Architecture

```
TrafficSnapshot (Model)
    ↓ (emits signals)
ApplicationController
    ↓ (forwards to view)
MainWindow (View)
    ├─→ Sidebar (displays lists)
    └─→ Canvas (displays graphics)
```

### Key Components

## 1. Model Layer: TrafficSnapshot

**Location**: `pse/umlsl_editor/src/core/traffic_snapshot.py`

The model is the single source of truth and emits PySide signals when data changes:

```python
class TrafficSnapshot(QObject):
    # Signals emitted when entities change
    car_added = Signal(Car)
    car_removed = Signal(Car)
    car_updated = Signal(Car)
    
    road_added = Signal(Road)
    road_removed = Signal(Road)
    road_updated = Signal(Road)
    
    crossing_segment_added = Signal(CrossingSegment)
    crossing_segment_removed = Signal(CrossingSegment)
    crossing_segment_updated = Signal(CrossingSegment)
```

**Observable Collections**: Uses `ObservableDict` and `ObservableList` to automatically emit signals when data is modified.

## 2. Controller Layer: ApplicationController

**Location**: `pse/umlsl_editor/src/controllers/application_controller.py`

Connects model signals to view methods:

```python
def _setup_event_listeners(self):
    # Connect model signals to controller handlers
    self.traffic_snapshot.car_added.connect(self._on_car_added)
    self.traffic_snapshot.road_added.connect(self._on_road_added)
    # ... etc
    
def _on_car_added(self, car_data: Car):
    # Forward to view
    self.view.add_car_view(car_data)
```

**Responsibilities**:
- Wire up signal connections
- Handle command execution
- Coordinate between model and view

## 3. View Layer

### 3.1 MainWindow

**Location**: `pse/umlsl_editor/src/view/main_window.py`

The main application window that contains both sidebar and canvas:

```python
class MainWindow(QMainWindow, TrafficView):
    def __init__(self):
        # Create scene and canvas
        self.scene = TrafficScene()
        self.canvas_view = TrafficCanvasView(self.scene)
        
        # Create sidebar
        self.sidebar = SidebarWidget()
        
        # Use QSplitter for resizable layout
        splitter = QSplitter(Qt.Horizontal)
        splitter.addWidget(self.sidebar)
        splitter.addWidget(self.canvas_view)
```

**Layout**:
```
┌─────────────────────────────────────────┐
│        MainWindow (QMainWindow)         │
├───────────┬─────────────────────────────┤
│  Sidebar  │        Canvas               │
│  (300px)  │    (Zoomable/Pannable)      │
│           │                             │
│  ┌─────┐  │   ┌──────────────────┐      │
│  │Query│  │   │  Roads (gray)    │      │
│  │Cars │  │   │  ├─ Lane lines   │      │
│  │Roads│  │   │  └─ Width by lanes│     │
│  └─────┘  │   │                  │      │
│           │   │  Cars (colored)  │      │
│           │   │  └─ Rectangle    │      │
│           │   │                  │      │
│           │   │  Crossings (○)   │      │
│           │   └──────────────────┘      │
└───────────┴─────────────────────────────┘
```

### 3.2 Sidebar Components

#### SidebarWidget
**Location**: `pse/umlsl_editor/src/view/sidebar/sidebar_widget.py`

Main sidebar container with tabbed interface:

```python
class SidebarWidget(QWidget):
    # Signals for user interactions
    car_selected = Signal(Car)
    road_selected = Signal(Road)
    query_selected = Signal(UMLSLQuery)
    
    def __init__(self):
        # Create tab widget with 3 tabs
        self.queries_list = QueriesListWidget()
        self.cars_list = CarsListWidget()
        self.roads_list = RoadsListWidget()
```

**Features**:
- Tab-based organization (Queries, Cars, Roads)
- Responds to model changes via methods called by controller
- Emits signals when user selects items

#### CarsListWidget
**Location**: `pse/umlsl_editor/src/view/sidebar/cars_list_widget.py`

Displays list of cars with key properties:

```python
def _format_car_text(self, car: Car) -> str:
    return f"{car.name} - Lane {car.lane.lane_index} ({car.lane.lane_direction.value}) - {car.velocity:.1f} m/s"
```

**Displayed Properties**:
- Car name
- Current lane (index and direction)
- Velocity

#### RoadsListWidget
**Location**: `pse/umlsl_editor/src/view/sidebar/roads_list_widget.py`

Displays list of roads with key properties:

```python
def _format_road_text(self, road: Road) -> str:
    lanes_info = f"{road.forward_lanes}↑ {road.backward_lanes}↓"
    orientation = "H" if road.orientation.value == "horizontal" else "V"
    return f"{road.name} - {lanes_info} - {orientation} @ {road.position:.1f}"
```

**Displayed Properties**:
- Road name
- Lane counts (forward/backward)
- Orientation (H/V)
- Position coordinate

#### QueriesListWidget
**Location**: `pse/umlsl_editor/src/view/sidebar/queries_list_widget.py`

Displays list of UMLSL queries:

```python
def _format_query_text(self, query: UMLSLQuery) -> str:
    status = "✓" if query.validation else "✗"
    latex_preview = query.latex[:40] + "..." if len(query.latex) > 40 else query.latex
    return f"{status} {query.assigned_car.name}: {latex_preview}"
```

**Displayed Properties**:
- Validation status (✓/✗)
- Assigned car name
- LaTeX query preview (truncated)

### 3.3 Canvas Components

#### TrafficCanvasView
**Location**: `pse/umlsl_editor/src/view/canvas/traffic_view.py`

Custom `QGraphicsView` with zoom and pan capabilities:

```python
class TrafficCanvasView(QGraphicsView):
    def wheelEvent(self, event):
        # Mouse wheel zooms in/out
        if delta > 0:
            self.scale(1.15, 1.15)  # Zoom in
        else:
            self.scale(1/1.15, 1/1.15)  # Zoom out
    
    def mousePressEvent(self, event):
        # Middle mouse button starts panning
        if event.button() == Qt.MiddleButton:
            self._is_panning = True
    
    def mouseMoveEvent(self, event):
        # Pan the view by moving scrollbars
        if self._is_panning:
            # Update scroll positions
```

**Features**:
- **Zoom**: Mouse wheel to zoom in/out (factor: 1.15)
- **Pan**: Middle mouse button drag to pan
- **Anchor**: Zoom anchored under mouse cursor
- **Anti-aliasing**: Smooth rendering enabled

#### TrafficScene
**Location**: `pse/umlsl_editor/src/view/canvas/traffic_scene.py`

Custom `QGraphicsScene` that manages graphical items:

```python
class TrafficScene(QGraphicsScene):
    def __init__(self):
        # Store mappings from data to graphics items
        self._car_items = {}  # car.name -> QGraphicsItem
        self._road_items = {}  # road.name -> QGraphicsItem
        self._crossing_items = {}  # crossing_id -> QGraphicsItem
```

**Visual Representation**:

1. **Cars** (QGraphicsRectItem):
   - Colored rectangles based on `car.color`
   - Size: `car.length * 10` × 20 pixels
   - Position calculated from lane and position_on_lane
   - Black border (1px)

2. **Roads** (QGraphicsRectItem):
   - Gray rectangles (RGB: 80, 80, 80)
   - Width: `(forward_lanes + backward_lanes) * 30` pixels
   - Length: 2000 pixels (roads are infinite, this is viewport segment)
   - Positioned based on orientation:
     - Horizontal: extends along X-axis at Y = position
     - Vertical: extends along Y-axis at X = position
   - White border (2px)

3. **Crossing Segments** (QGraphicsEllipseItem):
   - Ellipse/circle shape (50×50 pixels)
   - Semi-transparent brown (RGB: 200, 150, 100, α: 180)
   - Centered at crossing.position
   - Dark gray border (2px)

## Signal Flow Examples

### Example 1: Adding a Car

```
1. User executes command → ApplicationController.add_car()
2. Controller creates AddCarCommand
3. Command modifies TrafficSnapshot._cars (ObservableDict)
4. ObservableDict.__setitem__ triggers callback
5. TrafficSnapshot.car_added signal emits with Car object
6. ApplicationController._on_car_added() receives signal
7. Controller calls view.add_car_view(car)
8. MainWindow.add_car_view() calls:
   - scene.add_car_item(car)  → Canvas shows rectangle
   - sidebar.add_car(car)      → Sidebar shows list item
```

### Example 2: Updating a Car Position

```
1. Command modifies car.position_on_lane
2. ObservableDict update triggers callback
3. TrafficSnapshot.car_updated signal emits
4. Controller forwards to view.update_car_view()
5. Scene updates graphics item position
6. Sidebar updates list item text
```

### Example 3: User Selects Car in Sidebar

```
1. User clicks car in sidebar list
2. CarsListWidget.car_selected signal emits
3. SidebarWidget forwards to car_selected signal
4. MainWindow/Controller can connect to this signal to:
   - Highlight car in canvas
   - Show details panel
   - Enable edit/delete actions
```

## Data Flow Patterns

### One-Way Data Flow
```
Model (TrafficSnapshot)
  ↓ signals only
Controller
  ↓ method calls only
View (MainWindow, Sidebar, Canvas)
  ↓ user interaction signals
Controller
  ↓ commands
Model
```

### Separation of Concerns

1. **Model** (TrafficSnapshot):
   - Knows: Data structure, validation rules, business logic
   - Doesn't know: How data is displayed, Qt widgets

2. **View** (MainWindow, Sidebar, Canvas):
   - Knows: How to display data, Qt widgets, user interactions
   - Doesn't know: Business logic, validation, where data comes from

3. **Controller** (ApplicationController):
   - Knows: How to connect model and view
   - Doesn't know: Internal details of model or view

## Extension Points

### Adding New Entity Types

To add a new entity type (e.g., TrafficLight):

1. Add signals to TrafficSnapshot:
```python
traffic_light_added = Signal(TrafficLight)
traffic_light_removed = Signal(TrafficLight)
traffic_light_updated = Signal(TrafficLight)
```

2. Connect signals in ApplicationController:
```python
self.traffic_snapshot.traffic_light_added.connect(self._on_traffic_light_added)
```

3. Add view methods to MainWindow:
```python
def add_traffic_light_view(self, light: TrafficLight):
    self.scene.add_traffic_light_item(light)
    self.sidebar.add_traffic_light(light)
```

4. Implement graphics in TrafficScene and list widget in Sidebar

### Adding Custom Graphics Items

For more complex graphics (e.g., custom car shape), create custom QGraphicsItem subclasses:

```python
class CarGraphicsItem(QGraphicsItem):
    def __init__(self, car: Car):
        self.car = car
    
    def paint(self, painter, option, widget):
        # Custom drawing code
        painter.drawPolygon(...)  # Draw car shape
    
    def boundingRect(self):
        return QRectF(0, 0, self.car.length * 10, 20)
```

### Adding Interactions

To handle clicks on canvas items:

```python
class TrafficScene(QGraphicsScene):
    entity_clicked = Signal(object)  # Emit clicked entity
    
    def mousePressEvent(self, event):
        item = self.itemAt(event.scenePos(), QTransform())
        if item and hasattr(item, 'entity_data'):
            self.entity_clicked.emit(item.entity_data)
```

## Benefits of This Architecture

1. **Loose Coupling**: Model, View, Controller are independent
2. **Testability**: Each component can be tested in isolation
3. **Maintainability**: Changes to one layer don't affect others
4. **Extensibility**: Easy to add new entity types or views
5. **Signal-Based**: Non-blocking, event-driven updates
6. **Type Safety**: Strong typing with dataclasses
7. **Scalability**: Can handle many entities efficiently

## Implementation Notes

### ObservableDict and ObservableList

Currently not implemented (raise NotImplementedError), but when implemented will:
- Wrap standard Python dict/list
- Call callbacks on modifications
- Enable automatic signal emission

### Position Calculations

Car positions need proper calculation based on:
- Road geometry (orientation, position)
- Lane index and direction
- Position on lane
- Transition value (for lane changes)

Current implementation uses simplified positioning - this should be enhanced with proper coordinate transformation.

### Performance Considerations

For large numbers of entities:
- Use QGraphicsItem caching
- Implement level-of-detail (LOD) rendering
- Only update visible items
- Use spatial indexing for collision detection

## Future Enhancements

1. **Context Menus**: Right-click on items for actions
2. **Selection Model**: Multi-select entities
3. **Drag-and-Drop**: Move cars/roads by dragging
4. **Property Panels**: Detail view for selected entity
5. **Grid/Snap**: Snap roads to grid
6. **Layers**: Toggle visibility of different entity types
7. **Animation**: Smooth transitions for updates
8. **Undo/Redo Integration**: Visual feedback for command stack

