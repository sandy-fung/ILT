# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

This is the **ILT (Image Labelling Tool)** - a Python desktop application for image annotation and labeling. The tool provides a GUI interface for navigating through images, viewing/editing labels, and managing image-label datasets.

## Development Setup

### Environment
- Uses Python 3.10 with a virtual environment located at `venv/`
- Activate with: `source venv/bin/activate` (Linux/Mac) or `venv\Scripts\activate` (Windows)

### Dependencies
The project uses these key packages (installed in venv):
- **opencv-python** (4.12.0.88) - Image processing
- **pillow** (11.3.0) - Image manipulation for Tkinter
- **numpy** (2.2.6) - Array operations
- **tkinter** - GUI framework (built-in)

### Running the Application
```bash
source venv/bin/activate
python main.py
```

## Architecture

### MVC Pattern with Event-Driven Design
- **View**: `ILT_UI.py` - Tkinter GUI components and user interactions
- **Controller**: `Controller.py` - Business logic and event coordination
- **Model**: Configuration and utility modules
- **Events**: `UI_event.py` defines event types using Enum for loose coupling

### Key Components
- **main.py** - Entry point, initializes UI and Controller
- **ILT_UI.py** - Complete UI implementation with canvas, toolbar, and controls
- **Controller.py** - Handles all business logic, image navigation, and event dispatching
- **config_utils.py** - Manages config.ini file operations
- **folder_utils.py** - Scans image folders and manages label files
- **image_utils.py** - Image loading, processing, and PIL conversion
- **log_levels.py** - Custom logging system

### Configuration
- **config.ini** - Stores application state (folders, current image, dimensions)
- Automatically creates empty .txt label files for images without labels
- Supports JPG, JPEG, PNG image formats

## Application Features

### Navigation
- Arrow keys (Left/Right) for previous/next image
- Automatic image resizing with window
- Displays current image index

### UI Components
- Top toolbar: "Reselect Folders", "Crop", "Add" buttons
- Main canvas with image display and bounding box visualization
- Text box showing label content
- Hint area with keyboard shortcuts (in Chinese)

### Bounding Box Features
- **Visualization**: Display YOLO format labels as colored bounding boxes
- **Selection**: Click to select boxes (red highlight)
- **Drawing**: Ctrl key toggles drawing mode for creating new boxes
- **Deletion**: Delete key or right-click to remove selected box
- **Dragging**: Drag selected boxes to new positions
- **Resizing**: Drag corner handles to resize boxes
- **Auto-sorting**: Labels automatically sorted left-to-right on load
  - Supports multiple license plates with intelligent grouping
  - Uses 50% vertical overlap threshold for plate detection

### Event System
Events are defined in `UI_event.py` and handled through the Controller:
- Keyboard events: LEFT/RIGHT navigation, Ctrl modifiers, Delete key
- Mouse events: Left/right clicks, drag operations
- Button events: Toolbar button clicks
- System events: Window ready, canvas resize

## Development Notes

### Code Organization
- UI logic is contained in `ILT_UI.py` with clear separation from business logic
- Utility functions are modularized by responsibility
- Event-driven architecture allows for easy feature extension

### Image Processing Flow
1. `folder_utils.py` scans for image files
2. `image_utils.py` loads with OpenCV and converts to PIL
3. `ILT_UI.py` displays on Tkinter canvas with auto-resize
4. Labels are read/written as text files alongside images

### Label Processing Flow
1. `label_display_utils.py` parses YOLO format labels into LabelObject instances
2. Auto-sorting on load:
   - Groups labels by vertical overlap (same license plate detection)
   - Sorts each group by X coordinate (left-to-right)
   - Saves sorted results back to label files
3. Visual feedback shows number of labels and detected plates

### Configuration Management
- Uses Python's configparser for config.ini
- Graceful error handling for missing/corrupt config files
- Automatic config creation with sensible defaults