import os
import shutil
from src.utils import get_directory_size

class CleanerCore:
    def __init__(self):
        self.categories = {
            "User Temp": {"path": os.environ.get('TEMP'), "desc": "Temporary files created by apps"},
            "System Temp": {"path": "C:\\Windows\\Temp", "desc": "Temporary files created by Windows"},
            "Windows Update": {"path": "C:\\Windows\\SoftwareDistribution\\Download", "desc": "Cached update files (safe to delete)"},
            "Prefetch": {"path": "C:\\Windows\\Prefetch", "desc": "Application launch cache"},
            "Recycle Bin": {"path": "C:\\$Recycle.Bin", "desc": "Deleted files in trash"}
        }
        # Patterns for developer folders
        self.dev_patterns = ["node_modules", "vendor", "target", "bin", "obj", "__pycache__", ".next", ".nuxt", "dist", "build"]

    def scan_category(self, category_name):
        if category_name in self.categories:
            path = self.categories[category_name]["path"]
            if os.path.exists(path):
                return get_directory_size(path)
        return 0

    def scan_dev_folders(self, root_path, selected_patterns):
        """Scans a directory for developer junk folders."""
        found_folders = []
        if not os.path.exists(root_path):
            return found_folders

        try:
            for root, dirs, files in os.walk(root_path):
                # Optimization: Don't go deeper into folders we are already going to delete
                for d in list(dirs):
                    if d in selected_patterns:
                        full_path = os.path.join(root, d)
                        size = get_directory_size(full_path)
                        found_folders.append({"path": full_path, "name": d, "size": size})
                        dirs.remove(d) # Don't recurse into found folder
        except Exception:
            pass
        return found_folders

    def clean_path(self, path):
        """Generic path cleaner."""
        freed = 0
        if os.path.exists(path):
            initial_size = get_directory_size(path)
            try:
                if os.path.isfile(path) or os.path.islink(path):
                    os.unlink(path)
                elif os.path.isdir(path):
                    shutil.rmtree(path)
            except Exception:
                pass
            final_size = get_directory_size(path)
            freed = initial_size - final_size
        return freed

    def clean_category(self, category_name):
        # ... (same as before but using clean_path internally)
        freed = 0
        if category_name in self.categories:
            path = self.categories[category_name]["path"]
            if os.path.exists(path):
                try:
                    for filename in os.listdir(path):
                        freed += self.clean_path(os.path.join(path, filename))
                except Exception:
                    pass
        return freed
