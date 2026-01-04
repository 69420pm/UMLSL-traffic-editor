# Modal Architecture Diagram

## Complete System Architecture with Modals

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                           USER INTERFACE LAYER                              │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                             │
│  ┌──────────────────────┐              ┌──────────────────────────────┐    │
│  │   MainWindow         │              │   Modal Dialogs              │    │
│  │                      │              │                              │    │
│  │  ┌────────────────┐  │              │  ┌────────────────────────┐  │    │
│  │  │  SidebarWidget │  │              │  │  EntityModal (Base)    │  │    │
│  │  │                │  │              │  │  ├─ Form Layout        │  │    │
│  │  │  ┌──────────┐  │  │              │  │  ├─ Validation        │  │    │
│  │  │  │ Queries  │  │  │              │  │  └─ OK/Cancel         │  │    │
│  │  │  │ [Add]    │━━┓  │              │  └────────────────────────┘  │    │
│  │  │  │ [Edit]   │  ┃  │              │           ▲                  │    │
│  │  │  │ [Delete] │  ┃  │              │           │                  │    │
│  │  │  └──────────┘  ┃  │              │  ┌────────┴─────────────┐   │    │
│  │  │                ┃  │              │  │                      │   │    │
│  │  │  ┌──────────┐  ┃  │              │  │  CarModal            │   │    │
│  │  │  │ Cars     │  ┃  │              │  │  RoadModal           │   │    │
│  │  │  │ [Add]    │━━╋━━┃━━━━━━━━━━━━━━┃━━▶  QueryModal          │   │    │
│  │  │  │ [Edit]   │  ┃  │   Triggers   │  │                      │   │    │
│  │  │  │ [Delete] │  ┃  │   Modal      │  │  ConfirmationDialog  │   │    │
│  │  │  └──────────┘  ┃  │              │  └──────────────────────┘   │    │
│  │  │                ┃  │              │                              │    │
│  │  │  ┌──────────┐  ┃  │              └──────────────────────────────┘    │
│  │  │  │ Roads    │  ┃  │                           │                      │
│  │  │  │ [Add]    │━━┛  │                           │ Emits                │
│  │  │  │ [Edit]   │     │                           │ Confirmed            │
│  │  │  │ [Delete] │     │                           │ Signal               │
│  │  │  └──────────┘     │                           │                      │
│  │  └────────────────┘  │                           ▼                      │
│  │                      │                                                  │
│  │  ┌────────────────┐  │                                                  │
│  │  │  Canvas        │  │                                                  │
│  │  └────────────────┘  │                                                  │
│  └──────────────────────┘                                                  │
│             │                                                               │
│             │ Emits CRUD Signals                                            │
│             ▼                                                               │
└─────────────────────────────────────────────────────────────────────────────┘
              │
              │
┌─────────────▼───────────────────────────────────────────────────────────────┐
│                           CONTROLLER LAYER                                  │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                             │
│  ┌─────────────────────────────────────────────────────────────────────┐   │
│  │  ApplicationController (Facade)                                     │   │
│  │                                                                     │   │
│  │  Modal Management Methods:                                         │   │
│  │  ┌──────────────────────────────────────────────────────────────┐  │   │
│  │  │  show_create_car_modal()                                     │  │   │
│  │  │    1. Create CarModal with callbacks                         │  │   │
│  │  │    2. get_roads: () => snapshot.get_roads()                  │  │   │
│  │  │    3. Connect car_confirmed → _on_car_confirmed()            │  │   │
│  │  │    4. modal.exec() (blocking)                                │  │   │
│  │  │                                                              │  │   │
│  │  │  _on_car_confirmed(car_params)                               │  │   │
│  │  │    1. Extract parameters from CarParams                      │  │   │
│  │  │    2. Call self.add_car(...) [CommandController method]      │  │   │
│  │  │    3. Handle exceptions → show error dialog                  │  │   │
│  │  │                                                              │  │   │
│  │  │  handle_delete_car(car_name)                                 │  │   │
│  │  │    1. Show ConfirmationDialog                                │  │   │
│  │  │    2. If confirmed: self.remove_car(car_name)                │  │   │
│  │  │    3. Handle exceptions → show error dialog                  │  │   │
│  │  └──────────────────────────────────────────────────────────────┘  │   │
│  │                                                                     │   │
│  │  (Similar methods for roads and queries)                            │   │
│  │                                                                     │   │
│  └─────────────────────────────────────────────────────────────────────┘   │
│         │                           │                         │             │
│         │                           │                         │             │
│  ┌──────▼──────────┐    ┌───────────▼────────────┐   ┌──────▼──────┐     │
│  │ ViewController  │    │  CommandController     │   │  Callbacks  │     │
│  │                 │    │                        │   │             │     │
│  │ Model → View    │    │  Command Execution     │   │ get_roads() │     │
│  │ Signal wiring   │    │  add_car()             │   │ get_cars()  │     │
│  │                 │    │  remove_car()          │   │             │     │
│  └─────────────────┘    │  edit_car()            │   └─────────────┘     │
│                         │  (and road, query)     │                       │
│                         └────────────────────────┘                       │
│                                    │                                     │
└────────────────────────────────────┼─────────────────────────────────────┘
                                     │ Executes Commands
                                     ▼
┌─────────────────────────────────────────────────────────────────────────────┐
│                            COMMAND LAYER                                    │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                             │
│  ┌──────────────────┐  ┌──────────────────┐  ┌──────────────────┐         │
│  │  AddCarCommand   │  │  EditCarCommand  │  │ DeleteCarCommand │         │
│  │                  │  │                  │  │                  │         │
│  │  validate()      │  │  validate()      │  │  validate()      │         │
│  │  execute()       │  │  execute()       │  │  execute()       │         │
│  │  undo()          │  │  undo()          │  │  undo()          │         │
│  └──────────────────┘  └──────────────────┘  └──────────────────┘         │
│                                                                             │
│  (Similar commands for roads and queries)                                  │
│                                                                             │
└─────────────────────────────────────────────────────────────────────────────┘
                                     │ Modifies
                                     ▼
┌─────────────────────────────────────────────────────────────────────────────┐
│                            MODEL LAYER                                      │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                             │
│  ┌─────────────────────────────────────────────────────────────────────┐   │
│  │  TrafficSnapshot                                                    │   │
│  │                                                                     │   │
│  │  TrafficSnapshotReader:          TrafficSnapshotWriter:            │   │
│  │  ├─ get_cars()                   ├─ add_car(car)                   │   │
│  │  ├─ get_roads()                  ├─ remove_car(name)               │   │
│  │  ├─ get_cars_on_road(road)       ├─ update_car(car)                │   │
│  │  └─ validate_lane(...)           ├─ add_road(road)                 │   │
│  │                                  ├─ remove_road(name)              │   │
│  │                                  └─ update_road(road)              │   │
│  │                                                                     │   │
│  │  Observable Collections:                                           │   │
│  │  ├─ _cars: ObservableDict<str, Car>                                │   │
│  │  ├─ _roads: ObservableDict<str, Road>                              │   │
│  │  └─ _crossing_segments: ObservableList<CrossingSegment>            │   │
│  │                                                                     │   │
│  │  Signals (auto-emitted by ObservableDict/List):                    │   │
│  │  ├─ car_added, car_removed, car_updated                            │   │
│  │  ├─ road_added, road_removed, road_updated                         │   │
│  │  └─ query_added, query_removed, query_updated                      │   │
│  └─────────────────────────────────────────────────────────────────────┘   │
│                                                                             │
└─────────────────────────────────────────────────────────────────────────────┘
```

## Data Flow: Creating a Car

```
┌────────────┐
│ 1. User    │ Clicks "Add" button in Cars list
└──────┬─────┘
       │
       ▼
┌──────────────────────────────────────────────────────────────┐
│ 2. CarsListWidget                                            │
│    create_car_requested.emit()                               │
└──────┬───────────────────────────────────────────────────────┘
       │
       ▼
┌──────────────────────────────────────────────────────────────┐
│ 3. SidebarWidget                                             │
│    Forwards: create_car_requested.emit()                     │
└──────┬───────────────────────────────────────────────────────┘
       │
       ▼
┌──────────────────────────────────────────────────────────────┐
│ 4. ApplicationController.show_create_car_modal()             │
│    ┌──────────────────────────────────────────────────────┐  │
│    │ modal = CarModal(                                    │  │
│    │   mode=CREATE,                                       │  │
│    │   get_roads=lambda: self.snapshot.get_roads()        │  │
│    │ )                                                    │  │
│    │ modal.car_confirmed.connect(self._on_car_confirmed) │  │
│    │ modal.exec()                                         │  │
│    └──────────────────────────────────────────────────────┘  │
└──────┬───────────────────────────────────────────────────────┘
       │
       ▼
┌──────────────────────────────────────────────────────────────┐
│ 5. CarModal                                                  │
│    ┌──────────────────────────────────────────────────────┐  │
│    │ _populate_roads():                                   │  │
│    │   roads = self.get_roads()  ← Calls controller lambda│  │
│    │   for road in roads:                                 │  │
│    │     combo.addItem(road.name, road)                   │  │
│    └──────────────────────────────────────────────────────┘  │
│                                                              │
│    User fills form fields...                                 │
│    User clicks OK                                            │
│                                                              │
│    ┌──────────────────────────────────────────────────────┐  │
│    │ _validate():                                         │  │
│    │   if not name: return False, "Name required"        │  │
│    │   if not color.startswith('#'): return False, "..."  │  │
│    │   return True, ""                                   │  │
│    └──────────────────────────────────────────────────────┘  │
│                                                              │
│    ┌──────────────────────────────────────────────────────┐  │
│    │ accept():                                            │  │
│    │   data = self._collect_data()                        │  │
│    │   params = CarParams(**data)                         │  │
│    │   self.car_confirmed.emit(params)                    │  │
│    └──────────────────────────────────────────────────────┘  │
└──────┬───────────────────────────────────────────────────────┘
       │
       ▼
┌──────────────────────────────────────────────────────────────┐
│ 6. ApplicationController._on_car_confirmed(car_params)       │
│    ┌──────────────────────────────────────────────────────┐  │
│    │ try:                                                 │  │
│    │   self.add_car(                                      │  │
│    │     name=params.name,                                │  │
│    │     assigned_road=params.lane.road,                  │  │
│    │     ...                                              │  │
│    │   )                                                  │  │
│    │ except Exception as e:                               │  │
│    │   QMessageBox.critical("Error", str(e))              │  │
│    └──────────────────────────────────────────────────────┘  │
└──────┬───────────────────────────────────────────────────────┘
       │
       ▼
┌──────────────────────────────────────────────────────────────┐
│ 7. CommandController.add_car(...)                           │
│    ┌──────────────────────────────────────────────────────┐  │
│    │ command = AddCarCommand(snapshot, params)            │  │
│    │ command.validate()  ← Business logic validation      │  │
│    │ command.execute()   ← Modifies model                 │  │
│    └──────────────────────────────────────────────────────┘  │
└──────┬───────────────────────────────────────────────────────┘
       │
       ▼
┌──────────────────────────────────────────────────────────────┐
│ 8. TrafficSnapshot (Model)                                  │
│    ┌──────────────────────────────────────────────────────┐  │
│    │ _cars[car.name] = car  ← ObservableDict              │  │
│    │   ↓                                                  │  │
│    │ car_added.emit(car)  ← Auto-emitted by Observable    │  │
│    └──────────────────────────────────────────────────────┘  │
└──────┬───────────────────────────────────────────────────────┘
       │
       ▼
┌──────────────────────────────────────────────────────────────┐
│ 9. ViewController (already wired in __init__)                │
│    ┌──────────────────────────────────────────────────────┐  │
│    │ snapshot.car_added.connect(view.add_car_view)        │  │
│    └──────────────────────────────────────────────────────┘  │
└──────┬───────────────────────────────────────────────────────┘
       │
       ▼
┌──────────────────────────────────────────────────────────────┐
│ 10. MainWindow.add_car_view(car)                            │
│     ┌─────────────────────────────────────────────────────┐  │
│     │ scene.add_car_item(car)  ← Adds to canvas          │  │
│     │ sidebar.add_car(car)     ← Adds to list            │  │
│     └─────────────────────────────────────────────────────┘  │
└─────────────────────────────────────────────────────────────┘

✓ Car now visible in both canvas and sidebar!
```

## Key Architectural Principles

### 1. No Direct Model Access from Views
```
❌ Wrong:
CarModal(traffic_snapshot=snapshot)  # Direct access!
modal.get_roads_from_snapshot()

✓ Correct:
CarModal(get_roads=lambda: controller.snapshot.get_roads())
modal.get_roads()  # Calls callback, no direct reference
```

### 2. Controller as Mediator
```
View ←→ Controller ←→ Model
     (signals)  (commands)

View never talks to Model directly
Model never knows about View
Controller coordinates everything
```

### 3. Two-Stage Validation
```
Modal Validation (UI Layer):
- Non-empty strings
- Correct format (#RRGGBB)
- Number ranges
→ Fast feedback to user

Command Validation (Business Layer):
- Unique names
- Valid references (road exists)
- Lane indices in bounds
→ Data integrity enforcement
```

### 4. Signal-Based Updates
```
Model changes → Signal emitted
              → Controller receives
              → View updates

Automatic propagation
No manual refresh calls
Always consistent state
```

