# CLAUDE.md

## Project Purpose
This repository contains **ILT (Image Labelling Tool)** — a Python desktop application for image annotation and YOLO-format labeling. The goal is to maintain a clean, event-driven MVC architecture with strong separation between UI, controller, and utility logic.

## Tech Stack & Conventions
- **UI Framework**: Tkinter  
- **Image Processing**: OpenCV, Pillow, NumPy  
- **Architecture**: MVC + Event-driven  
- **Code Style**: PEP8, clear function/method names, comments for non-obvious logic  
- **Logging**: Use the provided `log_levels.py` system, keep messages in English  

## Key Modules
- **main.py** → Application entry point  
- **ILT_UI.py** → Tkinter UI components  
- **Controller.py** → Business logic & event dispatch  
- **bbox_controller.py** → Bounding box interactions  
- **label_display_utils.py** → YOLO label parsing/sorting  
- **config_utils.py** → Config.ini read/write  
- **folder_utils.py** → Folder/image scanning  
- **image_utils.py** → Image loading/conversion  

## Important Guidelines
- **Maintain MVC separation**  
  - UI code only in `ILT_UI.py`  
  - Business logic in `Controller.py`  
  - No mixing of file I/O logic with UI  
- **Preserve YOLO label compatibility**  
  - Labels stored as text files alongside images  
  - Auto-sorting (left-to-right within plates) must be preserved  
- **Respect configuration system**  
  - Do not break `config.ini` keys or sections  
  - Support lazy label file creation by default  
- **UI behavior**  
  - Use event-driven flow (keyboard/mouse events)  
  - Keep new features toggleable through config if relevant  
- **Dependencies**  
  - Do not add heavy new packages unless strictly necessary  
  - Keep Tkinter as the only UI framework  

## Restrictions
- Do not remove or rewrite the event system in `UI_event.py`  
- Do not alter the config file schema  
- Avoid introducing global state outside existing patterns  
