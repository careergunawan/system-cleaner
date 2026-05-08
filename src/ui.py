import customtkinter as ctk
import tkinter as tk
from tkinter import filedialog, messagebox
import threading
import psutil
import os
from src.utils import format_size
from src.core import CleanerCore

class CleanerUI(ctk.CTk):
    def __init__(self):
        super().__init__()

        # Window Config
        self.title("Giat Cleaner - by Gugun Gunawan, S.Kom")
        self.geometry("950x680")
        
        # Core Logic
        self.core = CleanerCore()
        
        # UI State
        self.stop_event = threading.Event()
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
        
        self.logo = ctk.CTkLabel(self.sidebar, text="GIAT CLEANER", font=ctk.CTkFont(size=24, weight="bold"))
        self.logo.pack(pady=(40, 10), padx=20)
        
        self.ver = ctk.CTkLabel(self.sidebar, text="v1.0.0 Public Release", font=ctk.CTkFont(size=10), text_color="gray")
        self.ver.pack(pady=(0, 20))

        self.stats_box = ctk.CTkFrame(self.sidebar, fg_color="transparent")
        self.stats_box.pack(pady=10, padx=20, fill="x")
        self.drive_labels = {} # Store labels by drive letter

        self.btn_stop = ctk.CTkButton(self.sidebar, text="🛑 Batalkan Proses", fg_color="#e67e22", hover_color="#d35400", command=self.stop_process, state="disabled")
        self.btn_stop.pack(pady=20, padx=20, fill="x")

        # Author Info
        self.author_box = ctk.CTkFrame(self.sidebar, fg_color="transparent")
        self.author_box.pack(side="bottom", fill="x", pady=(10, 20), padx=20)
        ctk.CTkLabel(self.author_box, text="Developed by:", font=("Arial", 10, "italic"), text_color="gray").pack()
        ctk.CTkLabel(self.author_box, text="Gugun Gunawan, S.Kom", font=("Arial", 11, "bold")).pack()

        # Theme Switcher
        self.appearance_mode_menu = ctk.CTkOptionMenu(self.sidebar, values=["Dark", "Light", "System"], command=self.change_appearance)
        self.appearance_mode_menu.pack(side="bottom", padx=20, pady=10)
        self.appearance_mode_menu.set("Dark")

        # --- Main Content ---
        self.tabview = ctk.CTkTabview(self, corner_radius=15)
        self.tabview.grid(row=0, column=1, sticky="nsew", padx=20, pady=20)
        
        self.tab_system = self.tabview.add("System Cleanup")
        self.tab_projects = self.tabview.add("Project Cleanup (Dev)")
        self.tab_analyzer = self.tabview.add("Disk Analyzer")

        self.setup_system_tab()
        self.setup_projects_tab()
        self.setup_analyzer_tab()

        self.status_bar = ctk.CTkLabel(self, text="Ready to scan...", font=("Arial", 12, "italic"))
        self.status_bar.grid(row=1, column=1, pady=(0, 5))
        
        self.progress = ctk.CTkProgressBar(self)
        self.progress.grid(row=2, column=1, sticky="ew", padx=40, pady=(0, 20))
        self.progress.set(0)

    def setup_system_tab(self):
        self.tab_system.grid_columnconfigure(0, weight=1)
        self.btn_scan_sys = ctk.CTkButton(self.tab_system, text="🔍 Scan System Files", height=40, command=self.run_scan, font=("Arial", 13, "bold"))
        self.btn_scan_sys.pack(pady=10, padx=20)
        
        self.scroll_sys = ctk.CTkScrollableFrame(self.tab_system, label_text="System Junk Locations", label_font=("Arial", 12, "bold"))
        self.scroll_sys.pack(fill="both", expand=True, padx=10, pady=10)
        
        for name, info in self.core.categories.items():
            item = ctk.CTkFrame(self.scroll_sys, fg_color=("gray95", "#2b2b2b"), height=40)
            item.pack(fill="x", pady=2, padx=5)
            
            cb = ctk.CTkCheckBox(item, text=name, variable=self.selected_vars[name], font=("Arial", 12))
            cb.pack(side="left", padx=10, pady=5)
            
            lbl = ctk.CTkLabel(item, text="-- MB", font=("Arial", 12, "bold"), text_color=("#34495e", "#bdc3c7"))
            lbl.pack(side="right", padx=15)
            self.category_labels[name] = lbl
            
        self.btn_clean_sys = ctk.CTkButton(self.tab_system, text="✨ Clean Selected", fg_color="#e74c3c", hover_color="#c0392b", command=self.run_clean, height=40, font=("Arial", 13, "bold"))
        self.btn_clean_sys.pack(pady=10)

    def setup_projects_tab(self):
        self.tab_projects.grid_columnconfigure(0, weight=1)
        path_frame = ctk.CTkFrame(self.tab_projects, fg_color="transparent")
        path_frame.pack(fill="x", padx=20, pady=10)
        
        self.project_path_var = tk.StringVar(value="E:\\projects")
        self.path_entry = ctk.CTkEntry(path_frame, textvariable=self.project_path_var, placeholder_text="Select projects directory...", height=35)
        self.path_entry.pack(side="left", fill="x", expand=True, padx=(0, 10))
        
        self.btn_browse = ctk.CTkButton(path_frame, text="📁 Browse", width=100, height=35, command=self.browse_path)
        self.btn_browse.pack(side="right")
        
        self.pattern_vars = {p: tk.BooleanVar(value=True) for p in self.core.dev_patterns}
        
        pattern_frame = ctk.CTkFrame(self.tab_projects, fg_color=("gray95", "#2b2b2b"))
        pattern_frame.pack(fill="x", padx=20, pady=5)
        
        ctk.CTkLabel(pattern_frame, text="Folder Patterns to Scan:", font=("Arial", 11, "bold")).pack(pady=(5, 0))
        
        grid_container = ctk.CTkFrame(pattern_frame, fg_color="transparent")
        grid_container.pack(fill="x", padx=10, pady=5)
        
        cols = 5
        for i, p in enumerate(self.core.dev_patterns):
            cb = ctk.CTkCheckBox(grid_container, text=p, variable=self.pattern_vars[p], font=("Arial", 10), width=100)
            cb.grid(row=i//cols, column=i%cols, padx=5, pady=5, sticky="w")
            
        btn_frame = ctk.CTkFrame(self.tab_projects, fg_color="transparent")
        btn_frame.pack(pady=10)
        
        self.btn_scan_dev = ctk.CTkButton(btn_frame, text="🔎 Scan Dev Folders", command=self.run_dev_scan, width=180, height=40, font=("Arial", 13, "bold"))
        self.btn_scan_dev.pack(side="left", padx=10)
        
        self.btn_clean_dev = ctk.CTkButton(btn_frame, text="🗑️ Delete Found Folders", fg_color="#e74c3c", hover_color="#c0392b", command=self.run_dev_clean, width=180, height=40, font=("Arial", 13, "bold"))
        self.btn_clean_dev.pack(side="left", padx=10)
        
        self.dev_scroll = ctk.CTkScrollableFrame(self.tab_projects, label_text="Found Project Junk", label_font=("Arial", 12, "bold"))
        self.dev_scroll.pack(fill="both", expand=True, padx=10, pady=10)

    def setup_analyzer_tab(self):
        self.tab_analyzer.grid_columnconfigure(0, weight=1)
        
        header = ctk.CTkFrame(self.tab_analyzer, fg_color="transparent")
        header.pack(fill="x", padx=20, pady=10)
        
        self.analyzer_path_var = tk.StringVar(value="C:\\")
        self.analyzer_path_entry = ctk.CTkEntry(header, textvariable=self.analyzer_path_var)
        self.analyzer_path_entry.pack(side="left", fill="x", expand=True, padx=(0, 10))
        
        self.btn_analyze = ctk.CTkButton(header, text="📊 Analyze Drive", width=120, command=self.run_analysis)
        self.btn_analyze.pack(side="right")
        
        self.analyzer_scroll = ctk.CTkScrollableFrame(self.tab_analyzer, label_text="Folder Usage Analysis")
        self.analyzer_scroll.pack(fill="both", expand=True, padx=10, pady=10)

    def run_analysis(self):
        self.set_busy(True)
        self.btn_analyze.configure(state="disabled")
        for widget in self.analyzer_scroll.winfo_children(): widget.destroy()
        threading.Thread(target=self._analysis_thread, daemon=True).start()

    def _analysis_thread(self):
        root = self.analyzer_path_var.get()
        self.status_bar.configure(text=f"Analyzing {root}... Folder akan muncul satu per satu.")
        
        self.analysis_results = []
        self.max_analysis_size = 1

        def update_ui_callback(item):
            # This runs in the worker thread, but CTk handles thread-safe updates for most things
            # or we use after() for sorting and re-rendering
            self.analysis_results.append(item)
            self.analysis_results.sort(key=lambda x: x['size'], reverse=True)
            self.after(0, self._render_analysis_results)

        self.core.analyze_disk(root, callback=update_ui_callback, stop_event=self.stop_event)
        
        self.status_bar.configure(text="Analisis selesai!" if not self.stop_event.is_set() else "Analisis dibatalkan.")
        self.btn_analyze.configure(state="normal")
        self.set_busy(False)

    def _render_analysis_results(self):
        # Clear and re-render the scroll frame (debounced or simplified)
        # To avoid flickering, we can just update existing or only render top 50
        for widget in self.analyzer_scroll.winfo_children():
            widget.destroy()
        
        if not self.analysis_results:
            return

        self.max_analysis_size = max(item['size'] for item in self.analysis_results)
        
        # Only show top 50 to keep UI responsive
        for item in self.analysis_results[:50]:
            row = ctk.CTkFrame(self.analyzer_scroll, fg_color=("white", "#2b2b2b"), border_width=1, border_color=("gray85", "gray25"))
            row.pack(fill="x", pady=4, padx=5)
            
            info_frame = ctk.CTkFrame(row, fg_color="transparent")
            info_frame.pack(side="left", fill="x", expand=True, padx=10, pady=5)
            
            name_lbl = ctk.CTkLabel(info_frame, text=item['name'], font=("Arial", 12, "bold"), anchor="w")
            name_lbl.pack(fill="x")
            
            path_lbl = ctk.CTkLabel(info_frame, text=item['path'], font=("Arial", 9), text_color="gray", anchor="w")
            path_lbl.pack(fill="x")
            
            data_frame = ctk.CTkFrame(row, fg_color="transparent", width=150)
            data_frame.pack(side="right", padx=10)
            
            size_lbl = ctk.CTkLabel(data_frame, text=format_size(item['size']), font=("Arial", 12, "bold"), text_color=("#3498db", "#5dade2"))
            size_lbl.pack(side="top", anchor="e")
            
            progress = ctk.CTkProgressBar(data_frame, width=100, height=8, progress_color="#3498db")
            progress.pack(side="bottom", pady=(0, 5))
            progress.set(item['size'] / self.max_analysis_size)

    def browse_path(self):
        path = filedialog.askdirectory()
        if path: self.project_path_var.set(path)

    def update_disk_stats(self):
        try:
            partitions = psutil.disk_partitions()
            existing_drives = [p.device.split(":")[0] for p in partitions if 'fixed' in p.opts or 'cdrom' not in p.opts]
            
            # Remove labels for drives that no longer exist
            for drive in list(self.drive_labels.keys()):
                if drive not in existing_drives:
                    self.drive_labels[drive].destroy()
                    del self.drive_labels[drive]

            for part in partitions:
                if 'cdrom' in part.opts or part.fstype == "": continue
                
                drive = part.device.split(":")[0]
                try:
                    usage = psutil.disk_usage(part.mountpoint)
                    free_gb = usage.free / (1024**3)
                    percent_free = (usage.free / usage.total) * 100
                    text = f"{drive}: {free_gb:.1f} GB Free ({percent_free:.0f}%)"
                    
                    if drive not in self.drive_labels:
                        # Better colors for drive labels
                        color = ("#27ae60", "#2ecc71") if drive == "C" else ("#2980b9", "#3498db")
                        lbl = ctk.CTkLabel(self.stats_box, text=text, font=("Arial", 12, "bold"), text_color=color)
                        lbl.pack(pady=4, fill="x")
                        self.drive_labels[drive] = lbl
                    else:
                        self.drive_labels[drive].configure(text=text)
                except:
                    pass
        except:
            pass

    def stop_process(self):
        self.stop_event.set()
        self.status_bar.configure(text="Menghentikan proses...")

    def set_busy(self, busy=True):
        if busy:
            self.stop_event.clear()
            self.btn_stop.configure(state="normal")
            self.progress.set(0)
        else:
            self.btn_stop.configure(state="disabled")

    def run_scan(self):
        self.set_busy(True)
        self.btn_scan_sys.configure(state="disabled")
        threading.Thread(target=self._scan_thread, daemon=True).start()

    def _scan_thread(self):
        items = list(self.core.categories.keys())
        for i, name in enumerate(items):
            if self.stop_event.is_set(): break
            self.status_bar.configure(text=f"Scanning {name}...")
            size = self.core.scan_category(name, self.stop_event)
            self.category_labels[name].configure(text=format_size(size))
            self.progress.set((i + 1) / len(items))
        self.status_bar.configure(text="Scan selesai!" if not self.stop_event.is_set() else "Scan dibatalkan.")
        self.btn_scan_sys.configure(state="normal")
        self.set_busy(False)

    def run_clean(self):
        if not messagebox.askyesno("Konfirmasi Keamanan", "Apakah Anda yakin ingin menghapus file sistem yang dipilih?"):
            return
        self.set_busy(True)
        self.btn_clean_sys.configure(state="disabled")
        threading.Thread(target=self._clean_thread, daemon=True).start()

    def _clean_thread(self):
        selected = [n for n, v in self.selected_vars.items() if v.get()]
        total_freed = 0
        for i, name in enumerate(selected):
            if self.stop_event.is_set(): break
            self.status_bar.configure(text=f"Cleaning {name}...")
            freed = self.core.clean_category(name)
            total_freed += freed
            new_size = self.core.scan_category(name, self.stop_event)
            self.category_labels[name].configure(text=format_size(new_size))
            self.progress.set((i + 1) / len(selected))
        self.update_disk_stats()
        self.status_bar.configure(text=f"Selesai! Freed {format_size(total_freed)}" if not self.stop_event.is_set() else "Pembersihan dibatalkan.")
        self.btn_clean_sys.configure(state="normal")
        self.set_busy(False)

    def run_dev_scan(self):
        self.set_busy(True)
        self.btn_scan_dev.configure(state="disabled")
        for widget in self.dev_scroll.winfo_children(): widget.destroy()
        self.found_dev_items = []
        threading.Thread(target=self._dev_scan_thread, daemon=True).start()

    def _dev_scan_thread(self):
        root = self.project_path_var.get()
        selected_patterns = [p for p, v in self.pattern_vars.items() if v.get()]
        found = self.core.scan_dev_folders(root, selected_patterns, self.stop_event)
        for item in found:
            row = ctk.CTkFrame(self.dev_scroll, fg_color="transparent")
            row.pack(fill="x", pady=2)
            var = tk.BooleanVar(value=True)
            cb = ctk.CTkCheckBox(row, text=f"{item['name']} ({os.path.basename(os.path.dirname(item['path']))})", variable=var)
            cb.pack(side="left")
            size_lbl = ctk.CTkLabel(row, text=format_size(item['size']))
            size_lbl.pack(side="right")
            self.found_dev_items.append({"path": item['path'], "var": var, "lbl": size_lbl})
        self.status_bar.configure(text=f"Ditemukan {len(found)} folder." if not self.stop_event.is_set() else "Scan dibatalkan.")
        self.btn_scan_dev.configure(state="normal")
        self.set_busy(False)

    def run_dev_clean(self):
        to_clean = [i for i in self.found_dev_items if i['var'].get()]
        if not to_clean:
            messagebox.showwarning("Peringatan", "Tidak ada folder yang dipilih untuk dihapus.")
            return
        
        if not messagebox.askyesno("Konfirmasi Keamanan", f"Anda akan menghapus {len(to_clean)} folder proyek. Tindakan ini tidak bisa dibatalkan. Lanjutkan?"):
            return

        self.set_busy(True)
        self.btn_clean_dev.configure(state="disabled")
        threading.Thread(target=self._dev_clean_thread, daemon=True).start()

    def _dev_clean_thread(self):
        to_clean = [i for i in self.found_dev_items if i['var'].get()]
        freed_total = 0
        for i, item in enumerate(to_clean):
            if self.stop_event.is_set(): break
            freed = self.core.clean_path(item['path'])
            freed_total += freed
            item['lbl'].configure(text="CLEANED", text_color="#2ecc71")
            self.progress.set((i + 1) / len(to_clean))
        self.update_disk_stats()
        self.status_bar.configure(text=f"Selesai! Freed {format_size(freed_total)}" if not self.stop_event.is_set() else "Pembersihan dibatalkan.")
        self.btn_clean_dev.configure(state="normal")
        self.set_busy(False)

    def change_appearance(self, mode):
        ctk.set_appearance_mode(mode)
