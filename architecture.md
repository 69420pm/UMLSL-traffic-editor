# UMLSL Traffic Editor – Software Architecture Documentation

## Table of Contents

1. [Overview](#overview)
2. [Architectural Goals and Constraints](#architectural-goals-and-constraints)
3. [High-Level Layered Architecture](#high-level-layered-architecture)
4. [Controller Layer](#controller-layer)
   - [ApplicationController (Facade Pattern)](#applicationcontroller-facade-pattern)
   - [CommandController](#commandcontroller)
   - [EventController](#eventcontroller)
   - [DataController](#datacontroller)
5. [Core Layer](#core-layer)
   - [Interface Segregation: Reader/Writer Pattern](#interface-segregation-readerwriter-pattern)
   - [TrafficSnapshot as Single Source of Truth](#trafficsnapshot-as-single-source-of-truth)
   - [Observable Collections (Observer Pattern)](#observable-collections-observer-pattern)
6. [Command Layer (Command Pattern)](#command-layer-command-pattern)
   - [Command Interface](#command-interface)
   - [Command Categories](#command-categories)
   - [Undo/Redo Infrastructure](#undoredo-infrastructure)
7. [View Layer](#view-layer)
   - [Abstract View Interface](#abstract-view-interface)
   - [Concrete PySide6 Implementation](#concrete-pyside6-implementation)
   - [Qt Designer Integration](#qt-designer-integration)
8. [Signal-Based Model-to-View Binding](#signal-based-model-to-view-binding)
9. [Design Patterns Summary](#design-patterns-summary)
10. [Recommended UML Diagrams](#recommended-uml-diagrams)

---

## Overview

The UMLSL Traffic Editor is a desktop application built with Python and PySide6 (Qt for Python) for creating, editing, and visualizing traffic simulation scenarios. The application follows a layered MVC-inspired architecture with clear separation of concerns, designed for maintainability, testability, and extensibility.

The architecture emphasizes:
- **Decoupling** between the model, view, and controller layers
- **Command-based mutations** for traceable and undoable state changes
- **Signal-driven synchronization** between model and view
- **Interface segregation** for controlled access to shared state

---

## Architectural Goals and Constraints

### Goals

| Goal | Description |
|------|-------------|
| **Separation of Concerns** | Each layer has a single, well-defined responsibility. The view layer knows nothing about persistence; the model layer knows nothing about Qt widgets. |
| **Testability** | Controllers and commands can be unit tested without instantiating the GUI. The abstract `TrafficView` interface enables mock views in tests. |
| **Extensibility** | New entity types, commands, or view implementations can be added without modifying existing code. |
| **Undo/Redo Support** | The command-based architecture provides the foundation for implementing undo/redo functionality. |
| **Framework Independence** | The core domain logic is decoupled from PySide6. Only the concrete view layer and signal wiring depend on Qt. |

### Constraints

| Constraint | Rationale |
|------------|-----------|
| **PySide6 as UI Framework** | Chosen for its mature Qt ecosystem, cross-platform support, and Qt Designer integration for rapid UI prototyping. |
| **Single TrafficSnapshot Instance** | The application operates on one traffic scenario at a time. This simplifies state management and avoids multi-document complexity. |
| **Synchronous Command Execution** | Commands execute synchronously on the main thread. Asynchronous operations (e.g., file I/O) are handled at the command boundary, not within the core logic. |

---

## High-Level Layered Architecture

The application is organized into four primary layers, each with distinct responsibilities:

```
┌─────────────────────────────────────────────────────────────────────┐
│                           VIEW LAYER                                │
│  (TrafficView interface, PySide6 widgets, Qt Designer .ui files)    │
└─────────────────────────────────────────────────────────────────────┘
                                   ▲
                                   │ Signals / Method Calls
                                   ▼
┌─────────────────────────────────────────────────────────────────────┐
│                        CONTROLLER LAYER                             │
│  (ApplicationController, CommandController, EventController,       │
│   DataController)                                                   │
└─────────────────────────────────────────────────────────────────────┘
                                   ▲
                                   │ Executes Commands / Reads Data
                                   ▼
┌─────────────────────────────────────────────────────────────────────┐
│                         COMMAND LAYER                               │
│  (Command interface, concrete commands for cars, roads, etc.)       │
└─────────────────────────────────────────────────────────────────────┘
                                   ▲
                                   │ Mutates / Queries via Interfaces
                                   ▼
┌─────────────────────────────────────────────────────────────────────┐
│                          CORE LAYER                                 │
│  (Entities, Value Objects, View Models, Reader/Writer Interfaces)   │
└─────────────────────────────────────────────────────────────────────┘
```

### Layer Responsibilities

| Layer | Responsibility |
|-------|----------------|
| **View Layer** | Renders the traffic simulation, handles user input, displays modals. Has no knowledge of how data is stored or mutated. |
| **Controller Layer** | Orchestrates application flow, translates user actions into commands, wires model signals to view updates. |
| **Command Layer** | Encapsulates discrete state mutations. Each command is a self-contained, potentially reversible operation. |
| **Core Layer** | Defines the domain model (entities, value objects), provides controlled access via interfaces, and emits signals on state changes. |

### Rationale

This layered approach was chosen because:

1. **Maintainability**: Changes to the UI do not ripple into business logic. A new view implementation (e.g., a 3D renderer) can be added by implementing the `TrafficView` interface without modifying controllers or the model.

2. **Testability**: The `TrafficView` abstraction allows controllers to be tested with mock views. Commands can be tested by injecting mock reader/writer interfaces.

3. **Traceability**: All mutations flow through commands, making it easy to log, audit, or reverse changes.

---

## Controller Layer

The controller layer consists of four specialized controllers, unified under a facade.

### ApplicationController (Facade Pattern)

**Location**: `src/controllers/application_controller.py`

The `ApplicationController` is the **Facade** that provides a simplified, unified interface to the application's controller subsystem. External code (e.g., the main entry point or UI binders) interacts primarily with this single controller rather than managing multiple specialized controllers directly.

```python
class ApplicationController:
    def __init__(self, traffic_snapshot: TrafficSnapshot, view: TrafficView, settings: Settings):
        self.event_controller = EventController(...)
        self.command_controller = CommandController(...)
        self.data_controller = DataController(...)
```

#### Rationale for the Facade Pattern

| Benefit | Explanation |
|---------|-------------|
| **Simplified Interface** | Clients don't need to know which specialized controller handles which responsibility. |
| **Centralized Initialization** | All sub-controllers are instantiated and wired in one place, reducing initialization complexity. |
| **Swappable Subsystems** | The `ApplicationController` can swap out the `TrafficSnapshot` (e.g., when loading a new file) and reinitialize all sub-controllers consistently via `set_traffic_snapshot()`. |

### CommandController

**Location**: `src/controllers/command_controller.py`

The `CommandController` is responsible for:
- Executing commands that mutate the model
- Providing a high-level API for common operations (add/edit/remove cars, roads, queries)
- Managing command history for undo/redo (infrastructure prepared, not yet implemented)

```python
class CommandController:
    def __init__(self, traffic_snapshot_reader: TrafficSnapshotReader, 
                 traffic_snapshot_writer: TrafficSnapshotWriter):
        self.traffic_snapshot_reader = traffic_snapshot_reader
        self.traffic_snapshot_writer = traffic_snapshot_writer
```

#### Design Decisions

1. **Accepts Interfaces, Not Concrete Types**: The controller depends on `TrafficSnapshotReader` and `TrafficSnapshotWriter` interfaces, not the concrete `TrafficSnapshot`. This enforces controlled access and makes the controller testable with mocks.

2. **Two Execution Modes**:
   - `execute_command()`: Adds command to history (for undoable operations)
   - `execute_without_history()`: Skips history (for ephemeral operations like selection changes)

3. **High-Level API Methods**: Methods like `add_car()`, `edit_road()`, `select_car()` provide a convenient, type-safe API that internally creates and executes the appropriate command objects.

### EventController

**Location**: `src/controllers/event_controller.py`

The `EventController` is the **binding layer** that connects model signals to view methods. It implements the **Observer Pattern** by subscribing to model events and forwarding them to the view.

```python
class EventController:
    def _setup_event_listeners(self) -> None:
        # Connect Car signals directly to view methods
        self.traffic_snapshot.car_added.connect(self.view.add_car_view)
        self.traffic_snapshot.car_removed.connect(self.view.remove_car_view)
        self.traffic_snapshot.car_updated.connect(self.view.update_car_view)
        
        # Connect Road signals directly to view methods
        self.traffic_snapshot.road_added.connect(self.view.add_road_view)
        # ... and so on
```

#### Rationale

| Benefit | Explanation |
|---------|-------------|
| **Automatic View Updates** | When the model changes (e.g., a car is added), the view is automatically notified and updates itself. No manual refresh calls needed. |
| **Decoupled Model and View** | The `TrafficSnapshot` emits signals without knowing what consumes them. The view implements an interface without knowing what triggers its methods. |
| **Centralized Wiring** | All signal-to-view connections are defined in one place, making it easy to understand the data flow. |

### DataController

**Location**: `src/controllers/data_controller.py`

The `DataController` provides **read-only access** to model data for the view layer. Unlike the `EventController` (which pushes updates), the `DataController` supports **pull-based** queries.

```python
class DataController:
    def __init__(self, traffic_snapshot_reader: TrafficSnapshotReader):
        self.traffic_snapshot_reader = traffic_snapshot_reader

    def get_all_cars(self) -> list[Car]: ...
    def get_all_roads(self) -> list[Road]: ...
    def should_render_coordinate_system(self) -> bool: ...
```

#### Rationale

Some view operations require querying the current state rather than reacting to changes. For example:
- Initial view population when the application starts
- Rebuilding the view after loading a new traffic snapshot
- On-demand queries for rendering decisions (e.g., "should I render the coordinate system?")

The `DataController` complements the push-based `EventController` with pull-based data access.

---

## Core Layer

The core layer contains the domain model and provides controlled access through interfaces.

### Interface Segregation: Reader/Writer Pattern

**Locations**: 
- `src/core/traffic_snapshot_reader.py`
- `src/core/traffic_snapshot_writer.py`

The `TrafficSnapshot` model class implements two separate interfaces:

```python
class TrafficSnapshotReader(ABC):
    @abstractmethod
    def get_cars(self) -> list[Car]: ...
    @abstractmethod
    def get_roads(self) -> list[Road]: ...
    @abstractmethod
    def get_cars_on_road(self, road: Road) -> list[Car]: ...
    @abstractmethod
    def validate_lane(self, road: Road, lane_index: int, lane_direction: str) -> bool: ...

class TrafficSnapshotWriter(ABC):
    @abstractmethod
    def add_road(self, road: Road) -> None: ...
    @abstractmethod
    def remove_road(self, road_name: str) -> None: ...
    @abstractmethod
    def add_car(self, car: Car) -> None: ...
    @abstractmethod
    def remove_car(self, car_name: str) -> None: ...
```

#### Rationale for Interface Segregation

This follows the **Interface Segregation Principle (ISP)** from SOLID:

| Benefit | Explanation |
|---------|-------------|
| **Controlled Access** | Components that only need to read data receive `TrafficSnapshotReader`. They cannot accidentally mutate state. |
| **Clear Intent** | A method signature like `def __init__(self, reader: TrafficSnapshotReader)` clearly communicates that this component is read-only. |
| **Testability** | Mock implementations can be provided for each interface independently. A read-only test can use a simple mock reader without implementing write methods. |
| **Enforcement at Compile/Lint Time** | Type checkers can verify that read-only components don't call write methods. |

### TrafficSnapshot as Single Source of Truth

**Location**: `src/core/view_models/traffic_snapshot.py`

The `TrafficSnapshot` is the central model class that:
- Holds all roads, cars, crossing segments, and UMLSL queries
- Implements both `TrafficSnapshotReader` and `TrafficSnapshotWriter`
- Inherits from `QObject` to support Qt signals
- Emits signals when data changes

```python
class TrafficSnapshot(QObject, TrafficSnapshotReader, TrafficSnapshotWriter):
    car_added = Signal(Car)
    car_removed = Signal(Car)
    car_updated = Signal(Car)
    road_added = Signal(Road)
    road_removed = Signal(Road)
    road_updated = Signal(Road)
    # ... more signals
```

#### Rationale

| Decision | Rationale |
|----------|-----------|
| **Single Instance** | One traffic snapshot per application session simplifies state management. Loading a new file replaces the entire snapshot. |
| **Signal Emission** | Using Qt signals integrates naturally with PySide6 and allows multiple observers (views, validators, loggers) to react to changes. |
| **Multiple Interface Implementation** | The same object can be passed as a reader to read-only components and as a writer to mutation components, avoiding object proliferation. |

### Observable Collections (Observer Pattern)

**Location**: `src/core/helper/observables.py`

The core layer provides `ObservableDict` and `ObservableList` collections that emit callbacks when modified:

```python
class ObservableDict(MutableMapping[Key, Value]):
    def __init__(
            self,
            on_add: Optional[Callable[[Value], None]] = None,
            on_remove: Optional[Callable[[Value], None]] = None,
            on_update: Optional[Callable[[Value], None]] = None,
    ): ...
```

These collections are used internally by `TrafficSnapshot` to trigger signal emission:

```python
self._cars = ObservableDict[str, Car](
    on_add=self.car_added.emit,
    on_remove=self.car_removed.emit,
    on_update=self.car_updated.emit
)
```

#### Rationale

| Benefit | Explanation |
|---------|-------------|
| **Automatic Signal Emission** | Adding/removing items from the collection automatically emits the corresponding signal. No manual signal calls needed. |
| **Encapsulation** | The mutation logic and notification logic are bundled together, reducing the risk of forgotten notifications. |
| **Reusability** | The same observable collection pattern can be used for different entity types (cars, roads, queries). |

---

## Command Layer (Command Pattern)

All state mutations in the application are encapsulated as **Command** objects, implementing the **Command Pattern**.

### Command Interface

**Location**: `src/commands/command.py`

```python
class Command(ABC, Generic[ReturnValue]):
    @abstractmethod
    def execute(self) -> ReturnValue:
        """Executes the command and returns a value of type ReturnValue."""
        raise NotImplementedError()

class CommandValidationError(ValueError):
    """Exception raised when a command fails validation."""
    pass
```

#### Design Decisions

1. **Generic Return Type**: Commands can return values (e.g., the created entity's ID) or `None` for void operations.

2. **Validation via Exception**: Commands validate their preconditions and raise `CommandValidationError` if they cannot execute. This separates validation from execution.

3. **Self-Contained**: Each command encapsulates all data needed for execution. Commands receive references to reader/writer interfaces, not the entire application state.

### Command Categories

Commands are organized by domain concern:

| Category | Commands | Purpose |
|----------|----------|---------|
| **Cars** | `AddCarCommand`, `EditCarCommand`, `DeleteCarCommand` | CRUD operations for car entities |
| **Roads** | `AddRoadCommand`, `EditRoadCommand`, `DeleteRoadCommand` | CRUD operations for road entities |
| **UMLSL** | `AddUMLSLQueryCommand`, `EditUMLSLQueryCommand`, `DeleteUMLSLQueryCommand` | CRUD operations for UMLSL queries |
| **Selection** | `SelectCarCommand`, `DeselectCarCommand`, `SelectRoadCommand`, `DeselectRoadCommand`, `ClearSelectionCommand` | UI selection state management |
| **Settings** | `ChangeBreakingAccelerationCommand`, `ToggleCoordinateSystemCommand`, `ToggleSafetyDistanceCommand` | Application settings |
| **Persistence** | `LoadTrafficSnapshotCommand`, `SaveTrafficSnapshotCommand`, `SaveAsTrafficSnapshotCommand` | File I/O operations |

#### Example Command Structure

```python
class AddCarCommand(Command[None]):
    def __init__(
        self,
        traffic_snapshot_reader: TrafficSnapshotReader,
        traffic_snapshot_writer: TrafficSnapshotWriter,
        car_params: CarParams
    ):
        self.traffic_snapshot_writer = traffic_snapshot_writer
        self.traffic_snapshot_reader = traffic_snapshot_reader
        self.car_params = car_params

    def execute(self) -> None:
        # Validate, create Car, add to snapshot
        ...
```

### Rationale for Command Pattern

| Benefit | Explanation |
|---------|-------------|
| **Undo/Redo Ready** | Each command can implement an `undo()` method. The `CommandController` maintains a history stack for navigation. |
| **Logging/Auditing** | All mutations pass through commands, making it easy to log every state change. |
| **Testability** | Commands are simple objects that can be instantiated and executed in isolation during tests. |
| **Transactional Semantics** | A command either fully succeeds or fails with an exception. Partial mutations are avoided. |
| **Decoupling** | UI code creates command objects and passes them to the controller. It doesn't directly manipulate the model. |

### Undo/Redo Infrastructure

The `CommandController` includes commented-out infrastructure for undo/redo:

```python
# self._command_history = []  # TODO: Implement undo/redo stack
# self._history_position = -1  # Current position in history

# def undo(self) -> bool: ...
# def redo(self) -> bool: ...
# def can_undo(self) -> bool: ...
# def can_redo(self) -> bool: ...
```

The distinction between `execute_command()` (with history) and `execute_without_history()` (without history) prepares for this feature. Selection changes, for example, should not be undoable and use `execute_without_history()`.

---

## View Layer

The view layer follows the **Dependency Inversion Principle**: high-level modules (controllers) depend on abstractions (interfaces), not concretions (Qt widgets).

### Abstract View Interface

**Location**: `src/view/traffic_view.py`

```python
class TrafficView(ABC):
    @abstractmethod
    def initialize_view(self) -> None: ...
    
    @abstractmethod
    def add_car_view(self, car_data: Car) -> None: ...
    
    @abstractmethod
    def remove_car_view(self, car_data: Car) -> None: ...
    
    @abstractmethod
    def update_car_view(self, car_data: Car) -> None: ...
    
    # Similar methods for roads, crossing segments, queries, selection, settings...
```

#### Rationale

| Benefit | Explanation |
|---------|-------------|
| **Implementation Freedom** | The concrete view could be a 2D canvas (current), a 3D renderer, a text-based debugger, or a mock for testing. |
| **Controller Independence** | Controllers call `view.add_car_view(car)` without knowing whether this adds a rectangle to a `QGraphicsScene` or prints to console. |
| **Test Mocks** | Unit tests can provide a mock `TrafficView` that records method calls without rendering anything. |

### Concrete PySide6 Implementation

**Locations**:
- `src/view/canvas/traffic_scene.py` – `TrafficScene(QGraphicsScene)`
- `src/view/canvas/traffic_view.py` – `TrafficCanvasView(QGraphicsView)`

The concrete implementation uses Qt's Graphics View Framework:

| Class | Responsibility |
|-------|----------------|
| `TrafficScene` | Manages `QGraphicsItem` objects representing cars, roads, and crossings. Maintains mappings from entity names to graphics items. |
| `TrafficCanvasView` | Provides zoom and pan interaction. Handles mouse wheel for zooming and middle-mouse-button for panning. |

```python
class TrafficScene(QGraphicsScene):
    def __init__(self, parent=None):
        super().__init__(parent)
        self._car_items = {}   # Map car name to QGraphicsItem
        self._road_items = {}  # Map road name to QGraphicsItem
        self._crossing_items = {}
```

### Qt Designer Integration

**Location**: `src/view/ui/main_window_ui_binder.py`

The application supports Qt Designer `.ui` files for layout definition:

1. **Designer-based Layout**: The main window layout is defined in a `.ui` file created with Qt Designer.

2. **Widget Promotion**: `QGraphicsView` widgets in the `.ui` file are "promoted" to `TrafficCanvasView` for custom behavior.

3. **UI Binder Pattern**: The `MainWindowUiBinder` class finds widgets by `objectName` and provides typed access:

```python
class MainWindowUiBinder(Generic[TMainWindow]):
    def bind(self, root: TMainWindow) -> None:
        # Find widgets by objectName
        self.main_splitter = root.findChild(QSplitter, "mainSplitter")
        self.traffic_view = root.findChild(QGraphicsView, "trafficView")
        # ...
```

#### Rationale for UI Binder Pattern

| Benefit | Explanation |
|---------|-------------|
| **Separation of Structure and Behavior** | The `.ui` file defines layout; Python code defines behavior. Designers can modify layout without touching Python. |
| **Type Safety** | The binder provides typed attributes (`traffic_view: QGraphicsView`) rather than stringly-typed `findChild` calls scattered throughout the code. |
| **Stable Widget References** | Controllers receive widget references through the binder, isolated from changes in the `.ui` file structure. |

### Modal Dialogs

**Location**: `src/view/modals/entity_modal.py`

Modal dialogs for entity creation/editing inherit from a common base class:

```python
class EntityModal(QDialog):
    """
    Base class for entity creation/editing modals.
    
    Subclasses should:
    1. Override _setup_form() to add specific input fields
    2. Override _validate() to implement validation logic
    3. Override _collect_data() to gather form data
    """
```

This provides a consistent UX pattern across all entity types (cars, roads, queries) while allowing customization of form fields and validation rules.

---

## Signal-Based Model-to-View Binding

The model-to-view synchronization follows a **push-based reactive pattern**:

```
┌─────────────────┐         ┌──────────────────┐         ┌─────────────────┐
│  Command        │ mutates │  TrafficSnapshot │ emits   │  EventController│
│  (e.g., AddCar) │────────►│  (Model)         │────────►│  (Wiring)       │
└─────────────────┘         └──────────────────┘         └────────┬────────┘
                                                                  │ calls
                                                                  ▼
                                                         ┌─────────────────┐
                                                         │  TrafficView    │
                                                         │  (View)         │
                                                         └─────────────────┘
```

### Data Flow Example: Adding a Car

1. **User Action**: User fills out the "Add Car" modal and clicks OK.
2. **Command Creation**: UI creates an `AddCarCommand` with the form data.
3. **Command Execution**: `CommandController.execute_command(command)` is called.
4. **Model Mutation**: The command calls `traffic_snapshot_writer.add_car(car)`.
5. **Signal Emission**: The `ObservableDict` internally calls `self.car_added.emit(car)`.
6. **View Update**: The `EventController` has connected `car_added` to `view.add_car_view`, so the view's method is automatically invoked.
7. **Rendering**: `TrafficScene.add_car_item(car)` creates a `QGraphicsItem` for the new car.

### Why Push-Based?

| Alternative | Drawbacks |
|-------------|-----------|
| **Polling** | Inefficient; the view would need to constantly check for changes. |
| **Manual Refresh** | Error-prone; developers might forget to call refresh after a mutation. |
| **Direct Coupling** | Commands calling view methods directly would tightly couple model and view. |

The signal-based approach ensures **automatic, guaranteed view updates** whenever the model changes, without any coupling between the model and view layers.

---

## Design Patterns Summary

| Pattern | Where Used | Purpose |
|---------|------------|---------|
| **Facade** | `ApplicationController` | Provides a unified interface to the controller subsystem, hiding complexity of specialized controllers. |
| **Command** | `Command` class and subclasses | Encapsulates state mutations as objects, enabling undo/redo, logging, and decoupling. |
| **Observer** | `ObservableDict`, `ObservableList`, Qt Signals | Notifies interested parties (view) when model state changes. |
| **Interface Segregation** | `TrafficSnapshotReader`, `TrafficSnapshotWriter` | Separates read and write access to the model, enforcing access control. |
| **Strategy** (potential) | `TrafficView` interface | Allows swapping view implementations without changing controllers. |
| **Template Method** | `EntityModal` base class | Defines the skeleton of modal dialogs, with subclasses providing specific form fields and validation. |
| **Composite** | AST nodes (in query subsystem) | Represents complex query expressions as trees of nodes. *(Documented elsewhere)* |

---

## Recommended UML Diagrams

The following diagrams would effectively communicate the architecture:

### Component Diagram

**Purpose**: Show the high-level structure of the application, including the four main layers and their dependencies.

**Contents**:
- Components: `View Layer`, `Controller Layer`, `Command Layer`, `Core Layer`
- Interfaces: `TrafficView`, `TrafficSnapshotReader`, `TrafficSnapshotWriter`
- Dependencies: Arrows showing which components depend on which interfaces
- Multiplicity: Show that multiple command types exist in the Command Layer

---

### Class Diagram: Controller Layer

**Purpose**: Detail the relationships between controllers and their dependencies.

**Contents**:
- Classes: `ApplicationController`, `CommandController`, `EventController`, `DataController`
- Interfaces: `TrafficSnapshotReader`, `TrafficSnapshotWriter`, `TrafficView`
- Relationships:
  - `ApplicationController` ◇── (composition) `CommandController`, `EventController`, `DataController`
  - `CommandController` ──► (dependency) `TrafficSnapshotReader`, `TrafficSnapshotWriter`
  - `EventController` ──► (dependency) `TrafficSnapshot`, `TrafficView`, `Settings`
  - `DataController` ──► (dependency) `TrafficSnapshotReader`

---

### Class Diagram: Command Pattern

**Purpose**: Show the command hierarchy and how commands interact with the model.

**Contents**:
- Abstract class: `Command<ReturnValue>`
- Concrete classes: `AddCarCommand`, `EditCarCommand`, `DeleteCarCommand`, `AddRoadCommand`, etc.
- Interfaces: `TrafficSnapshotReader`, `TrafficSnapshotWriter`
- Relationships:
  - All concrete commands inherit from `Command`
  - Commands hold references to `TrafficSnapshotReader` and/or `TrafficSnapshotWriter`
  - `CommandController` executes `Command` objects

---

### Class Diagram: Core Layer Interfaces

**Purpose**: Illustrate the Interface Segregation pattern in the core layer.

**Contents**:
- Interfaces: `TrafficSnapshotReader` (with read methods), `TrafficSnapshotWriter` (with write methods)
- Concrete class: `TrafficSnapshot` implements both interfaces
- Show method signatures in each interface
- Annotations: Note that `TrafficSnapshot` inherits from `QObject` for signal support

---

### Sequence Diagram: Add Car Flow

**Purpose**: Show the complete data flow from user action to view update when adding a car.

**Contents**:
- Participants: `User`, `AddCarModal`, `CommandController`, `AddCarCommand`, `TrafficSnapshot`, `ObservableDict`, `EventController`, `TrafficView`, `TrafficScene`
- Messages:
  1. User → AddCarModal: submit form
  2. AddCarModal → CommandController: `add_car(...)`
  3. CommandController → AddCarCommand: `execute()`
  4. AddCarCommand → TrafficSnapshot: `add_car(car)`
  5. TrafficSnapshot → ObservableDict: `__setitem__(name, car)`
  6. ObservableDict → TrafficSnapshot: `car_added.emit(car)`
  7. TrafficSnapshot → EventController: (signal received)
  8. EventController → TrafficView: `add_car_view(car)`
  9. TrafficView → TrafficScene: `add_car_item(car)`

---

### Class Diagram: View Layer

**Purpose**: Show the abstract/concrete view structure and Qt Designer integration.

**Contents**:
- Abstract class: `TrafficView` (interface)
- Concrete classes: `TrafficScene`, `TrafficCanvasView`
- Helper class: `MainWindowUiBinder`
- Relationships:
  - `TrafficScene` implements `TrafficView` (or is composed with a class that does)
  - `TrafficCanvasView` ──► (uses) `TrafficScene`
  - `MainWindowUiBinder` ──► (finds) `TrafficCanvasView` by objectName
- Stereotypes: Mark `TrafficScene` as `<<QGraphicsScene>>`, `TrafficCanvasView` as `<<QGraphicsView>>`

---

### State Diagram: Selection State

**Purpose**: Show the allowed state transitions for entity selection.

**Contents**:
- States: `Nothing Selected`, `Car Selected`, `Road Selected`
- Transitions:
  - `Nothing Selected` → `Car Selected`: on `select_car()`
  - `Nothing Selected` → `Road Selected`: on `select_road()`
  - `Car Selected` → `Nothing Selected`: on `deselect_car()` or `clear_selection()`
  - `Car Selected` → `Road Selected`: on `select_road()` (implicit deselect)
  - `Road Selected` → `Nothing Selected`: on `deselect_road()` or `clear_selection()`
  - `Road Selected` → `Car Selected`: on `select_car()` (implicit deselect)

---

## Appendix: Directory Structure

```
src/
├── commands/           # Command Pattern implementations
│   ├── command.py      # Abstract Command base class
│   ├── cars/           # Car-related commands
│   ├── roads/          # Road-related commands
│   ├── umlsl/          # UMLSL query commands
│   ├── selection/      # Selection state commands
│   ├── settings/       # Application settings commands
│   └── persistence/    # Save/Load commands
├── controllers/        # Controller layer
│   ├── application_controller.py  # Facade
│   ├── command_controller.py      # Command execution
│   ├── event_controller.py        # Signal-to-view binding
│   └── data_controller.py         # Read-only data access
├── core/               # Domain model
│   ├── entities/       # Domain entities (Car, Road, UMLSLQuery)
│   ├── value_objects/  # Immutable value types (Lane, Position, TurnIntent)
│   ├── view_models/    # Observable models (TrafficSnapshot, Settings, Selection)
│   ├── helper/         # Utilities (ObservableDict, uid_service)
│   ├── traffic_snapshot_reader.py  # Read interface
│   └── traffic_snapshot_writer.py  # Write interface
├── persistence/        # Serialization services
├── query/              # UMLSL query evaluation (documented separately)
└── view/               # View layer
    ├── traffic_view.py # Abstract view interface
    ├── canvas/         # PySide6 graphics view implementation
    ├── modals/         # Dialog windows
    └── ui/             # Qt Designer binders
```

---

*This architecture documentation is part of the larger UMLSL Traffic Editor design documentation. For domain model details, entity specifications, and persistence format documentation, refer to the corresponding sections.*

