# Program Installation and Setup

This file contatins a short explanation on how to setup and use
the UMLSL Traffic Editor Program.

## ⚙️ Installation Reqeuirements

To run the program the user must be able to run Python-3.11
files (Python must be installed). The user also must have installed
the PyQT6 library (installation in setup tutorial).

## 🔧 Setup Program

1. Clone Repository.
   
   bash:
   
   git clone https://github.com/69420pm/UMLSL-traffic-editor.git
   
2. Install library dependencies.

   bash:
   
   pip install PySide6

## ▶️ Run Program
   bash:
   
   python main.py

# Program Usage Guide

The purpose of the program is to allow the user to build a traffic
snapshot with cars, roads and intersections and evaluate queries
in the UMLSL language based on the built traffic snapshot.

## Transformation (Movement) in the Traffic Visual Editor

To move around the canvas, click and hold your left mouse button inside the Traffic Visual Editor.
Now move the mouse while holding the left mouse button to move around the whole canvas.
Alternatively you can press one of the arrow keys to move in the corresponding direction.

To zoom in or out of the canvas, click on the plus or minus buttons in the top right corner
of the Traffic Visual Editor. Alternatively you can scroll up our down with the mouse wheel
to achieve the same effect.

## Adding Cars, Roads And Queries

1. Navigate to the panel on the left of the User Interface of the Program with your mouse.
2. Click on the + button in one of the three lists depending on what you want to add.
3. Specify properties in the pop up dialog and click the confirmation button.
4. Car, Road or Query is added to the rendered traffic snapshot on the right and the corresponding list on the left.

## Editing or Removing Cars, Roads and Queries

1. Navigate to the panel on the left of the User Interface of the Program with your mouse.
2. Click on the pen icon next to the entity you want to edit in one of the lists.
3. Change properties in the pop up dialog and click the confirmation button or click delete button.

## Moving around Cars and Roads

Instead of manually editing the position property inside a road`s or car`s editing menu,
the user can also move them around in a more intuitive way with their mouse:

1. Click on the Car or Road you want to move in the Traffic Visual Editor or in the corresponding entity list to select it.
2. Click and hold your left mouse button.
3. Drag the selected road or car to a new position and release the left mouse button to drop it there.

## Changing Settings

1. Click on the Settings button in the top left of the application.
2. Click on the Setting you want to change in the pop up dialog.
3. Change the value of the setting.
4. Click on the Save button of the pop up dialog to save the change.

## Saving and loading a Traffic Snapshot Configuration

1. Click on the File button in the top left of the application.
2. Click on the Save, Save As or Load button depending on if you want to save to an existing file, save to a new file or load an existing file.
3. Select the file you want to save to / load from (or create a new one for Save As).
4. Click the confirmation button to save / load the configuration.
