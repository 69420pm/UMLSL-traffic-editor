# Controller Architecture Diagram

## Before Refactoring

```
┌─────────────────────────────────────────────────────┐
│         ApplicationController                       │
│                                                     │
│  ┌──────────────────────────────────────────┐      │
│  │  Signal Connection Methods               │      │
│  │  - _setup_event_listeners()              │      │
│  │  - _on_car_added()                       │      │
│  │  - _on_car_removed()                     │      │
│  │  - _on_car_updated()                     │      │
│  │  - _on_road_added()                      │      │
│  │  - _on_road_removed()                    │      │
│  │  - _on_road_updated()                    │      │
│  │  - _on_crossing_segment_added()          │      │
│  │  - _on_crossing_segment_removed()        │      │
│  │  - _on_crossing_segment_updated()        │      │
│  │  (15+ intermediate handler methods)      │      │
│  └──────────────────────────────────────────┘      │
│                                                     │
│  ┌──────────────────────────────────────────┐      │
│  │  Command Execution Methods               │      │
│  │  - _execute_command()                    │      │
│  │  - add_car()                             │      │
│  │  - remove_car()                          │      │
│  │  - edit_car()                            │      │
│  │  - add_road()                            │      │
│  │  - remove_road()                         │      │
│  │  - edit_road()                           │      │
│  │  - add_umlsl_query()                     │      │
│  │  - remove_umlsl_query()                  │      │
│  │  - edit_umlsl_query()                    │      │
│  │  - undo() / redo()                       │      │
│  └──────────────────────────────────────────┘      │
│                                                     │
│  Problems:                                          │
│  - Mixed responsibilities                           │
│  - Hard to test                                     │
│  - Lots of boilerplate                             │
│  - Difficult to extend                             │
└─────────────────────────────────────────────────────┘
```

## After Refactoring

```
┌─────────────────────────────────────────────────────────────────┐
│                   ApplicationController                         │
│                         (Facade)                                │
│                                                                 │
│  Delegates to:                                                  │
│  - view_controller.method()                                     │
│  - command_controller.method()                                  │
│                                                                 │
│  Purpose: Maintains backward compatibility                      │
└────────────────┬────────────────────────────┬───────────────────┘
                 │                            │
        ┌────────▼─────────┐         ┌────────▼──────────┐
        │                  │         │                   │
        │ ViewController   │         │ CommandController │
        │                  │         │                   │
        └──────────────────┘         └───────────────────┘

┌──────────────────────────────────┐  ┌─────────────────────────────────┐
│      ViewController              │  │     CommandController           │
│                                  │  │                                 │
│  Responsibility:                 │  │  Responsibility:                │
│  Model → View Synchronization    │  │  Command Execution & History    │
│                                  │  │                                 │
│  ┌────────────────────────┐     │  │  ┌──────────────────────┐      │
│  │ Direct Connections     │     │  │  │ Command Execution    │      │
│  │                        │     │  │  │                      │      │
│  │ model.car_added        │     │  │  │ execute_command()    │      │
│  │   → view.add_car_view  │     │  │  │ execute_without_     │      │
│  │                        │     │  │  │   history()          │      │
│  │ model.road_added       │     │  │  │                      │      │
│  │   → view.add_road_view │     │  │  │ undo() / redo()      │      │
│  │                        │     │  │  │ can_undo()           │      │
│  │ (No intermediate       │     │  │  │ can_redo()           │      │
│  │  handler methods!)     │     │  │  └──────────────────────┘      │
│  └────────────────────────┘     │  │                                 │
│                                  │  │  ┌──────────────────────┐      │
│  Benefits:                       │  │  │ High-Level API       │      │
│  ✓ Clean & concise               │  │  │                      │      │
│  ✓ Easy to understand            │  │  │ add_car()            │      │
│  ✓ Less code to maintain         │  │  │ remove_car()         │      │
│                                  │  │  │ edit_car()           │      │
└──────────────────────────────────┘  │  │ add_road()           │      │
                                      │  │ remove_road()         │      │
                                      │  │ edit_road()           │      │
                                      │  │ add_umlsl_query()     │      │
                                      │  │ remove_umlsl_query()  │      │
                                      │  │ edit_umlsl_query()    │      │
                                      │  └──────────────────────┘      │
                                      │                                 │
                                      │  Benefits:                      │
                                      │  ✓ Single responsibility        │
                                      │  ✓ Undo/redo in one place       │
                                      │  ✓ Easy to test                 │
                                      └─────────────────────────────────┘
```

## Signal Flow Comparison

### Before (Verbose)
```
TrafficSnapshot
    │
    │ car_added.emit(car)
    ↓
ApplicationController._on_car_added(car)
    │
    │ self.view.add_car_view(car)
    ↓
MainWindow.add_car_view(car)
    │
    ├→ Sidebar.add_car(car)
    └→ Canvas.add_car_item(car)
```

### After (Direct)
```
TrafficSnapshot
    │
    │ car_added.emit(car)
    ↓
MainWindow.add_car_view(car)  ← Direct connection!
    │
    ├→ Sidebar.add_car(car)
    └→ Canvas.add_car_item(car)
```

## Command Execution Flow

```
User Action (e.g., "Add Car" button clicked)
    ↓
UI Handler
    ↓
CommandController.add_car(...)
    ↓
Creates AddCarCommand
    ↓
CommandController.execute_command(command)
    │
    ├→ Validates command
    ├→ Executes command.execute()
    ├→ Adds to undo stack
    └→ Returns result
        ↓
TrafficSnapshot.add_car(car)  ← Model is updated
    │
    │ car_added.emit(car)  ← Signal automatically emitted
    ↓
MainWindow.add_car_view(car)  ← View automatically updates
    │
    ├→ Sidebar.add_car(car)
    └→ Canvas.add_car_item(car)
```

## Selection Flow (Future Implementation)

```
User clicks car in sidebar
    ↓
Sidebar.car_selected.emit(car)
    ↓
ApplicationController receives signal
    ↓
Creates SelectEntityCommand(car)
    ↓
CommandController.execute_without_history(command)
    │
    └→ Does NOT add to undo stack!
        ↓
SelectionModel.select_car(car)
    │
    │ selection_changed.emit()
    ↓
Views update visual selection
    │
    ├→ Sidebar highlights selected car
    └→ Canvas highlights selected car
```

## Code Reduction

| Metric | Before | After | Reduction |
|--------|--------|-------|-----------|
| Lines in ApplicationController | ~139 | ~180 (all 3 files) | Net: +41 lines |
| Handler methods | 15+ | 0 | -15 methods |
| Controllers | 1 | 3 | Better separation |
| Lines per controller | 139 | ~60 avg | Easier to read |
| Responsibility overlap | High | None | Clear boundaries |

**Note**: While total lines increased slightly, each file is now:
- Smaller and focused
- Easier to understand
- Easier to test
- Easier to extend

## Testing Strategy

### Before (Difficult)
```python
# Had to mock everything in one test
def test_application_controller():
    # Test both view sync AND command execution
    # Lots of setup, hard to isolate
```

### After (Easy)
```python
# Test view controller independently
def test_view_controller():
    # Only test signal connections
    # Mock view, check method calls
    
# Test command controller independently  
def test_command_controller():
    # Only test command execution
    # Mock traffic_snapshot, verify calls
```

## Files Summary

1. **`view_controller.py`** (47 lines)
   - Clean, focused responsibility
   - Direct signal connections
   - No logic, just wiring

2. **`command_controller.py`** (263 lines)
   - All command-related logic
   - Undo/redo management
   - High-level API methods

3. **`application_controller.py`** (171 lines)
   - Facade pattern
   - Backward compatibility
   - Simple delegation

4. **`__init__.py`** (9 lines)
   - Clean exports
   - Easy imports

