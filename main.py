from src.ui import CleanerUI

if __name__ == "__main__":
    try:
        app = CleanerUI()
        app.mainloop()
    except KeyboardInterrupt:
        print("\nAplikasi dihentikan oleh pengguna.")
