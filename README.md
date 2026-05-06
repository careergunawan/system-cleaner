# Giat Cleaner 🚀

A lightweight, modern system cleanup utility for Windows, designed for developers and power users.

## 👤 Author
**Gugun Gunawan, S.Kom**
*Developer & System Optimizer*

---

## 🌟 Features
- **System Junk Cleanup**: Scan and remove Windows temp files, update cache, and prefetch data safely.
- **Developer Mode (Dev Cleaner)**: Recursively find and delete heavy folders like `node_modules`, `vendor`, `target`, `bin/obj`, and more.
- **Dynamic Path Selection**: Point the cleaner to any drive or project directory.
- **Disk Analytics**: Real-time monitoring of Drive C: storage.
- **Safety First**: Includes security confirmation dialogs and skips files currently in use.
- **Modern UI**: Dark/Light mode support with a premium responsive interface.

## 🛠️ Project Structure
- `main.py`: Main application entry point.
- `src/core.py`: Cleanup and scanning logic.
- `src/ui.py`: CustomTkinter GUI implementation.
- `src/utils.py`: Utility functions for file operations.
- `scripts/clean_scripts.py`: Standalone CLI tool for cleaning code cache.

## 🚀 Setup & Installation
1. Clone this repository.
2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```
3. Run the application:
   ```bash
   python main.py
   ```

## 📦 Creating a Standalone Executable
To use this tool on any Windows machine without Python installed:
1. Install PyInstaller: `pip install pyinstaller`
2. Build the exe:
   ```bash
   pyinstaller --noconsole --onefile --name "AG_System_Cleaner" main.py
   ```

## 📜 License
This project is open-source and available under the **MIT License**.

---
*Developed with ❤️ for the Developer Community.*
