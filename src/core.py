import os
import shutil
from concurrent.futures import ThreadPoolExecutor, as_completed
from src.utils import get_directory_size

class CleanerCore:
    def __init__(self):
        # Base system paths
        self.categories = {
            "User Temp": {"path": os.environ.get('TEMP'), "desc": "Temporary files created by apps"},
            "System Temp": {"path": "C:\\Windows\\Temp", "desc": "Temporary files created by Windows"},
            "Windows Update": {"path": "C:\\Windows\\SoftwareDistribution\\Download", "desc": "Cached update files (safe to delete)"},
            "Prefetch": {"path": "C:\\Windows\\Prefetch", "desc": "Application launch cache"},
            "Recycle Bin": {"path": "C:\\$Recycle.Bin", "desc": "Deleted files in trash"}
        }

        # Developer-specific safe clean locations
        dev_data = {
            "npm Cache": {"path": os.path.join(os.environ.get('AppData', ''), 'npm-cache'), "desc": "Node.js package manager cache"},
            "pip Cache": {"path": os.path.join(os.environ.get('LocalAppData', ''), 'pip', 'Cache'), "desc": "Python package manager cache"},
            "NuGet Cache": {"path": os.path.join(os.path.expanduser('~'), '.nuget', 'packages'), "desc": "NuGet package cache (can be redownloaded)"},
            "Gradle Cache": {"path": os.path.join(os.path.expanduser('~'), '.gradle', 'caches'), "desc": "Gradle build system cache"},
            "Maven Repo": {"path": os.path.join(os.path.expanduser('~'), '.m2', 'repository'), "desc": "Maven local repository (can be redownloaded)"},
            "VS Code Cache": {"path": os.path.join(os.environ.get('AppData', ''), 'Code', 'Cache'), "desc": "Visual Studio Code internal cache"},
            "Android SDK Temp": {"path": os.path.join(os.environ.get('LocalAppData', ''), 'Android', 'Sdk', 'temp'), "desc": "Android SDK temporary download files"}
        }

        # Add existing dev data if paths exist
        for name, info in dev_data.items():
            if info["path"] and os.path.exists(info["path"]):
                self.categories[name] = info

        # Drive D Junk (if exists)
        if os.path.exists('D:'):
            d_junk = {
                "D: Recycle Bin": {"path": "D:\\$Recycle.Bin", "desc": "Deleted files in drive D trash"},
                "D: Temp": {"path": "D:\\Temp", "desc": "Temporary files on drive D"}
            }
            for name, info in d_junk.items():
                if os.path.exists(info["path"]):
                    self.categories[name] = info

        # Patterns for developer folders
        self.dev_patterns = ["node_modules", "vendor", "target", "bin", "obj", "__pycache__", ".next", ".nuxt", "dist", "build"]

    def scan_category(self, category_name, stop_event=None):
        if category_name in self.categories:
            path = self.categories[category_name]["path"]
            if os.path.exists(path):
                return get_directory_size(path, stop_event)
        return 0

    def scan_dev_folders(self, root_path, selected_patterns, stop_event=None):
        """Scans a directory for developer junk folders with stop support."""
        found_folders = []
        if not os.path.exists(root_path):
            return found_folders

        try:
            for root, dirs, files in os.walk(root_path):
                if stop_event and stop_event.is_set():
                    break
                # Optimization: Don't go deeper into folders we are already going to delete
                for d in list(dirs):
                    if stop_event and stop_event.is_set():
                        break
                    if d in selected_patterns:
                        full_path = os.path.join(root, d)
                        size = get_directory_size(full_path, stop_event)
                        found_folders.append({"path": full_path, "name": d, "size": size})
                        dirs.remove(d) 
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

    def analyze_disk(self, root_path, callback=None, stop_event=None):
        """Analyzes top-level folders in a drive using parallel processing."""
        if not os.path.exists(root_path):
            return

        try:
            items = os.listdir(root_path)
            # Filter items to scan
            to_scan = []
            root_files_size = 0

            for item in items:
                if stop_event and stop_event.is_set(): break
                item_path = os.path.join(root_path, item)
                
                if os.path.isfile(item_path):
                    try:
                        root_files_size += os.path.getsize(item_path)
                    except: pass
                elif os.path.isdir(item_path):
                    # Skip some system folders that are usually inaccessible and slow
                    if item.lower() in ["system volume information", "$recycle.bin", "config.msi"]:
                        continue
                    to_scan.append((item, item_path))

            if root_files_size > 0 and callback:
                callback({"name": "[Files in Root]", "path": root_path, "size": root_files_size})

            # Parallel scan of directories
            with ThreadPoolExecutor(max_workers=os.cpu_count() or 4) as executor:
                future_to_item = {executor.submit(get_directory_size, path, stop_event): name for name, path in to_scan}
                
                for future in as_completed(future_to_item):
                    if stop_event and stop_event.is_set():
                        executor.shutdown(wait=False)
                        break
                    
                    name = future_to_item[future]
                    path = os.path.join(root_path, name)
                    try:
                        size = future.result()
                        if callback:
                            callback({"name": name, "path": path, "size": size})
                    except Exception:
                        pass
        except Exception:
            pass
