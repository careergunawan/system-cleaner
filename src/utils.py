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

def get_directory_size(directory):
    """Calculates the total size of a directory recursively."""
    total = 0
    try:
        with os.scandir(directory) as it:
            for entry in it:
                if entry.is_file():
                    total += entry.stat().st_size
                elif entry.is_dir():
                    total += get_directory_size(entry.path)
    except (PermissionError, FileNotFoundError, OSError):
        pass
    return total
