import customtkinter as ctk
import tkinter as tk
from tkinter import filedialog
import threading
import psutil
import os
from src.utils import format_size
from src.core import CleanerCore

class CleanerUI(ctk.CTk):
    def __init__(self):
        super().__init__()

        # Window Config
        self.title("AG System Cleaner")
        self.geometry("950x650")
        
        # Core Logic
        self.core = CleanerCore()
        
        # UI State
        self.selected_vars = {name: tk.BooleanVar(value=True) for name in self.core.categories}
        self.category_labels = {}
        self.found_dev_items = []
        
        self.setup_layout()
        self.update_disk_stats()

    def setup_layout(self):
        self.grid_columnconfigure(1, weight=1)
        self.grid_rowconfigure(0, weight=1)

        # --- Sidebar ---
        self.sidebar = ctk.CTkFrame(self, width=220, corner_radius=0)
        self.sidebar.grid(row=0, column=0, sticky="nsew")
        
        self.logo = ctk.CTkLabel(self.sidebar, text="AG CLEANER", font=ctk.CTkFont(size=24, weight="bold"))
        self.logo.pack(pady=40, padx=20)

        # Disk Stats in Sidebar
        self.stats_box = ctk.CTkFrame(self.sidebar, fg_color="transparent")
        self.stats_box.pack(pady=10, padx=20, fill="x")
        self.free_lbl = ctk.CTkLabel(self.stats_box, text="Free: -- GB", font=("Arial", 14, "bold"), text_color="#2ecc71")
        self.free_lbl.pack()

        # Theme Switcher
        self.appearance_mode_menu = ctk.CTkOptionMenu(self.sidebar, values=["Dark", "Light", "System"], command=self.change_appearance)
        self.appearance_mode_menu.pack(side="bottom", padx=20, pady=20)
        self.appearance_mode_menu.set("Dark")

        # --- Main Content ---
        self.tabview = ctk.CTkTabview(self, corner_radius=15)
        self.tabview.grid(row=0, column=1, sticky="nsew", padx=20, pady=20)
        
        self.tab_system = self.tabview.add("System Cleanup")
        self.tab_projects = self.tabview.add("Project Cleanup (Dev)")

        self.setup_system_tab()
        self.setup_projects_tab()

        # Global Status Bar & Progress
        self.status_bar = ctk.CTkLabel(self, text="Ready to scan...", font=("Arial", 12, "italic"))
        self.status_bar.grid(row=1, column=1, pady=(0, 5))
        
        self.progress = ctk.CTkProgressBar(self)
        self.progress.grid(row=2, column=1, sticky="ew", padx=40, pady=(0, 20))
        self.progress.set(0)

    def setup_system_tab(self):
        self.tab_system.grid_columnconfigure(0, weight=1)
        
        self.btn_scan_sys = ctk.CTkButton(self.tab_system, text="🔍 Scan System Files", height=40, command=self.run_scan)
        self.btn_scan_sys.pack(pady=10, padx=20)

        self.scroll_sys = ctk.CTkScrollableFrame(self.tab_system, label_text="System Junk Locations")
        self.scroll_sys.pack(fill="both", expand=True, padx=10, pady=10)

        for name, info in self.core.categories.items():
            item = ctk.CTkFrame(self.scroll_sys, fg_color="transparent")
            item.pack(fill="x", pady=5)
            cb = ctk.CTkCheckBox(item, text=name, variable=self.selected_vars[name])
            cb.pack(side="left")
            lbl = ctk.CTkLabel(item, text="-- MB")
            lbl.pack(side="right")
            self.category_labels[name] = lbl

        self.btn_clean_sys = ctk.CTkButton(self.tab_system, text="✨ Clean Selected", fg_color="#e74c3c", command=self.run_clean)
        self.btn_clean_sys.pack(pady=10)

    def setup_projects_tab(self):
        self.tab_projects.grid_columnconfigure(0, weight=1)

        path_frame = ctk.CTkFrame(self.tab_projects, fg_color="transparent")
        path_frame.pack(fill="x", padx=20, pady=10)
        
        self.project_path_var = tk.StringVar(value="E:\\projects")
        self.path_entry = ctk.CTkEntry(path_frame, textvariable=self.project_path_var, placeholder_text="Select projects directory...")
        self.path_entry.pack(side="left", fill="x", expand=True, padx=(0, 10))
        
        self.btn_browse = ctk.CTkButton(path_frame, text="Browse", width=80, command=self.browse_path)
        self.btn_browse.pack(side="right")

        self.pattern_vars = {p: tk.BooleanVar(value=True) for p in self.core.dev_patterns}
        pattern_frame = ctk.CTkFrame(self.tab_projects)
        pattern_frame.pack(fill="x", padx=20, pady=5)
        
        grid_container = ctk.CTkFrame(pattern_frame, fg_color="transparent")
        grid_container.pack(fill="x", padx=10, pady=5)
        
        cols = 4
        for i, p in enumerate(self.core.dev_patterns):
            cb = ctk.CTkCheckBox(grid_container, text=p, variable=self.pattern_vars[p], font=("Arial", 11))
            cb.grid(row=i//cols, column=i%cols, padx=10, pady=5, sticky="w")

        self.btn_scan_dev = ctk.CTkButton(self.tab_projects, text="🔎 Scan Dev Folders", command=self.run_dev_scan)
        self.btn_scan_dev.pack(pady=10)

        self.dev_scroll = ctk.CTkScrollableFrame(self.tab_projects, label_text="Found Project Junk")
        self.dev_scroll.pack(fill="both", expand=True, padx=10, pady=10)

        self.btn_clean_dev = ctk.CTkButton(self.tab_projects, text="🗑️ Delete Found Folders", fg_color="#e74c3c", command=self.run_dev_clean)
        self.btn_clean_dev.pack(pady=10)

    def browse_path(self):
        path = filedialog.askdirectory()
        if path:
            self.project_path_var.set(path)

    def update_disk_stats(self):
        try:
            usage = psutil.disk_usage('C:')
            if hasattr(self, 'free_lbl'):
                self.free_lbl.configure(text=f"C: Free: {usage.free / (1024**3):.1f} GB")
        except Exception:
            pass

    def run_scan(self):
        self.btn_scan_sys.configure(state="disabled")
        self.status_bar.configure(text="Scanning system files...")
        threading.Thread(target=self._scan_thread, daemon=True).start()

    def _scan_thread(self):
        items = list(self.core.categories.keys())
        for i, name in enumerate(items):
            size = self.core.scan_category(name)
            self.category_labels[name].configure(text=format_size(size))
            self.progress.set((i + 1) / len(items))
        self.status_bar.configure(text="Scan completed!")
        self.btn_scan_sys.configure(state="normal")

    def run_clean(self):
        self.btn_clean_sys.configure(state="disabled")
        self.status_bar.configure(text="Starting cleanup...")
        threading.Thread(target=self._clean_thread, daemon=True).start()

    def _clean_thread(self):
        selected = [n for n, v in self.selected_vars.items() if v.get()]
        total_freed = 0
        for i, name in enumerate(selected):
            freed = self.core.clean_category(name)
            total_freed += freed
            new_size = self.core.scan_category(name)
            self.category_labels[name].configure(text=format_size(new_size))
            self.progress.set((i + 1) / len(selected))
        self.update_disk_stats()
        self.status_bar.configure(text=f"Done! Freed {format_size(total_freed)}")
        self.btn_clean_sys.configure(state="normal")

    def run_dev_scan(self):
        self.btn_scan_dev.configure(state="disabled")
        for widget in self.dev_scroll.winfo_children(): widget.destroy()
        self.found_dev_items = []
        threading.Thread(target=self._dev_scan_thread, daemon=True).start()

    def _dev_scan_thread(self):
        root = self.project_path_var.get()
        selected_patterns = [p for p, v in self.pattern_vars.items() if v.get()]
        found = self.core.scan_dev_folders(root, selected_patterns)
        for item in found:
            row = ctk.CTkFrame(self.dev_scroll, fg_color="transparent")
            row.pack(fill="x", pady=2)
            var = tk.BooleanVar(value=True)
            cb = ctk.CTkCheckBox(row, text=f"{item['name']} ({os.path.basename(os.path.dirname(item['path']))})", variable=var)
            cb.pack(side="left")
            size_lbl = ctk.CTkLabel(row, text=format_size(item['size']))
            size_lbl.pack(side="right")
            self.found_dev_items.append({"path": item['path'], "var": var, "lbl": size_lbl})
        self.status_bar.configure(text=f"Scan complete. Found {len(found)} folders.")
        self.btn_scan_dev.configure(state="normal")

    def run_dev_clean(self):
        self.btn_clean_dev.configure(state="disabled")
        threading.Thread(target=self._dev_clean_thread, daemon=True).start()

    def _dev_clean_thread(self):
        to_clean = [i for i in self.found_dev_items if i['var'].get()]
        freed_total = 0
        for i, item in enumerate(to_clean):
            freed = self.core.clean_path(item['path'])
            freed_total += freed
            item['lbl'].configure(text="CLEANED", text_color="#2ecc71")
            self.progress.set((i + 1) / len(to_clean))
        self.update_disk_stats()
        self.status_bar.configure(text=f"Finished! Freed {format_size(freed_total)}")
        self.btn_clean_dev.configure(state="normal")

    def change_appearance(self, mode):
        ctk.set_appearance_mode(mode)
