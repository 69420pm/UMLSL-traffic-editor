# Modal Architecture Documentation

## Overview

This document describes the modal dialog architecture for creating, editing, and deleting entities (Cars, Roads, and UMLSL Queries) in the UMLSL Traffic Editor.

## Design Principles

### 1. Separation of Concerns
- **Views (Modals)** collect and validate user input, but never directly access the model
- **Controller** mediates all data access and command execution
- **Model** remains isolated from UI concerns

### 2. Data Flow
```
User Action (Button Click)
    ↓
Sidebar emits request signal (e.g., create_car_requested)
    ↓
ApplicationController handles request
    ↓
Controller creates modal with data provider callbacks
    ↓
Modal populates dropdowns via callbacks (accessing TrafficSnapshotReader)
    ↓
User fills form and clicks OK
    ↓
Modal validates and emits confirmed signal with parameters
    ↓
Controller receives parameters and executes command
    ↓
Command validates and modifies TrafficSnapshot
    ↓
Model emits signals → View updates automatically
```

## Architecture Components

### 1. Base Modal Class: `EntityModal`

**Location**: `pse/umlsl_editor/src/view/modals/entity_modal.py`

Abstract base class providing common modal functionality:

- Form layout structure
- OK/Cancel buttons
- Validation error display
- Mode handling (CREATE vs EDIT)

**Key Methods**:
- `_setup_form()`: Override to add specific input fields
- `_validate()`: Override to implement validation logic
- `_collect_data()`: Override to gather form data
- `accept()`: Override to emit entity-specific signals

**Usage Pattern**:
```python
class CarModal(EntityModal):
    car_confirmed = Signal(CarParams)
    
    def _setup_form(self):
        # Add input fields
        self.name_input = QLineEdit()
        self.form_layout.addRow("Name:", self.name_input)
    
    def _validate(self) -> tuple[bool, str]:
        # Validate input
        if not self.name_input.text().strip():
            return False, "Name cannot be empty"
        return True, ""
    
    def accept(self):
        data = self._collect_data()
        params = CarParams(**data)
        self.car_confirmed.emit(params)
        super().accept()
```

### 2. Entity-Specific Modals

#### CarModal
**Location**: `pse/umlsl_editor/src/view/modals/car_modal.py`

**Constructor Parameters**:
- `mode`: CREATE or EDIT
- `get_roads`: Callback function `() -> list[Road]` for populating road dropdown
- `initial_data`: Dictionary with initial values (for EDIT mode)
- `parent`: Parent widget

**Signal**:
- `car_confirmed(CarParams)`: Emitted when user confirms with valid data

**Form Fields**:
- Name (QLineEdit)
- Road (QComboBox) - populated via `get_roads()` callback
- Lane Index (QSpinBox)
- Lane Direction (QComboBox: Forward/Backward)
- Color (QLineEdit with color picker button)
- Position on Lane (QDoubleSpinBox)
- Transition (QDoubleSpinBox: -0.99 to 0.99)
- Velocity (QDoubleSpinBox)
- Length (QDoubleSpinBox)
- Next Turn (TODO: implement when TurnIntent is finalized)

**Validation**:
- Name: Non-empty string
- Road: Must be selected
- Color: Must be #RRGGBB format
- Length: Must be positive

#### RoadModal
**Location**: `pse/umlsl_editor/src/view/modals/road_modal.py`

**Constructor Parameters**:
- `mode`: CREATE or EDIT
- `initial_data`: Dictionary with initial values (for EDIT mode)
- `parent`: Parent widget

**Signal**:
- `road_confirmed(RoadParams)`: Emitted when user confirms with valid data

**Form Fields**:
- Name (QLineEdit)
- Orientation (QComboBox: Horizontal/Vertical)
- Position (QDoubleSpinBox)
- Forward Lanes (QSpinBox: 0-10)
- Backward Lanes (QSpinBox: 0-10)

**Validation**:
- Name: Non-empty string
- Lanes: At least one lane (forward or backward) must exist

#### QueryModal
**Location**: `pse/umlsl_editor/src/view/modals/query_modal.py`

**Constructor Parameters**:
- `mode`: CREATE or EDIT
- `get_cars`: Callback function `() -> list[Car]` for populating car dropdown
- `initial_data`: Dictionary with initial values (for EDIT mode)
- `parent`: Parent widget

**Signal**:
- `query_confirmed(str, Car)`: Emitted with (latex, assigned_car) when confirmed

**Form Fields**:
- LaTeX Query (QTextEdit with example help text)
- Assigned Car (QComboBox) - populated via `get_cars()` callback

**Validation**:
- LaTeX: Non-empty string
- Car: Must be selected

### 3. Confirmation Dialog

**Location**: `pse/umlsl_editor/src/view/modals/confirmation_dialog.py`

Simple yes/no confirmation for destructive operations (delete).

**Usage**:
```python
if ConfirmationDialog.confirm("Delete Car", f"Delete car '{car_name}'?", parent):
    # Proceed with deletion
    self.remove_car(car_name)
```

### 4. Sidebar List Widgets

**Locations**:
- `pse/umlsl_editor/src/view/sidebar/cars_list_widget.py`
- `pse/umlsl_editor/src/view/sidebar/roads_list_widget.py`
- `pse/umlsl_editor/src/view/sidebar/queries_list_widget.py`

**Added Features**:
- Add/Edit/Delete buttons below the list
- Edit/Delete buttons disabled until item selected
- Emit CRUD request signals when buttons clicked

**New Signals**:
```python
# CarsListWidget
create_car_requested = Signal()
edit_car_requested = Signal(str)  # car name
delete_car_requested = Signal(str)  # car name

# RoadsListWidget
create_road_requested = Signal()
edit_road_requested = Signal(str)  # road name
delete_road_requested = Signal(str)  # road name

# QueriesListWidget
create_query_requested = Signal()
edit_query_requested = Signal(int)  # query hash
delete_query_requested = Signal(int)  # query hash
```

### 5. SidebarWidget

**Location**: `pse/umlsl_editor/src/view/sidebar/sidebar_widget.py`

**Updated Behavior**:
- Forwards CRUD request signals from list widgets to parent
- Controller can connect to these signals

**New Signals** (forwarded from list widgets):
- All car, road, and query CRUD signals

### 6. ApplicationController

**Location**: `pse/umlsl_editor/src/controllers/application_controller.py`

**New Responsibilities**:
- Create and show modals in response to CRUD requests
- Provide data access callbacks to modals (using `TrafficSnapshotReader`)
- Connect modal confirmation signals to command execution
- Show confirmation dialogs for delete operations

**New Methods**:

#### Modal Factory Methods (to be implemented)
```python
def show_create_car_modal() -> None:
    """Create and show car creation modal."""
    
def show_edit_car_modal(car_name: str) -> None:
    """Create and show car editing modal."""
    
def show_create_road_modal() -> None:
    """Create and show road creation modal."""
    
def show_edit_road_modal(road_name: str) -> None:
    """Create and show road editing modal."""
    
def show_create_query_modal() -> None:
    """Create and show query creation modal."""
    
def show_edit_query_modal(query_hash: int) -> None:
    """Create and show query editing modal."""
```

#### Delete Handlers (to be implemented)
```python
def handle_delete_car(car_name: str) -> None:
    """Show confirmation and delete car if confirmed."""
    
def handle_delete_road(road_name: str) -> None:
    """Show confirmation and delete road if confirmed."""
    
def handle_delete_query(query_hash: int) -> None:
    """Show confirmation and delete query if confirmed."""
```

#### Confirmation Handlers (to be implemented)
```python
def _on_car_confirmed(car_params: CarParams) -> None:
    """Execute add/edit car command with validated parameters."""
    
def _on_road_confirmed(road_params: RoadParams) -> None:
    """Execute add/edit road command with validated parameters."""
    
def _on_query_confirmed(latex: str, assigned_car: Car) -> None:
    """Execute add/edit query command with validated parameters."""
```

## Implementation Example: Creating a Car

### Step-by-Step Flow

1. **User clicks "Add" button** in Cars tab
   ```
   User → CarsListWidget.add_button.clicked
   ```

2. **Cars list widget emits request signal**
   ```python
   # In CarsListWidget._on_add_clicked()
   self.create_car_requested.emit()
   ```

3. **Sidebar forwards signal**
   ```python
   # In SidebarWidget._setup_ui()
   self.cars_list.create_car_requested.connect(self.create_car_requested.emit)
   ```

4. **Controller handles request** (to be implemented)
   ```python
   # In ApplicationController.show_create_car_modal()
   modal = CarModal(
       mode=ModalMode.CREATE,
       get_roads=lambda: self.traffic_snapshot.get_roads(),
       parent=self.view
   )
   modal.car_confirmed.connect(self._on_car_confirmed)
   modal.exec()  # Blocking modal
   ```

5. **Modal populates dropdowns**
   ```python
   # In CarModal._populate_roads()
   roads = self.get_roads()  # Calls controller's lambda
   for road in roads:
       self.road_combo.addItem(road.name, road)
   ```

6. **User fills form and clicks OK**
   - Modal validates input via `_validate()`
   - If valid, calls `accept()`

7. **Modal emits confirmation signal**
   ```python
   # In CarModal.accept()
   data = self._collect_data()
   car_params = CarParams(**data)
   self.car_confirmed.emit(car_params)
   ```

8. **Controller receives parameters** (to be implemented)
   ```python
   # In ApplicationController._on_car_confirmed()
   try:
       self.add_car(
           name=car_params.name,
           assigned_road=car_params.lane.road,
           lane_index=car_params.lane.lane_index,
           lane_direction=car_params.lane.lane_direction,
           color=car_params.color,
           position_on_lane=car_params.position_on_lane,
           transition=car_params.transition,
           velocity=car_params.velocity,
           length=car_params.length,
           next_turn=car_params.next_turn
       )
   except Exception as e:
       # Show error dialog to user
       QMessageBox.critical(self.view, "Error", str(e))
   ```

9. **Command executes**
   - Creates `AddCarCommand`
   - Validates via command's `validate()` method
   - Adds car to `TrafficSnapshot`

10. **Model emits signal**
    ```python
    # In TrafficSnapshot (via ObservableDict)
    self.car_added.emit(car)
    ```

11. **View updates automatically**
    ```python
    # In ViewController (already connected)
    self.traffic_snapshot.car_added.connect(self.view.add_car_view)
    ```

## Key Benefits

### 1. No Direct Model Access from Views
- Modals receive data via callbacks, not direct references
- Controller mediates all data access
- Maintains strict MVC separation

### 2. Reusable Components
- `EntityModal` base class reduces duplication
- `ConfirmationDialog` utility for all delete operations
- Consistent UX across all entity types

### 3. Validation in Layers
- **Modal validation**: Basic format checks (non-empty, correct format)
- **Command validation**: Business logic (unique names, valid references)
- Clear error messages at appropriate level

### 4. Testability
- Modals can be unit tested with mock callbacks
- Controller logic can be tested independently
- Commands remain independent of UI

### 5. Extensibility
- Easy to add new entity types by subclassing `EntityModal`
- Modal behavior can be customized per entity
- Edit mode reuses same modal as create mode

## TODO: Implementation Tasks

### High Priority
1. Implement `ApplicationController.show_create_car_modal()`
2. Implement `ApplicationController._on_car_confirmed()`
3. Implement `ApplicationController.handle_delete_car()`
4. Repeat for roads and queries

### Medium Priority
1. Implement `CarModal._populate_initial_data()` for EDIT mode
2. Implement `RoadModal._populate_initial_data()` for EDIT mode
3. Implement `QueryModal._populate_initial_data()` for EDIT mode
4. Add error message dialogs when command execution fails

### Low Priority
1. Add turn intent selection to `CarModal`
2. Add keyboard shortcuts (Ctrl+N for new, Del for delete)
3. Add context menu to list items (right-click → Edit/Delete)
4. Add icons to buttons
5. Add tooltips to form fields

## Testing Considerations

### Unit Tests
- Test each modal's validation logic
- Test `_collect_data()` with various inputs
- Test callback mechanism with mocks

### Integration Tests
- Test complete flow from button click to model update
- Test error handling when validation fails
- Test cancel behavior (no changes to model)

### UI Tests
- Test keyboard navigation (Tab, Enter, Escape)
- Test button enable/disable states
- Test color picker integration
- Test dropdown population

## Notes

### Modal Lifecycle
- Modals are created each time (not reused)
- Controller creates modal, connects signals, calls `exec()`
- Modal is destroyed after closing
- No persistent state between invocations

### Thread Safety
- All modal operations happen on main Qt thread
- No async operations in modals
- Blocking exec() ensures sequential execution

### Error Handling
- Modal validation shows inline errors
- Command validation failures should show message dialog
- Network/file errors should show message dialog
- Always provide actionable error messages to user

