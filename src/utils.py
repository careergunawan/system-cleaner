import os

def format_size(size_bytes):
    """Formats bytes to human readable string."""
    if size_bytes == 0: return "0 B"
    size_name = ("B", "KB", "MB", "GB", "TB")
    import math
    i = int(math.floor(math.log(size_bytes, 1024)))
    p = math.pow(1024, i)
    s = round(size_bytes / p, 2)
    return f"{s} {size_name[i]}"

def get_directory_size(directory, stop_event=None):
    """Calculates the total size of a directory recursively (iterative), with optional stop event."""
    total = 0
    stack = [directory]
    
    while stack:
        if stop_event and stop_event.is_set():
            return total
            
        current_dir = stack.pop()
        try:
            with os.scandir(current_dir) as it:
                for entry in it:
                    if stop_event and stop_event.is_set():
                        return total
                    try:
                        if entry.is_file(follow_symlinks=False):
                            total += entry.stat(follow_symlinks=False).st_size
                        elif entry.is_dir(follow_symlinks=False):
                            stack.append(entry.path)
                    except (PermissionError, OSError):
                        continue
        except (PermissionError, FileNotFoundError, OSError):
            continue
    return total
