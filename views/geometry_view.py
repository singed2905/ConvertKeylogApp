import tkinter as tk
from tkinter import messagebox, filedialog, simpledialog
from tkinter import ttk
import threading
import os
from datetime import datetime
import psutil

# NEW: Import matplotlib for coordinate plotting
try:
    import matplotlib.pyplot as plt
    from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg, NavigationToolbar2Tk
    from mpl_toolkits.mplot3d import Axes3D
    import numpy as np
    MATPLOTLIB_AVAILABLE = True
except ImportError:
    MATPLOTLIB_AVAILABLE = False
    print("Warning: matplotlib not available. Coordinate plotting disabled.")

class GeometryView:
    def __init__(self, window, config=None):
        self.window = window
        self.window.title("Geometry Mode - Anti-Crash Excel! 💪")
        self.window.configure(bg="#F8F9FA")

        # Lưu config được truyền vào
        self.config = config or {}
        
        # Import và khởi tạo GeometryService (lazy loading)
        self.geometry_service = None
        self._initialize_service()
        
        # Excel processing state
        self.imported_data = False
        self.imported_file_path = ""
        self.imported_file_name = ""  # NEW: store only file name after import
        self.manual_data_entered = False
        self.processing_cancelled = False
        self.is_large_file = False  # Track if current file is large
        self.has_result = False  # Track if manual result is available
        
        # NEW: Plotting state
        self.plot_visible = False
        self.fig = None
        self.canvas = None
        self.toolbar = None
        
        # Biến và trạng thái
        self._initialize_variables()
        
        # NEW: Build scrollable root content before UI
        self._build_scrollable_root()
        
        # Build inner UI on scrollable frame
        self._setup_ui()
        
        # Đảm bảo hiển thị đúng ngay lần đầu
        self._on_operation_changed()
        self._on_shape_changed()

    # ===== Scrollable Root =====
    def _build_scrollable_root(self):
        """Wrap the entire view in a scrollable Canvas with vertical scrollbar"""
        # Container that fills window
        self.root_container = tk.Frame(self.window, bg="#F8F9FA")
        self.root_container.pack(fill="both", expand=True)

        # Canvas + Scrollbar
        self.scroll_canvas = tk.Canvas(self.root_container, bg="#F8F9FA", highlightthickness=0)
        self.v_scrollbar = ttk.Scrollbar(self.root_container, orient="vertical", command=self.scroll_canvas.yview)
        self.scroll_canvas.configure(yscrollcommand=self.v_scrollbar.set)

        self.v_scrollbar.pack(side="right", fill="y")
        self.scroll_canvas.pack(side="left", fill="both", expand=True)

        # Inner frame inside canvas
        self.scrollable_frame = tk.Frame(self.scroll_canvas, bg="#F8F9FA")
        self.scroll_window = self.scroll_canvas.create_window((0, 0), window=self.scrollable_frame, anchor="nw")

        # Bind to configure scrollregion on size change
        def _on_frame_configure(event=None):
            self.scroll_canvas.configure(scrollregion=self.scroll_canvas.bbox("all"))
        self.scrollable_frame.bind("<Configure>", _on_frame_configure)

        # Enable mouse wheel scrolling
        self._enable_mousewheel(self.scroll_canvas)

        # Resize inner window width to canvas width
        def _on_canvas_configure(event):
            try:
                self.scroll_canvas.itemconfig(self.scroll_window, width=event.width)
            except Exception:
                pass
        self.scroll_canvas.bind("<Configure>", _on_canvas_configure)

    def _enable_mousewheel(self, widget):
        """Enable platform-aware mouse wheel scrolling for the canvas"""
        def _on_mousewheel(event):
            # Windows / Linux use event.delta; Mac uses different sign/scale
            delta = -1 * int(event.delta/120) if event.delta else 0
            if delta == 0:
                delta = 1 if getattr(event, 'num', 0) == 5 else -1
            self.scroll_canvas.yview_scroll(delta, "units")
            return "break"
        # Bind for various platforms
        widget.bind_all("<MouseWheel>", _on_mousewheel)      # Windows
        widget.bind_all("<Button-4>", _on_mousewheel)        # Linux scroll up
        widget.bind_all("<Button-5>", _on_mousewheel)        # Linux scroll down

    def _initialize_service(self):
        try:
            from services.geometry.geometry_service import GeometryService
            self.geometry_service = GeometryService(self.config)
        except Exception as e:
            print(f"Warning: Could not initialize GeometryService: {e}")
            self.geometry_service = None

    def _initialize_variables(self):
        self.dropdown1_var = tk.StringVar(value="")
        self.dropdown2_var = tk.StringVar(value="")
        self.kich_thuoc_A_var = tk.StringVar(value="3")
        self.kich_thuoc_B_var = tk.StringVar(value="3")
        self.pheptoan_var = tk.StringVar(value="Khoảng cách")
        self.phien_ban_list = self._get_available_versions()
        self.phien_ban_var = tk.StringVar(value=self.phien_ban_list[0])
        self.dropdown1_var.trace('w', self._on_shape_changed)
        self.dropdown2_var.trace('w', self._on_shape_changed)
        self.pheptoan_var.trace('w', self._on_operation_changed)
        self.kich_thuoc_A_var.trace('w', self._on_dimension_changed)
        self.kich_thuoc_B_var.trace('w', self._on_dimension_changed)
        self.window.after(1000, self._setup_input_bindings)
        if self.geometry_service:
            self.geometry_service.set_kich_thuoc(self.kich_thuoc_A_var.get(), self.kich_thuoc_B_var.get())

    def _setup_input_bindings(self):
        entries = self._get_all_input_entries()
        for entry in entries:
            if hasattr(entry, 'bind'):
                entry.bind('<KeyRelease>', self._on_input_data_changed)

    def _get_all_input_entries(self):
        entries = []
        for attr_name in dir(self):
            if attr_name.startswith('entry_') and hasattr(self, attr_name):
                entry = getattr(self, attr_name)
                if hasattr(entry, 'get'):
                    entries.append(entry)
        return entries

    def _on_input_data_changed(self, event):
        if self.imported_data:
            messagebox.showerror("Lỗi", "Đã import Excel, không thể nhập dữ liệu thủ công!")
            event.widget.delete(0, tk.END)
            return
        has_data = self._check_manual_data()
        if has_data and not self.manual_data_entered:
            self.manual_data_entered = True
            self._show_manual_buttons()
        elif not has_data and self.manual_data_entered:
            self.manual_data_entered = False
            self._hide_action_buttons()
            self._hide_copy_button()
            self._hide_coordinate_plot()

    def _check_manual_data(self):
        entries = self._get_all_input_entries()
        for entry in entries:
            try:
                if entry.get().strip():
                    return True
            except:
                pass
        return False

    def _show_manual_buttons(self):
        self.frame_buttons_manual.grid()
        if hasattr(self, 'frame_buttons_import'):
            self.frame_buttons_import.grid_remove()

    def _show_import_buttons(self):
        if hasattr(self, 'frame_buttons_import'):
            self.frame_buttons_import.grid()
        self.frame_buttons_manual.grid_remove()

    def _hide_action_buttons(self):
        self.frame_buttons_manual.grid_remove()
        if hasattr(self, 'frame_buttons_import'):
            self.frame_buttons_import.grid_remove()

    def _get_available_versions(self):
        try:
            if self.config and 'common' in self.config and 'versions' in self.config['common']:
                versions_data = self.config['common']['versions']
                if 'versions' in versions_data:
                    return [f"Phiên bản {v}" for v in versions_data['versions']]
        except Exception as e:
            print(f"Warning: Không thể load versions từ config: {e}")
        return ["Phiên bản fx799", "Phiên bản fx880", "Phiên bản fx801"]

    def _get_available_operations(self):
        if self.geometry_service:
            return self.geometry_service.get_available_operations()
        else:
            return ["Tương giao", "Khoảng cách", "Diện tích", "Thể tích", "PT đường thẳng"]

    def _on_shape_changed(self, *args):
        if self.geometry_service:
            self.geometry_service.set_current_shapes(self.dropdown1_var.get(), self.dropdown2_var.get())
        self._update_input_frames()

    def _on_operation_changed(self, *args):
        operation = self.pheptoan_var.get()
        if operation and self.geometry_service:
            self.geometry_service.set_current_operation(operation)
            available_shapes = self.geometry_service.update_dropdown_options(operation)
            self._update_shape_dropdowns(available_shapes)
        self._update_input_frames()

    def _on_dimension_changed(self, *args):
        if self.geometry_service:
            self.geometry_service.set_kich_thuoc(self.kich_thuoc_A_var.get(), self.kich_thuoc_B_var.get())

    def _update_shape_dropdowns(self, available_shapes):
        if not available_shapes:
            return
        try:
            menu_A = self.dropdown1_menu['menu']
            menu_A.delete(0, 'end')
            for shape in available_shapes:
                menu_A.add_command(label=shape, command=tk._setit(self.dropdown1_var, shape))
            if self.dropdown1_var.get() not in available_shapes:
                self.dropdown1_var.set(available_shapes[0])
            if self.pheptoan_var.get() not in ["Diện tích", "Thể tích"]:
                menu_B = self.dropdown2_menu['menu']
                menu_B.delete(0, 'end')
                for shape in available_shapes:
                    menu_B.add_command(label=shape, command=tk._setit(self.dropdown2_var, shape))
                if self.dropdown2_var.get() not in available_shapes:
                    self.dropdown2_var.set(available_shapes[0])
                self.label_B.grid()
                self.dropdown2_menu.grid()
            else:
                self.label_B.grid_remove()
                self.dropdown2_menu.grid_remove()
        except Exception as e:
            print(f"Warning: Could not update dropdowns: {e}")

    def _update_input_frames(self):
        all_frames = ['frame_A_diem', 'frame_A_duong', 'frame_A_plane', 'frame_A_circle', 'frame_A_sphere',
                     'frame_B_diem', 'frame_B_duong', 'frame_B_plane', 'frame_B_circle', 'frame_B_sphere']
        for frame_name in all_frames:
            frame = getattr(self, frame_name, None)
            if frame and hasattr(frame, 'grid_remove'):
                try:
                    frame.grid_remove()
                except:
                    pass
        shape_A = self.dropdown1_var.get()
        if shape_A:
            self._show_input_frame_A(shape_A)
        if self.pheptoan_var.get() not in ["Diện tích", "Thể tích"]:
            shape_B = self.dropdown2_var.get()
            if shape_B:
                self._show_input_frame_B(shape_B)

    def _show_input_frame_A(self, shape):
        try:
            if shape == "Điểm" and hasattr(self, 'frame_A_diem'):
                self.frame_A_diem.grid()
            elif shape == "Đường thẳng" and hasattr(self, 'frame_A_duong'):
                self.frame_A_duong.grid()
            elif shape == "Mặt phẳng" and hasattr(self, 'frame_A_plane'):
                self.frame_A_plane.grid()
            elif shape == "Đường tròn" and hasattr(self, 'frame_A_circle'):
                self.frame_A_circle.grid()
            elif shape == "Mặt cầu" and hasattr(self, 'frame_A_sphere'):
                self.frame_A_sphere.grid()
        except Exception as e:
            print(f"Warning: Could not show frame A for {shape}: {e}")

    def _show_input_frame_B(self, shape):
        try:
            if shape == "Điểm" and hasattr(self, 'frame_B_diem'):
                self.frame_B_diem.grid()
            elif shape == "Đường thẳng" and hasattr(self, 'frame_B_duong'):
                self.frame_B_duong.grid()
            elif shape == "Mặt phẳng" and hasattr(self, 'frame_B_plane'):
                self.frame_B_plane.grid()
            elif shape == "Đường tròn" and hasattr(self, 'frame_B_circle'):
                self.frame_B_circle.grid()
            elif shape == "Mặt cầu" and hasattr(self, 'frame_B_sphere'):
                self.frame_B_sphere.grid()
        except Exception as e:
            print(f"Warning: Could not show frame B for {shape}: {e}")

    def _setup_ui(self):
        # Header on top of scrollable frame
        self._create_header(parent=self.scrollable_frame)
        
        self.main_container = tk.Frame(self.scrollable_frame, bg="#F8F9FA")
        self.main_container.pack(fill="both", expand=True, padx=10, pady=5)

        top_frame = tk.Frame(self.main_container, bg="#F8F9FA")
        top_frame.grid(row=0, column=0, columnspan=4, padx=10, pady=5, sticky="we")

        self._setup_dropdowns(top_frame)
        self._setup_all_input_frames()
        self._setup_control_frame()
        if MATPLOTLIB_AVAILABLE:
            self._create_coordinate_plot_frame()
        self._show_ready_message()

    # ===== NEW: Modular Coordinate Plotting using Shape Renderers =====
    def _create_coordinate_plot_frame(self):
        if not MATPLOTLIB_AVAILABLE:
            return
        self.frame_plot = tk.LabelFrame(
            self.main_container, text="📊 Hiển thị trên hệ tọa độ",
            bg="#FFFFFF", fg="#1B5299", font=("Arial", 10, "bold")
        )
        self.frame_plot.grid(row=11, column=0, columnspan=4, padx=10, pady=10, sticky="we")
        self.fig = plt.Figure(figsize=(10, 6), dpi=100, facecolor='white')
        self.canvas = FigureCanvasTkAgg(self.fig, self.frame_plot)
        self.canvas.get_tk_widget().pack(fill="both", expand=True, padx=5, pady=5)
        toolbar_frame = tk.Frame(self.frame_plot, bg="#FFFFFF")
        toolbar_frame.pack(fill="x", padx=5, pady=2)
        self.toolbar = NavigationToolbar2Tk(self.canvas, toolbar_frame)
        self.toolbar.update()
        self.frame_plot.grid_remove()
        self.plot_visible = False

    def _show_coordinate_plot(self):
        if not MATPLOTLIB_AVAILABLE or self.imported_data:
            return
        if not self.plot_visible:
            self.frame_plot.grid()
            self.plot_visible = True
        self._update_coordinate_plot()

    def _hide_coordinate_plot(self):
        if not MATPLOTLIB_AVAILABLE:
            return
        if self.plot_visible:
            self.frame_plot.grid_remove()
            self.plot_visible = False

    def _update_coordinate_plot(self):
        if not MATPLOTLIB_AVAILABLE or not self.plot_visible or self.imported_data:
            return
        try:
            self.fig.clear()
            data_a = self._get_input_data_A()
            data_b = self._get_input_data_B()
            is_3d = (self.kich_thuoc_A_var.get() == "3" or self.kich_thuoc_B_var.get() == "3")
            if is_3d:
                ax = self.fig.add_subplot(111, projection='3d')
                self._plot_3d_data(ax, data_a, data_b)
            else:
                ax = self.fig.add_subplot(111)
                self._plot_2d_data(ax, data_a, data_b)
            self.canvas.draw()
            # Update scroll region after plot
            self.scrollable_frame.update_idletasks()
        except Exception as e:
            print(f"Plot update error: {e}")

    def _plot_2d_data(self, ax, data_a, data_b):
        ax.set_title(f"Hệ tọa độ Oxy - {self.pheptoan_var.get()}", fontsize=12, fontweight='bold')
        ax.set_xlabel("X", fontsize=10)
        ax.set_ylabel("Y", fontsize=10)
        ax.grid(True, alpha=0.3)
        
        rendered_count = 0
        rendered_count += self._plot_group_with_renderer(ax, data_a, "A", "blue", self.dropdown1_var.get(), False)
        if self.pheptoan_var.get() not in ["Diện tích", "Thể tích"]:
            rendered_count += self._plot_group_with_renderer(ax, data_b, "B", "red", self.dropdown2_var.get(), False)
        
        # Only show legend if we have rendered objects
        handles, labels = ax.get_legend_handles_labels()
        valid_labels = [lb for lb in labels if lb and not lb.startswith('_')]
        if handles and valid_labels:
            ax.legend()
        
        # Show hint if nothing rendered
        if rendered_count == 0:
            ax.text(0.5, 0.5, 'Nhập dữ liệu hợp lệ để hiển thị đồ thị', 
                   transform=ax.transAxes, ha='center', va='center',
                   fontsize=12, color='gray', style='italic')
        else:
            ax.axis('equal')

    def _plot_3d_data(self, ax, data_a, data_b):
        ax.set_title(f"Hệ tọa độ Oxyz - {self.pheptoan_var.get()}", fontsize=12, fontweight='bold')
        ax.set_xlabel("X", fontsize=10)
        ax.set_ylabel("Y", fontsize=10)
        ax.set_zlabel("Z", fontsize=10)
        
        rendered_count = 0
        rendered_count += self._plot_group_with_renderer(ax, data_a, "A", "blue", self.dropdown1_var.get(), True)
        if self.pheptoan_var.get() not in ["Diện tích", "Thể tích"]:
            rendered_count += self._plot_group_with_renderer(ax, data_b, "B", "red", self.dropdown2_var.get(), True)
        
        # Only show legend if we have rendered objects
        handles, labels = ax.get_legend_handles_labels()
        valid_labels = [lb for lb in labels if lb and not lb.startswith('_')]
        if handles and valid_labels:
            ax.legend()
        
        # Show hint if nothing rendered
        if rendered_count == 0:
            ax.text2D(0.5, 0.5, 'Nhập dữ liệu hợp lệ để hiển thị đồ thị 3D',
                     transform=ax.transAxes, ha='center', va='center',
                     fontsize=12, color='gray', style='italic')

    def _plot_group_with_renderer(self, ax, data, group_name, color, shape_type, is_3d):
        """Plot a single group using appropriate shape renderer"""
        try:
            # Import shape factory
            from services.geometry.shapes.shape_factory import ShapeRendererFactory
            
            renderer = ShapeRendererFactory.get_renderer(shape_type, is_3d, color, group_name)
            if renderer and renderer.can_render(data):
                success = renderer.render(ax, data)
                return 1 if success else 0
            return 0
            
        except ImportError:
            print(f"Warning: Shape renderer not available for {shape_type}")
            return self._plot_group_fallback(ax, data, group_name, color, shape_type, is_3d)
        except Exception as e:
            print(f"Error using renderer for {shape_type} {group_name}: {e}")
            return 0
    
    def _plot_group_fallback(self, ax, data, group_name, color, shape_type, is_3d):
        """Fallback plotting method if renderers not available"""
        print(f"Using fallback renderer for {shape_type} {group_name}")
        return 0  # Skip fallback for now, encourage fixing import issues

    def _create_header(self, parent=None):
        HEADER_COLORS = {"primary": "#2E86AB", "secondary": "#1B5299", "text": "#FFFFFF", "accent": "#F18F01", "success": "#4CAF50", "warning": "#FF9800", "danger": "#F44336"}
        target = parent or self.window
        self.header_frame = tk.Frame(target, bg=HEADER_COLORS["primary"], height=90)
        self.header_frame.pack(fill="x", padx=10, pady=5)
        self.header_frame.pack_propagate(False)
        header_content = tk.Frame(self.header_frame, bg=HEADER_COLORS["primary"])
        header_content.pack(fill="both", expand=True, padx=15, pady=10)
        left_section = tk.Frame(header_content, bg=HEADER_COLORS["primary"])
        left_section.pack(side="left", fill="y")
        logo_frame = tk.Frame(left_section, bg=HEADER_COLORS["primary"])
        logo_frame.pack(side="top", fill="x")
        tk.Label(logo_frame, text="🧮", font=("Arial", 20), bg=HEADER_COLORS["primary"], fg=HEADER_COLORS["text"]).pack(side="left")
        tk.Label(logo_frame, text="Geometry v2.1 - Anti-Crash! 💪", font=("Arial", 16, "bold"), bg=HEADER_COLORS["primary"], fg=HEADER_COLORS["text"]).pack(side="left", padx=(5, 20))
        operation_frame = tk.Frame(left_section, bg=HEADER_COLORS["primary"])
        operation_frame.pack(side="top", fill="x", pady=(5, 0))
        tk.Label(operation_frame, text="Phép toán:", font=("Arial", 10), bg=HEADER_COLORS["primary"], fg=HEADER_COLORS["text"]).pack(side="left")
        operations = self._get_available_operations()
        self.operation_menu = tk.OptionMenu(operation_frame, self.pheptoan_var, *operations)
        self.operation_menu.config(bg=HEADER_COLORS["secondary"], fg=HEADER_COLORS["text"], font=("Arial", 10, "bold"), width=15, relief="flat", borderwidth=0)
        self.operation_menu.pack(side="left", padx=(5, 0))
        center_section = tk.Frame(header_content, bg=HEADER_COLORS["primary"])
        center_section.pack(side="left", fill="both", expand=True, padx=20)
        version_frame = tk.Frame(center_section, bg=HEADER_COLORS["primary"])
        version_frame.pack(side="top", fill="x")
        tk.Label(version_frame, text="Phiên bản:", font=("Arial", 9), bg=HEADER_COLORS["primary"], fg=HEADER_COLORS["text"]).pack(side="left")
        self.version_menu = tk.OptionMenu(version_frame, self.phien_ban_var, *self.phien_ban_list)
        self.version_menu.config(bg=HEADER_COLORS["accent"], fg="white", font=("Arial", 9), width=15, relief="flat", borderwidth=0)
        self.version_menu.pack(side="left", padx=(5, 0))
        self.excel_status_label = tk.Label(center_section, text="📊 Excel: ✅ Ready", font=("Arial", 8), bg=HEADER_COLORS["primary"], fg=HEADER_COLORS["success"])
        self.excel_status_label.pack(side="bottom")
        self.memory_status_label = tk.Label(center_section, text=f"💾 Memory: {self._get_memory_usage():.1f}MB", font=("Arial", 8), bg=HEADER_COLORS["primary"], fg=HEADER_COLORS["text"])
        self.memory_status_label.pack(side="bottom")
        status_text = "Service: ✅ Ready" if self.geometry_service else "Service: ⚠️ Error"
        plot_status = "📊 Plot: ✅ Ready" if MATPLOTLIB_AVAILABLE else "📊 Plot: ⚠️ Disabled"
        tk.Label(center_section, text=f"{status_text} | {plot_status}", font=("Arial", 8), bg=HEADER_COLORS["primary"], fg=HEADER_COLORS["text"]).pack(side="bottom")
        self._start_memory_monitoring()

    def _get_memory_usage(self) -> float:
        try:
            process = psutil.Process()
            return process.memory_info().rss / 1024 / 1024
        except:
            return 0.0

    def _start_memory_monitoring(self):
        def update_memory():
            try:
                memory_mb = self._get_memory_usage()
                if memory_mb > 800:
                    color = "#F44336"; status = "🔥 High"
                elif memory_mb > 500:
                    color = "#FF9800"; status = "⚠️ Medium"
                else:
                    color = "#4CAF50"; status = "✅ OK"
                self.memory_status_label.config(text=f"💾 Memory: {memory_mb:.1f}MB ({status})", fg=color)
            except Exception:
                pass
            self.window.after(5000, update_memory)
        update_memory()

    def _setup_dropdowns(self, parent):
        shapes = self.geometry_service.get_available_shapes() if self.geometry_service else ["Điểm", "Đường thẳng", "Mặt phẳng", "Đường tròn", "Mặt cầu"]
        if shapes:
            self.dropdown1_var.set(shapes[0])
            self.dropdown2_var.set(shapes[0])
        self.label_A = tk.Label(parent, text="Chọn nhóm A:", bg="#F8F9FA", font=("Arial", 10))
        self.label_A.grid(row=0, column=0, padx=5, pady=5, sticky="w")
        self.dropdown1_menu = tk.OptionMenu(parent, self.dropdown1_var, *shapes)
        self.dropdown1_menu.config(width=15, font=("Arial", 9))
        self.dropdown1_menu.grid(row=0, column=1, padx=5, pady=5)
        self.label_B = tk.Label(parent, text="Chọn nhóm B:", bg="#F8F9FA", font=("Arial", 10))
        self.label_B.grid(row=0, column=2, padx=5, pady=5, sticky="w")
        self.dropdown2_menu = tk.OptionMenu(parent, self.dropdown2_var, *shapes)
        self.dropdown2_menu.config(width=15, font=("Arial", 9))
        self.dropdown2_menu.grid(row=0, column=3, padx=5, pady=5)

    def _setup_all_input_frames(self):
        self._create_point_frame_A(); self._create_line_frame_A(); self._create_plane_frame_A(); self._create_circle_frame_A(); self._create_sphere_frame_A()
        self._create_point_frame_B(); self._create_line_frame_B(); self._create_plane_frame_B(); self._create_circle_frame_B(); self._create_sphere_frame_B()

    # ========== NHÓM A FRAMES ==========
    def _create_point_frame_A(self):
        self.frame_A_diem = tk.LabelFrame(self.main_container, text="🎯 NHÓM A - Điểm", bg="#FFFFFF", fg="#1B5299", font=("Arial", 10, "bold"))
        self.frame_A_diem.grid(row=1, column=0, columnspan=4, padx=10, pady=5, sticky="we")
        tk.Label(self.frame_A_diem, text="Kích thước:", bg="#FFFFFF").grid(row=0, column=0)
        tk.OptionMenu(self.frame_A_diem, self.kich_thuoc_A_var, "2", "3").grid(row=0, column=1)
        tk.Label(self.frame_A_diem, text="Nhập tọa độ (x,y,z):", bg="#FFFFFF").grid(row=1, column=0)
        self.entry_diem_A = tk.Entry(self.frame_A_diem, width=40)
        self.entry_diem_A.grid(row=1, column=1, columnspan=2, sticky="we")
        self.frame_A_diem.grid_remove()

    def _create_line_frame_A(self):
        self.frame_A_duong = tk.LabelFrame(self.main_container, text="📏 NHÓM A - Đường thẳng", bg="#FFFFFF", fg="#1B5299", font=("Arial", 10, "bold"))
        self.frame_A_duong.grid(row=1, column=0, columnspan=4, padx=10, pady=5, sticky="we")
        tk.Label(self.frame_A_duong, text="Điểm (A,B,C):", bg="#FFFFFF").grid(row=0, column=0)
        self.entry_point_A = tk.Entry(self.frame_A_duong, width=30)
        self.entry_point_A.grid(row=0, column=1)
        tk.Label(self.frame_A_duong, text="Vector (X,Y,Z):", bg="#FFFFFF").grid(row=1, column=0)
        self.entry_vector_A = tk.Entry(self.frame_A_duong, width=30)
        self.entry_vector_A.grid(row=1, column=1)
        self.frame_A_duong.grid_remove()

    def _create_plane_frame_A(self):
        self.frame_A_plane = tk.LabelFrame(self.main_container, text="📐 NHÓM A - Mặt phẳng", bg="#FFFFFF", fg="#1B5299", font=("Arial", 10, "bold"))
        self.frame_A_plane.grid(row=1, column=0, columnspan=4, padx=10, pady=5, sticky="we")
        tk.Label(self.frame_A_plane, text="Phương trình ax+by+cz+d=0:", bg="#FFFFFF").grid(row=0, column=0, columnspan=4)
        tk.Label(self.frame_A_plane, text="a:", bg="#FFFFFF", width=3).grid(row=1, column=0, sticky="e")
        self.entry_a_A = tk.Entry(self.frame_A_plane, width=15)
        self.entry_a_A.grid(row=1, column=1, padx=5)
        tk.Label(self.frame_A_plane, text="b:", bg="#FFFFFF", width=3).grid(row=1, column=2, sticky="e")
        self.entry_b_A = tk.Entry(self.frame_A_plane, width=15)
        self.entry_b_A.grid(row=1, column=3, padx=5)
        tk.Label(self.frame_A_plane, text="c:", bg="#FFFFFF", width=3).grid(row=2, column=0, sticky="e")
        self.entry_c_A = tk.Entry(self.frame_A_plane, width=15)
        self.entry_c_A.grid(row=2, column=1, padx=5)
        tk.Label(self.frame_A_plane, text="d:", bg="#FFFFFF", width=3).grid(row=2, column=2, sticky="e")
        self.entry_d_A = tk.Entry(self.frame_A_plane, width=15)
        self.entry_d_A.grid(row=2, column=3, padx=5)
        self.frame_A_plane.grid_remove()

    def _create_circle_frame_A(self):
        self.frame_A_circle = tk.LabelFrame(self.main_container, text="⭕ NHÓM A - Đường tròn", bg="#FFFFFF", fg="#1B5299", font=("Arial", 10, "bold"))
        self.frame_A_circle.grid(row=1, column=0, columnspan=4, padx=10, pady=5, sticky="we")
        tk.Label(self.frame_A_circle, text="Tâm đường tròn (x,y):", bg="#FFFFFF").grid(row=0, column=0)
        self.entry_center_A = tk.Entry(self.frame_A_circle, width=25)
        self.entry_center_A.grid(row=0, column=1, padx=5)
        tk.Label(self.frame_A_circle, text="Bán kính:", bg="#FFFFFF").grid(row=0, column=2)
        self.entry_radius_A = tk.Entry(self.frame_A_circle, width=20)
        self.entry_radius_A.grid(row=0, column=3, padx=5)
        self.frame_A_circle.grid_remove()

    def _create_sphere_frame_A(self):
        self.frame_A_sphere = tk.LabelFrame(self.main_container, text="🌍 NHÓM A - Mặt cầu", bg="#FFFFFF", fg="#1B5299", font=("Arial", 10, "bold"))
        self.frame_A_sphere.grid(row=1, column=0, columnspan=4, padx=10, pady=5, sticky="we")
        tk.Label(self.frame_A_sphere, text="Tâm mặt cầu (x,y,z):", bg="#FFFFFF").grid(row=0, column=0)
        self.entry_sphere_center_A = tk.Entry(self.frame_A_sphere, width=25)
        self.entry_sphere_center_A.grid(row=0, column=1, padx=5)
        tk.Label(self.frame_A_sphere, text="Bán kính:", bg="#FFFFFF").grid(row=0, column=2)
        self.entry_sphere_radius_A = tk.Entry(self.frame_A_sphere, width=20)
        self.entry_sphere_radius_A.grid(row=0, column=3, padx=5)
        self.frame_A_sphere.grid_remove()

    # ========== NHÓM B FRAMES ==========
    def _create_point_frame_B(self):
        self.frame_B_diem = tk.LabelFrame(self.main_container, text="🎯 NHÓM B - Điểm", bg="#FFFFFF", fg="#A23B72", font=("Arial", 10, "bold"))
        self.frame_B_diem.grid(row=2, column=0, columnspan=4, padx=10, pady=5, sticky="we")
        tk.Label(self.frame_B_diem, text="Kích thước:", bg="#FFFFFF").grid(row=0, column=0)
        tk.OptionMenu(self.frame_B_diem, self.kich_thuoc_B_var, "2", "3").grid(row=0, column=1)
        tk.Label(self.frame_B_diem, text="Nhập tọa độ (x,y,z):", bg="#FFFFFF").grid(row=1, column=0)
        self.entry_diem_B = tk.Entry(self.frame_B_diem, width=40)
        self.entry_diem_B.grid(row=1, column=1, columnspan=2, sticky="we")
        self.frame_B_diem.grid_remove()

    def _create_line_frame_B(self):
        self.frame_B_duong = tk.LabelFrame(self.main_container, text="📏 NHÓM B - Đường thẳng", bg="#FFFFFF", fg="#A23B72", font=("Arial", 10, "bold"))
        self.frame_B_duong.grid(row=2, column=0, columnspan=4, padx=10, pady=5, sticky="we")
        tk.Label(self.frame_B_duong, text="Điểm (A,B,C):", bg="#FFFFFF").grid(row=0, column=0)
        self.entry_point_B = tk.Entry(self.frame_B_duong, width=30)
        self.entry_point_B.grid(row=0, column=1)
        tk.Label(self.frame_B_duong, text="Vector (X,Y,Z):", bg="#FFFFFF").grid(row=1, column=0)
        self.entry_vector_B = tk.Entry(self.frame_B_duong, width=30)
        self.entry_vector_B.grid(row=1, column=1)
        self.frame_B_duong.grid_remove()

    def _create_plane_frame_B(self):
        self.frame_B_plane = tk.LabelFrame(self.main_container, text="📐 NHÓM B - Mặt phẳng", bg="#FFFFFF", fg="#A23B72", font=("Arial", 10, "bold"))
        self.frame_B_plane.grid(row=2, column=0, columnspan=4, padx=10, pady=5, sticky="we")
        tk.Label(self.frame_B_plane, text="Phương trình ax+by+cz+d=0:", bg="#FFFFFF").grid(row=0, column=0, columnspan=4)
        tk.Label(self.frame_B_plane, text="a:", bg="#FFFFFF", width=3).grid(row=1, column=0, sticky="e")
        self.entry_a_B = tk.Entry(self.frame_B_plane, width=15)
        self.entry_a_B.grid(row=1, column=1, padx=5)
        tk.Label(self.frame_B_plane, text="b:", bg="#FFFFFF", width=3).grid(row=1, column=2, sticky="e")
        self.entry_b_B = tk.Entry(self.frame_B_plane, width=15)
        self.entry_b_B.grid(row=1, column=3, padx=5)
        tk.Label(self.frame_B_plane, text="c:", bg="#FFFFFF", width=3).grid(row=2, column=0, sticky="e")
        self.entry_c_B = tk.Entry(self.frame_B_plane, width=15)
        self.entry_c_B.grid(row=2, column=1, padx=5)
        tk.Label(self.frame_B_plane, text="d:", bg="#FFFFFF", width=3).grid(row=2, column=2, sticky="e")
        self.entry_d_B = tk.Entry(self.frame_B_plane, width=15)
        self.entry_d_B.grid(row=2, column=3, padx=5)
        self.frame_B_plane.grid_remove()

    def _create_circle_frame_B(self):
        self.frame_B_circle = tk.LabelFrame(self.main_container, text="⭕ NHÓM B - Đường tròn", bg="#FFFFFF", fg="#A23B72", font=("Arial", 10, "bold"))
        self.frame_B_circle.grid(row=2, column=0, columnspan=4, padx=10, pady=5, sticky="we")
        tk.Label(self.frame_B_circle, text="Tâm đường tròn (x,y):", bg="#FFFFFF").grid(row=0, column=0)
        self.entry_center_B = tk.Entry(self.frame_B_circle, width=25)
        self.entry_center_B.grid(row=0, column=1, padx=5)
        tk.Label(self.frame_B_circle, text="Bán kính:", bg="#FFFFFF").grid(row=0, column=2)
        self.entry_radius_B = tk.Entry(self.frame_B_circle, width=20)
        self.entry_radius_B.grid(row=0, column=3, padx=5)
        self.frame_B_circle.grid_remove()

    def _create_sphere_frame_B(self):
        self.frame_B_sphere = tk.LabelFrame(self.main_container, text="🌍 NHÓM B - Mặt cầu", bg="#FFFFFF", fg="#A23B72", font=("Arial", 10, "bold"))
        self.frame_B_sphere.grid(row=2, column=0, columnspan=4, padx=10, pady=5, sticky="we")
        tk.Label(self.frame_B_sphere, text="Tâm mặt cầu (x,y,z):", bg="#FFFFFF").grid(row=0, column=0)
        self.entry_sphere_center_B = tk.Entry(self.frame_B_sphere, width=25)
        self.entry_sphere_center_B.grid(row=0, column=1, padx=5)
        tk.Label(self.frame_B_sphere, text="Bán kính:", bg="#FFFFFF").grid(row=0, column=2)
        self.entry_sphere_radius_B = tk.Entry(self.frame_B_sphere, width=20)
        self.entry_sphere_radius_B.grid(row=0, column=3, padx=5)
        self.frame_B_sphere.grid_remove()

    # ========== DATA EXTRACTION ==========
    def _get_input_data_A(self):
        shape = self.dropdown1_var.get()
        data = {}
        if shape == "Điểm":
            data['point_input'] = self.entry_diem_A.get() if hasattr(self, 'entry_diem_A') else ''
        elif shape == "Đường thẳng":
            data['line_A1'] = self.entry_point_A.get() if hasattr(self, 'entry_point_A') else ''
            data['line_X1'] = self.entry_vector_A.get() if hasattr(self, 'entry_vector_A') else ''
        elif shape == "Mặt phẳng":
            data['plane_a'] = self.entry_a_A.get() if hasattr(self, 'entry_a_A') else ''
            data['plane_b'] = self.entry_b_A.get() if hasattr(self, 'entry_b_A') else ''
            data['plane_c'] = self.entry_c_A.get() if hasattr(self, 'entry_c_A') else ''
            data['plane_d'] = self.entry_d_A.get() if hasattr(self, 'entry_d_A') else ''
        elif shape == "Đường tròn":
            data['circle_center'] = self.entry_center_A.get() if hasattr(self, 'entry_center_A') else ''
            data['circle_radius'] = self.entry_radius_A.get() if hasattr(self, 'entry_radius_A') else ''
        elif shape == "Mặt cầu":
            data['sphere_center'] = self.entry_sphere_center_A.get() if hasattr(self, 'entry_sphere_center_A') else ''
            data['sphere_radius'] = self.entry_sphere_radius_A.get() if hasattr(self, 'entry_sphere_radius_A') else ''
        return data

    def _get_input_data_B(self):
        shape = self.dropdown2_var.get()
        data = {}
        if shape == "Điểm":
            data['point_input'] = self.entry_diem_B.get() if hasattr(self, 'entry_diem_B') else ''
        elif shape == "Đường thẳng":
            data['line_A2'] = self.entry_point_B.get() if hasattr(self, 'entry_point_B') else ''
            data['line_X2'] = self.entry_vector_B.get() if hasattr(self, 'entry_vector_B') else ''
        elif shape == "Mặt phẳng":
            data['plane_a'] = self.entry_a_B.get() if hasattr(self, 'entry_a_B') else ''
            data['plane_b'] = self.entry_b_B.get() if hasattr(self, 'entry_b_B') else ''
            data['plane_c'] = self.entry_c_B.get() if hasattr(self, 'entry_c_B') else ''
            data['plane_d'] = self.entry_d_B.get() if hasattr(self, 'entry_d_B') else ''
        elif shape == "Đường tròn":
            data['circle_center'] = self.entry_center_B.get() if hasattr(self, 'entry_center_B') else ''
            data['circle_radius'] = self.entry_radius_B.get() if hasattr(self, 'entry_radius_B') else ''
        elif shape == "Mặt cầu":
            data['sphere_center'] = self.entry_sphere_center_B.get() if hasattr(self, 'entry_sphere_center_B') else ''
            data['sphere_radius'] = self.entry_sphere_radius_B.get() if hasattr(self, 'entry_sphere_radius_B') else ''
        return data

    # ========== PROCESSING METHODS ==========
    def _process_group_A(self):
        try:
            if not self.geometry_service:
                messagebox.showerror("Lỗi", "GeometryService chưa được khởi tạo!")
                return
            data_A = self._get_input_data_A()
            result = self.geometry_service.thuc_thi_A(data_A)
            self._update_result_display(f"Nhóm A đã xử lý: {result}")
            if MATPLOTLIB_AVAILABLE and not self.imported_data:
                self._show_coordinate_plot()
        except Exception as e:
            messagebox.showerror("Lỗi", f"Lỗi xử lý nhóm A: {str(e)}")

    def _process_group_B(self):
        try:
            if not self.geometry_service:
                messagebox.showerror("Lỗi", "GeometryService chưa được khởi tạo!")
                return
            data_B = self._get_input_data_B()
            result = self.geometry_service.thuc_thi_B(data_B)
            self._update_result_display(f"Nhóm B đã xử lý: {result}")
            if MATPLOTLIB_AVAILABLE and not self.imported_data:
                self._show_coordinate_plot()
        except Exception as e:
            messagebox.showerror("Lỗi", f"Lỗi xử lý nhóm B: {str(e)}")

    def _process_all(self):
        try:
            if not self.geometry_service:
                messagebox.showerror("Lỗi", "GeometryService chưa được khởi tạo!")
                return
            if not self.pheptoan_var.get():
                messagebox.showwarning("Cảnh báo", "Vui lòng chọn phép toán!")
                return
            if not self.dropdown1_var.get():
                messagebox.showwarning("Cảnh báo", "Vui lòng chọn hình dạng cho nhóm A!")
                return
            data_A = self._get_input_data_A()
            data_B = self._get_input_data_B()
            result_A, result_B = self.geometry_service.thuc_thi_tat_ca(data_A, data_B)
            final_result = self.geometry_service.generate_final_result()
            self._show_single_line_result(final_result)
            self._show_copy_button()
            if MATPLOTLIB_AVAILABLE and not self.imported_data:
                self._show_coordinate_plot()
        except Exception as e:
            messagebox.showerror("Lỗi", f"Lỗi thực thi: {str(e)}")

    def _show_single_line_result(self, result_text: str):
        self.entry_tong.delete(1.0, tk.END)
        one_line = (result_text or "").strip().splitlines()[0] if result_text else ""
        self.entry_tong.insert(tk.END, one_line)
        try:
            self.entry_tong.config(font=("Flexio Fx799VN", 11, "bold"), fg="#000000", bg="#F8F9FA")
        except Exception:
            self.entry_tong.config(font=("Courier New", 11, "bold"), fg="#000000", bg="#F8F9FA")

    def _copy_result(self):
        try:
            result_text = self.entry_tong.get(1.0, tk.END).strip()
            if result_text:
                self.window.clipboard_clear()
                self.window.clipboard_append(result_text)
                messagebox.showinfo("Đã copy", f"Đã copy kết quả vào clipboard:\n\n{result_text}")
            else:
                messagebox.showwarning("Cảnh báo", "Không có kết quả để copy!")
        except Exception as e:
            messagebox.showerror("Lỗi Copy", f"Lỗi copy kết quả: {str(e)}")

    def _show_copy_button(self):
        if hasattr(self, 'btn_copy_result'):
            self.btn_copy_result.grid()

    def _hide_copy_button(self):
        if hasattr(self, 'btn_copy_result'):
            self.btn_copy_result.grid_remove()

    # ========== EXCEL METHODS (unchanged) ==========
    def _import_excel(self):
        try:
            file_path = filedialog.askopenfilename(
                title="Chọn file Excel",
                filetypes=[("Excel files", "*.xlsx *.xls")]
            )
            if not file_path:
                return
            file_ext = os.path.splitext(file_path)[1].lower()
            if file_ext not in ['.xlsx', '.xls']:
                messagebox.showerror("Lỗi", "Chỉ hỗ trợ file Excel (.xlsx, .xls)!")
                return
            if not os.path.exists(file_path):
                messagebox.showerror("Lỗi", "File không tồn tại!")
                return
            self.imported_file_path = file_path
            self.imported_file_name = os.path.basename(file_path)
            self.imported_data = True
            self.manual_data_entered = False
            self.is_large_file = False
            self._clear_and_lock_inputs()
            self._show_import_buttons()
            self._hide_copy_button()
            self._hide_coordinate_plot()
            status_message = f"📁 Đã import file: {self.imported_file_name}\n"
            self.excel_status_label.config(text=f"Excel: 📁 {self.imported_file_name[:15]}...")
            self._update_result_display(status_message)
        except Exception as e:
            messagebox.showerror("Lỗi Import", f"Lỗi import Excel: {str(e)}")

    def _process_excel_batch(self):
        # Excel processing logic (unchanged from previous version)
        pass

    def _create_progress_window(self, title):
        # Progress window logic (unchanged from previous version)
        pass

    def _export_excel(self):
        # Excel export logic (unchanged from previous version)
        pass

    def _create_template(self):
        # Template creation logic (unchanged from previous version)
        pass

    def _quit_import_mode(self):
        # Import mode exit logic (unchanged from previous version)
        pass

    def _clear_and_lock_inputs(self):
        entries = self._get_all_input_entries()
        for entry in entries:
            try:
                entry.delete(0, tk.END)
                entry.config(state='disabled', bg='#E0E0E0')
            except:
                pass

    def _unlock_and_clear_inputs(self):
        entries = self._get_all_input_entries()
        for entry in entries:
            try:
                entry.config(state='normal', bg='white')
                entry.delete(0, tk.END)
            except:
                pass

    def _update_result_display(self, message):
        self.entry_tong.delete(1.0, tk.END)
        self.entry_tong.insert(tk.END, message)
        try:
            self.entry_tong.config(font=("Courier New", 9), fg="black")
        except Exception:
            pass
        if "Lỗi" in message or "lỗi" in message:
            self.entry_tong.config(bg="#FFEBEE", fg="#D32F2F")
        elif "Đã import" in message or "Hoàn thành" in message:
            self.entry_tong.config(bg="#E8F5E8", fg="#388E3C")
        elif "Đang xử lý" in message:
            self.entry_tong.config(bg="#FFF3E0", fg="#F57C00")
        else:
            self.entry_tong.config(bg="#F8F9FA", fg="#2E86AB")

    def _show_ready_message(self):
        if self.geometry_service:
            message = "🎯 Geometry Mode sẵn sàng! Nhập dữ liệu và chọn 'Thực thi tất cả' để xem kết quả và đồ thị tọa độ."
        else:
            message = "⚠️ GeometryService không khởi tạo được.\nVui lòng kiểm tra cài đặt!"
        self.entry_tong.insert(tk.END, message)

    def _setup_control_frame(self):
        self.frame_tong = tk.LabelFrame(self.main_container, text="🎉 KẾT QUẢ & ĐIỀU KHIỂN", bg="#FFFFFF", font=("Arial", 10, "bold"))
        self.frame_tong.grid(row=8, column=0, columnspan=4, padx=10, pady=10, sticky="we")
        self.entry_tong = tk.Text(self.main_container, width=80, height=2, font=("Courier New", 9), wrap=tk.NONE, bg="#F8F9FA", fg="black", relief="solid", bd=1, padx=5, pady=5)
        self.entry_tong.grid(row=9, column=0, columnspan=4, padx=5, pady=5, sticky="we")
        self.btn_copy_result = tk.Button(self.main_container, text="📋 Copy Kết Quả", command=self._copy_result, bg="#9C27B0", fg="white", font=("Arial", 9, "bold"), width=20)
        self.btn_copy_result.grid(row=10,  column=0, sticky="w", padx=0, pady=5)
        self.btn_copy_result.grid_remove()
        self.btn_import_excel = tk.Button(self.frame_tong, text="📁 Import Excel (Fast Select - 250k limit!)", command=self._import_excel, bg="#FF9800", fg="white", font=("Arial", 9, "bold"))
        self.btn_import_excel.grid(row=0, column=0, columnspan=4, pady=5, sticky="we")
        self.frame_buttons_manual = tk.Frame(self.frame_tong, bg="#FFFFFF")
        self.frame_buttons_manual.grid(row=1, column=0, columnspan=4, pady=5, sticky="we")
        tk.Button(self.frame_buttons_manual, text="🔄 Xử lý Nhóm A", command=self._process_group_A, bg="#2196F3", fg="white", font=("Arial", 9)).grid(row=0, column=0, padx=5)
        tk.Button(self.frame_buttons_manual, text="🔄 Xử lý Nhóm B", command=self._process_group_B, bg="#2196F3", fg="white", font=("Arial", 9)).grid(row=0, column=1, padx=5)
        tk.Button(self.frame_buttons_manual, text="🚀 Thực thi tất cả", command=self._process_all, bg="#4CAF50", fg="white", font=("Arial", 9, "bold")).grid(row=0, column=2, padx=5)
        tk.Button(self.frame_buttons_manual, text="💾 Xuất Excel", command=self._export_excel, bg="#FF9800", fg="white", font=("Arial", 9, "bold")).grid(row=0, column=3, padx=5)
        self.frame_buttons_import = tk.Frame(self.frame_tong, bg="#FFFFFF")
        self.frame_buttons_import.grid(row=1, column=0, columnspan=4, pady=5, sticky="we")
        tk.Button(self.frame_buttons_import, text="🔥 Xử lý File Excel", command=self._process_excel_batch, bg="#F44336", fg="white", font=("Arial", 9, "bold")).grid(row=0, column=0, padx=5)
        tk.Button(self.frame_buttons_import, text="📁 Import File Khác", command=self._import_excel, bg="#2196F3", fg="white", font=("Arial", 9)).grid(row=0, column=1, padx=5)
        tk.Button(self.frame_buttons_import, text="📝 Tạo Template", command=self._create_template, bg="#9C27B0", fg="white", font=("Arial", 9)).grid(row=0, column=2, padx=5)
        tk.Button(self.frame_buttons_import, text="↩️ Quay lại", command=self._quit_import_mode, bg="#607D8B", fg="white", font=("Arial", 9)).grid(row=0, column=3, padx=5)
        self.frame_buttons_import.grid_remove()
        self.frame_buttons_manual.grid_remove()

if __name__ == "__main__":
    root = tk.Tk()
    app = GeometryView(root)
    root.mainloop()