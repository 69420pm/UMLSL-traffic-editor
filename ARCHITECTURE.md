# Architecture Documentation

This document provides a comprehensive overview of the architecture for the UMLSL Traffic Editor. It focuses on the backend structure and the communication patterns between the frontend (View) and the backend (Core/Controllers).

## 1. Architecture Overview

The application follows a **Model-View-Controller (MVC)** pattern, enhanced with the **Command Pattern** for state modifications and an **Observer Pattern** (via Signals) for state updates.

### High-Level Components

*   **Core (Model)**: The single source of truth for the application state (`TrafficSnapshot`). It holds all data about cars, roads, and queries.
*   **View**: The user interface (PySide6 widgets and graphics view). *Note: The view implementation is currently in progress.*
*   **Controllers**: The glue layer that manages communication between the View and the Model.
*   **Commands**: Encapsulated actions that modify the Model.

---

## 2. Backend Architecture

### 2.1 Core (The Model)

The heart of the application is the `TrafficSnapshot` class located in `src/core/traffic_snapshot.py`.

*   **Role**: Represents the complete state of the traffic simulation at a specific point in time.
*   **Data Structures**: Uses `ObservableDict` and `ObservableList` to store entities (Cars, Roads, Queries).
*   **Interfaces**:
    *   `TrafficSnapshotReader`: Interface for reading data (used by Commands/Validators).
    *   `TrafficSnapshotWriter`: Interface for writing data (used by Commands).
*   **Signals**: Inherits from `QObject` and defines PySide signals to notify listeners of changes:
    *   `car_added`, `car_removed`, `car_updated`
    *   `road_added`, `road_removed`, `road_updated`
    *   `umlsl_query_added`, ...

**Key Concept**: The `TrafficSnapshot` is the **only** place where state is stored. The frontend should never store its own version of the data, but rather display what is in the snapshot.

### 2.2 Controllers

The application uses a set of specialized controllers to manage different aspects of the application logic. These are located in `src/controllers`.

#### `ApplicationController` (Facade)
*   **Location**: `src/controllers/application_controller.py`
*   **Role**: The main entry point for the frontend. It inherits from both `ViewController` and `CommandController`, providing a unified interface.
*   **Usage**: The frontend should primarily interact with this class.

#### `CommandController` (Write Operations)
*   **Location**: `src/controllers/command_controller.py`
*   **Role**: Handles the execution of commands.
*   **Responsibilities**:
    *   Receives requests to modify the model (e.g., `add_car`).
    *   Instantiates the appropriate `Command` object.
    *   Executes the command via `execute_command()` (which handles validation and potentially undo/redo history).
*   **API**: Exposes high-level methods like `add_car(...)` that the frontend calls.

#### `ViewController` (Update Synchronization)
*   **Location**: `src/controllers/view_controller.py`
*   **Role**: Synchronizes the Model state to the View.
*   **Mechanism**: Connects `TrafficSnapshot` signals directly to `TrafficView` methods.
    *   Example: `traffic_snapshot.car_added` -> `view.add_car_view`
*   **Philosophy**: "Don't call us, we'll call you." The View doesn't manually ask for updates; it reacts to signals.

#### `DataController` (Read Operations)
*   **Location**: `src/controllers/data_controller.py`
*   **Role**: Provides read-only access to the model data.
*   **Usage**: Used by the View to populate lists, inspect object details, or render the initial state. It does **not** modify data.

### 2.3 Commands

All state modifications are encapsulated in **Command** objects located in `src/commands`.

*   **Base Class**: `Command[ReturnValue]` in `src/commands/command.py`.
*   **Structure**:
    *   `validate()`: Checks if the command can be executed (raises `CommandValidationError`).
    *   `execute()`: Performs the actual modification on the `TrafficSnapshot`.
*   **Benefits**: Decouples the "what" (action) from the "how" (execution), enabling validation, undo/redo, and logging.

---

## 3. Frontend-Backend Communication Guide

This section is specifically for frontend developers implementing the UI.

### 3.1 How to Modify Data (Frontend -> Backend)

**Do NOT modify the `TrafficSnapshot` directly.** Always go through the `ApplicationController`.

1.  **User Action**: User clicks "Add Car" in the UI.
2.  **Call Controller**: The View calls the corresponding method on the `ApplicationController`.
    ```python
    # Example in a View class
    self.controller.add_car(
        name="Car1",
        assigned_road=some_road,
        ...
    )
    ```
3.  **Processing**:
    *   The `ApplicationController` (via `CommandController`) creates an `AddCarCommand`.
    *   It calls `command.validate()`. If invalid, an error is raised (handle this in the UI!).
    *   It calls `command.execute()`.
    *   The `TrafficSnapshot` is updated.

### 3.2 How to Receive Updates (Backend -> Frontend)

**Do NOT manually refresh the UI after a command.** Rely on signals.

1.  **Model Change**: The `TrafficSnapshot` updates its internal dictionary.
2.  **Signal Emission**: `TrafficSnapshot` emits a signal, e.g., `car_added(Car)`.
3.  **View Update**:
    *   The `ViewController` has already connected this signal to a method in your View (e.g., `view.add_car_view(car)`).
    *   Your `add_car_view` method receives the new `Car` data object.
    *   **Action**: Create the visual representation (widget/graphics item) for this car.

### 3.3 How to Read Data (Frontend -> Backend)

For initializing views or populating property panels, use the `DataController` methods exposed via `ApplicationController`.

*   **Example**: Populating a list of cars.
    ```python
    cars = self.controller.get_all_cars()
    for car in cars:
        self.add_car_to_list(car)
    ```

---

## 4. Implementation Guide: Adding a New Feature

Scenario: You want to add a "Traffic Light" entity.

### Step 1: Define the Data (Core)
1.  Create `src/core/dataclasses/traffic_light.py`.
2.  Update `TrafficSnapshot`:
    *   Add `_traffic_lights = ObservableDict(...)`.
    *   Add signals: `traffic_light_added`, `traffic_light_removed`, `traffic_light_updated`.
    *   Implement `add_traffic_light`, `remove_traffic_light` methods in the writer interface.

### Step 2: Create the Command (Commands)
1.  Create `src/commands/traffic_lights/add_traffic_light.py`.
2.  Implement `AddTrafficLightCommand` inheriting from `Command`.
3.  Implement `validate()` (check for duplicates, valid position).
4.  Implement `execute()` (call `traffic_snapshot.add_traffic_light`).

### Step 3: Expose in Controller (Controllers)
1.  Update `CommandController`:
    *   Add method `add_traffic_light(...)`.
    *   Inside, instantiate and execute `AddTrafficLightCommand`.

### Step 4: Update View Controller (Controllers)
1.  Update `ViewController`:
    *   Connect `traffic_snapshot.traffic_light_added` to `view.add_traffic_light_view`.

### Step 5: Implement View (View)
1.  Update `TrafficView` interface to include `add_traffic_light_view`.
2.  Implement the UI logic to call `controller.add_traffic_light(...)`.

---

## 5. Directory Structure Summary

*   `src/core`: **Model**. `TrafficSnapshot`, Data Classes.
*   `src/controllers`: **Logic**. `ApplicationController`, `CommandController`, `ViewController`.
*   `src/commands`: **Actions**. `AddCar`, `DeleteRoad`, etc.
*   `src/view`: **UI**. Windows, Widgets, Canvas.
*   `src/persistence`: **IO**. Saving/Loading snapshots.

