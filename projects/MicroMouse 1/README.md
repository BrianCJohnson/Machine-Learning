##Micromouse simulation with visualization.

The project consists of 6 Python files:
- **MicroMouse.py**
  - the main program, contains most setup and main loop
- **maze.py**
  - defines a maze class object and methods
- **mouse.py**
  - defines a mouse object and methods
- **common.py**
  - defines a state object and methods
  - defines a vector object and methods
  - defines get_sensor_vectors()
  - defines some common helper functions
- **graph.py**:
  - defines a graph object and methods
- **display.py**
  - defines a display object and methods
  - sets up Tkinter
  - defines a number of display related functions
  
Running the Python code requires Tkinter, math, numpy, time, random, copy and Queue.

The following variables may be changed in MicroMouse.py:
- **maze_index**
  - selects which maze will be used, line 19
- **move_strategy_index**
  - selects which move strategy will be used, line 33
- **algorithm_index**
  - selects which algorithm will be used, line 39

The following variables may be changed in mouse.py:
- **with_markers**
  - enables display of search markers, line 63

There is also 1 Excel file:
- **Maze Editing Tool 20170206.xlsx**
  - Excel file that enables easy creation and editing of mazes
