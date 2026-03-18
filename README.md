# UMLSL Traffic Editor

A visual editor for building traffic snapshots (cars, roads, and intersections) and evaluating UMLSL language queries.

## Installation

**Prerequisites:** Python 3.11+

1. Clone the repository:
   ```bash
   git clone [https://github.com/69420pm/UMLSL-traffic-editor.git](https://github.com/69420pm/UMLSL-traffic-editor.git)
   cd UMLSL-traffic-editor
   ```
2. *(Recommended)* Create and activate a virtual environment.
3. Install the required dependencies:
   ```bash
   pip install -r requirements.txt
   ```

## Running the Program

Run the application from the root directory:

```bash
python -m pse.umlsl_editor.main
```

**Open a file directly:**
Launch the editor and load a specific traffic snapshot by passing the file path as an argument:
```bash
python -m pse.umlsl_editor.main <path/to/snapshot_file>
```

## Editor Features & Navigation

* **Canvas Navigation:** Click and drag the left mouse button or use the arrow keys to pan across the canvas. Zoom using the mouse wheel or the `+`/`-` buttons.
* **Entity Management:** Use the left panel to manage your environment. Click `+` to add entities, or use the pen icon to edit/delete them.
* **Drag & Drop:** Select any car or road and drag it with the mouse to quickly reposition it.
* **Settings & Files:** Access `Settings` and `File` management (`Load`, `Save`, `Save As`) from the top-left menu.

## Keyboard Shortcuts

| Action | Shortcut |
| :--- | :--- |
| Add Car | `C` |
| Add Road | `R` |
| Add Query | `Q` |
| Edit Selected | `E` |
| Delete Selected | `Backspace` |
