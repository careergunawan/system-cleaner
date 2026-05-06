import os
import shutil
import pathlib

def clean_code_cache(root_dir):
    """
    Cleans Python code caches and temporary artifacts.
    """
    patterns = [
        "__pycache__",
        "*.pyc",
        "*.pyo",
        ".pytest_cache",
        ".ipynb_checkpoints",
        ".mypy_cache"
    ]
    
    print(f"🧹 Cleaning code cache in: {root_dir}")
    count = 0
    freed = 0

    for pattern in patterns:
        for path in pathlib.Path(root_dir).rglob(pattern):
            try:
                if path.is_file():
                    size = path.stat().st_size
                    path.unlink()
                    freed += size
                elif path.is_dir():
                    # Calculate size before deleting
                    for f in path.rglob('*'):
                        if f.is_file(): freed += f.stat().st_size
                    shutil.rmtree(path)
                
                print(f"  [DELETED] {path}")
                count += 1
            except Exception as e:
                print(f"  [SKIP] {path} (In use or permission denied)")

    print("-" * 30)
    print(f"Done! Cleaned {count} items.")
    print(f"Freed space: {freed / 1024:.2f} KB")

if __name__ == "__main__":
    # Target folder scripts (bisa disesuaikan)
    target = os.path.join(os.getcwd(), "src") # Default ke folder src
    if os.path.exists(target):
        clean_code_cache(target)
    else:
        # Jika folder src tidak ada, scan folder saat ini
        clean_code_cache(os.getcwd())
