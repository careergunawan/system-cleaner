"""
Giat Cleaner
Developed by: Gugun Gunawan, S.Kom
Description: A modern system and project cleanup utility.
"""
from src.ui import CleanerUI

if __name__ == "__main__":
    try:
        app = CleanerUI()
        app.mainloop()
    except KeyboardInterrupt:
        print("\nAplikasi dihentikan oleh pengguna.")
