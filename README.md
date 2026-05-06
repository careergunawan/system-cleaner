# AG System Cleaner

A lightweight, modern system cleanup utility for Windows.

## Features
- **Dynamic Scanning**: Scans common Windows junk locations.
- **Disk Analytics**: Shows real-time disk usage for Drive C:.
- **Modern UI**: Built with CustomTkinter for a premium feel.
- **Safe Cleaning**: Skips files that are currently in use by the system.

## Project Structure
- `main.py`: Entry point.
- `src/core.py`: Cleanup logic.
- `src/ui.py`: GUI components.
- `src/utils.py`: Helper functions.

## Setup
1. Install requirements:
   ```bash
   pip install -r requirements.txt
   ```
2. Run the application:
   ```bash
   python main.py
   ```

## Creating Executable
To use on other devices without Python, install `pyinstaller` and run:
```bash
pyinstaller --noconsole --onefile main.py
```
