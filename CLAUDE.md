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
- **bbox_controller.py** - Manages bounding box interactions (drawing, selection, dragging, resizing)
- **label_display_utils.py** - YOLO label parsing, sorting, and LabelObject management
- **Words_Label_mapping.py** - Character-to-class mapping for license plate annotation (0-9, A-Z)
- **config_utils.py** - Manages config.ini file operations
- **folder_utils.py** - Scans image folders and manages label files
- **image_utils.py** - Image loading, processing, and PIL conversion
- **log_levels.py** - Custom logging system

### Configuration
- **config.ini** - Stores application state (folders, current image, dimensions)
  - `[ImageInfo]` - Image dimensions
  - `[Path]` - Folder paths, current image index, selected class ID
  - `[preview_magnifier]` - Magnifier settings (enabled, zoom_factor, cursor_type, region_size, cache_size)
  - `[LabelFiles]` - Label file handling settings (auto_create_labels)
- **Label File Strategy**: Uses lazy creation approach
  - Label files are created only when actually needed (when saving labels)
  - Empty label files are handled based on `auto_create_labels` configuration (default: False)
  - Significantly improves performance when opening large datasets
- Supports JPG, JPEG, PNG image formats

## Application Features

### Navigation
- Arrow keys (Left/Right) for previous/next image
- Automatic image resizing with window
- Displays current image index

### Image Management
- **Delete Current Image**: Bottom toolbar "Delete" button removes current image file and associated label file
- Automatic navigation to next available image after deletion
- Confirmation dialog to prevent accidental deletion

### UI Components
- Top toolbar: "Reselect Folders", "Crop", "Add" buttons
- Main canvas with image display and bounding box visualization
- Right panel: Class ID selection buttons (0-9, A-Z) for character annotation (optional)
- Text box showing label content in YOLO format (optional)
- Bottom toolbar: "Delete" button for removing current image and associated labels
- Hint area with keyboard shortcuts (in Chinese)
- Status display: Shows drawing mode, selection status, and sorting feedback

**UI Configuration Options:**
- `SHOW_CLASS_ID_BUTTONS`: Toggle class ID button panel visibility
- `SHOW_TEXT_BOX`: Toggle text box visibility for streamlined interface
- `SHOW_PREVIEW`: Toggle original size preview panel visibility

### Bounding Box Features
- **Visualization**: Display YOLO format labels as colored bounding boxes with class ID
- **Selection**: Click to select boxes (red highlight)
- **Class ID Assignment**: Select character button (0-9, A-Z) to set box class
- **Drawing**: Two drawing modes available:
  - Left Ctrl: Toggle drawing mode on/off
  - Right Ctrl: Hold to enter drawing mode, release to exit
- **Deletion**: Delete key or right-click to remove selected box
- **Dragging**: Drag selected boxes to new positions
- **Resizing**: Drag gray corner handles to resize boxes
- **Auto-sorting**: Labels automatically sorted left-to-right on load and after operations
  - Supports multiple license plates with intelligent grouping
  - Uses 50% vertical overlap threshold for plate detection
  - Re-sorts after adding, deleting, or moving boxes

### Original Size Preview with Interactive Magnifier
- **Location**: Bottom-right corner of the interface
- **Basic Features**:
  - Shows images at their original size without scaling
  - Displays original image dimensions info in top-left corner
  - Automatically updates when loading new images
  - Scrollbars appear automatically when image exceeds preview panel size
- **Interactive Magnifier Features**:
  - **Smart Cursor**: Mouse cursor changes to target/crosshair when hovering over preview
  - **Left-click Zoom**: Click anywhere to display 3x magnified tooltip with boundary detection
  - **Right-drag Navigation**: Drag to navigate through images larger than the preview panel
  - **Performance Optimized**: LRU cache system for smooth magnification experience
- **Configuration**: 
  - Toggle via `SHOW_PREVIEW` configuration or `toggle_preview()` method
  - Magnifier settings in `[preview_magnifier]` config section (zoom factor, cursor type, cache size)

### Event System
Events are defined in `UI_event.py` and handled through the Controller:
- Keyboard events: LEFT/RIGHT navigation, Left/Right Ctrl modifiers, Delete key
- Mouse events: Left/right clicks, drag operations, bounding box interactions
- Button events: Toolbar button clicks, class ID selection, image deletion
- System events: Window ready, canvas resize
- Bounding box events: Drawing mode toggle, selection, deletion, dragging, resizing
- Magnifier events: MAGNIFIER_SHOW, MAGNIFIER_HIDE, PREVIEW_DRAG_START/DRAG/DRAG_END

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
2. Auto-sorting triggers:
   - On initial image load
   - After creating new bounding box
   - After deleting selected box
   - After dragging box to new position
3. Sorting algorithm:
   - Groups labels by vertical overlap (same license plate detection)
   - Sorts each group by X coordinate (left-to-right)
   - Saves sorted results back to label files
4. Visual feedback shows number of labels and detected plates

### Configuration Management
- Uses Python's configparser for config.ini
- Graceful error handling for missing/corrupt config files
- Automatic config creation with sensible defaults
- Improved error messages for Windows-specific issues (e.g., file path access errors)
- **Magnifier Configuration**: Full API in `config_utils.py` for managing preview magnifier settings
  - `get_magnifier_*()` functions for reading configuration
  - `save_magnifier_config()` for updating settings
  - Dynamic cursor switching with 7 available cursor types (target, dotbox, tcross, crosshair, plus, circle, sizing)
- **Label File Configuration**: Enhanced performance-oriented settings
  - `get_auto_create_labels()` and `set_auto_create_labels()` for controlling empty label file creation
  - Backward compatibility maintained for existing projects

### Performance Optimization
- **Lazy Label File Creation**: Advanced on-demand file creation strategy
  - Eliminated pre-creation of thousands of empty label files
  - Folder selection time reduced from minutes to seconds for large datasets
  - Memory usage optimized by avoiding unnecessary file operations
  - Files created only when labels are actually saved
- **Efficient Folder Scanning**: Only scans image files during folder selection
- **Configurable Behavior**: Users can choose between lazy creation (default) and eager creation modes
  - Use `config_utils.set_auto_create_labels(True)` to enable eager creation
  - Use `config_utils.set_auto_create_labels(False)` to enable lazy creation (recommended)