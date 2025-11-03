import tkinter as tk
from tkinter import messagebox, filedialog
from utils.config_loader import config_loader

class MainView:
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("ConvertKeylogApp - Mode Selector")
        self.root.geometry("480x320")
        self.root.configure(bg="#e8f0f7")  # Màu nền nhẹ xanh pastel

        # Load danh sách mode từ cấu trúc mới (bao gồm Vector Mode)
        self.modes = self._load_modes()
        self.mode_var = tk.StringVar(value=self.modes[0] if self.modes else "Không có mode")

        # Active windows tracking - Store (window, view) pairs
        self.active_windows = {}

        self._setup_ui()

    def _load_modes(self):
        """Load modes từ config structure mới"""
        try:
            modes_data = config_loader.get_available_modes()
            # Đảm bảo Vector Mode được thêm vào
            if modes_data and "Vector Mode" not in modes_data:
                modes_data.append("Vector Mode")
            return modes_data if modes_data else ["Geometry Mode", "Equation Mode", "Polynomial Equation Mode", "Vector Mode"]
        except Exception as e:
            messagebox.showwarning("Cảnh báo", f"Không thể load modes từ config mới:\n{str(e)}\n\nSử dụng modes mặc định.")
            return ["Geometry Mode", "Equation Mode", "Polynomial Equation Mode", "Vector Mode"]

    def _setup_ui(self):
        """Tạo giao diện người dùng chính"""

        # === Tiêu đề lớn ===
        title_frame = tk.Frame(self.root, bg="#4A90E2")
        title_frame.pack(fill="x")

        title_label = tk.Label(
            title_frame,
            text="🧮 ConvertKeylogApp v2.2",
            font=("Segoe UI", 18, "bold"),
            bg="#4A90E2",
            fg="white",
            pady=15
        )
        title_label.pack()

        # === Khung chọn chế độ ===
        control_frame = tk.Frame(self.root, bg="#e8f0f7")
        control_frame.pack(pady=30)

        tk.Label(
            control_frame,
            text="Chọn chế độ:",
            font=("Segoe UI", 12, "bold"),
            bg="#e8f0f7",
            fg="#333"
        ).grid(row=0, column=0, padx=10, pady=10, sticky="w")

        # Custom OptionMenu (dropdown)
        optionmenu = tk.OptionMenu(control_frame, self.mode_var, *self.modes)
        optionmenu.config(
            width=25,
            font=("Segoe UI", 11),
            bg="#ffffff",
            fg="#333",
            relief="groove",
            highlightthickness=1,
            bd=0
        )
        optionmenu.grid(row=0, column=1, padx=5, pady=10)

        # === Khung chứa nút hành động ===
        button_frame = tk.Frame(self.root, bg="#e8f0f7")
        button_frame.pack(pady=20)

        # Nút chọn mode
        btn_select = tk.Button(
            button_frame,
            text="Mở chế độ",
            command=self._open_selected_mode,
            bg="#4CAF50",
            fg="white",
            font=("Segoe UI", 12, "bold"),
            relief="flat",
            activebackground="#45A049",
            width=12,
            height=1
        )
        btn_select.grid(row=0, column=0, padx=15, pady=10)

        # Nút thoát
        btn_quit = tk.Button(
            button_frame,
            text="❌ Thoát",
            command=self.root.quit,
            bg="#F44336",
            fg="white",
            font=("Segoe UI", 10, "bold"),
            relief="flat",
            activebackground="#E53935",
            width=10,
            height=1
        )
        btn_quit.grid(row=0, column=1, padx=15, pady=10)

        # === Thanh thông tin dưới cùng ===
        footer = tk.Label(
            self.root,
            text="📁 Config: Cấu trúc mới theo mode | 🎯 Version: 2.2 with Vector Mode",
            font=("Segoe UI", 9),
            bg="#dfe7ef",
            fg="#444",
            pady=5
        )
        footer.pack(side="bottom", fill="x")

    def _open_selected_mode(self):
        selected = self.mode_var.get()

        # Prevent multiple instances of same mode
        if selected in self.active_windows:
            try:
                # Bring existing window to front using correct tuple structure
                window, view = self.active_windows[selected]
                window.lift()
                window.focus_force()
                return
            except (tk.TclError, ValueError):
                # Window was closed or invalid, remove from tracking
                del self.active_windows[selected]

        if selected == "Geometry Mode":
            self._open_geometry_mode()
        elif selected == "Equation Mode":
            self._open_equation_mode()
        elif selected == "Polynomial Equation Mode":
            self._open_polynomial_mode()
        elif selected == "Vector Mode":
            self._open_vector_mode()
        elif selected == "Không có mode":
            messagebox.showwarning("Cảnh báo", "Vui lòng chọn một chế độ hợp lệ.")
        else:
            messagebox.showinfo("Thông báo", f"Mode '{selected}' chưa được hỗ trợ.\nHiện chỉ có giao diện UI (không logic).")

    def _open_geometry_mode(self):
        try:
            # Load config cho Geometry Mode
            geometry_config = config_loader.get_mode_config("Geometry Mode")
            
            from views.geometry_view import GeometryView
            geometry_window = tk.Toplevel(self.root)
            view = GeometryView(geometry_window, config=geometry_config)
            
            # Track window and view as tuple
            self.active_windows["Geometry Mode"] = (geometry_window, view)
            geometry_window.protocol("WM_DELETE_WINDOW", 
                                    lambda: self.on_mode_window_close("Geometry Mode"))
            
        except Exception as e:
            messagebox.showerror("Lỗi", f"Không thể mở Geometry Mode:\n{str(e)}")

    def _open_equation_mode(self):
        try:
            # Load config cho Equation Mode
            equation_config = config_loader.get_mode_config("Equation Mode")
            
            from views.equation_view import EquationView
            equation_window = tk.Toplevel(self.root)
            view = EquationView(equation_window, config=equation_config)
            
            # Track window and view as tuple
            self.active_windows["Equation Mode"] = (equation_window, view)
            equation_window.protocol("WM_DELETE_WINDOW",
                                   lambda: self.on_mode_window_close("Equation Mode"))
            
        except Exception as e:
            messagebox.showerror("Lỗi", f"Không thể mở Equation Mode:\n{str(e)}")

    def _open_polynomial_mode(self):
        try:
            # Load config cho Polynomial Mode
            polynomial_config = config_loader.get_mode_config("Polynomial Equation Mode")
            
            from views.polynomial_equation_view import PolynomialEquationView
            polynomial_window = tk.Toplevel(self.root)
            view = PolynomialEquationView(polynomial_window, config=polynomial_config)
            
            # Track window and view as tuple
            self.active_windows["Polynomial Equation Mode"] = (polynomial_window, view)
            polynomial_window.protocol("WM_DELETE_WINDOW",
                                      lambda: self.on_mode_window_close("Polynomial Equation Mode"))
            
        except Exception as e:
            messagebox.showerror("Lỗi", f"Không thể mở Polynomial Mode:\n{str(e)}")

    def _open_vector_mode(self):
        try:
            from views.vector_view import VectorView
            view = VectorView(self.root)  # VectorView creates its own Toplevel
            
            # Track VectorView's root window and view as tuple
            self.active_windows["Vector Mode"] = (view.root, view)
            view.root.protocol("WM_DELETE_WINDOW",
                              lambda: self.on_mode_window_close("Vector Mode"))
            
        except Exception as e:
            messagebox.showerror("Lỗi", f"Không thể mở Vector Mode:\n{str(e)}")

    def on_mode_window_close(self, mode_name: str):
        """Handle mode window closing with proper tuple handling"""
        try:
            if mode_name in self.active_windows:
                window, view = self.active_windows[mode_name]
                try:
                    window.destroy()
                except Exception:
                    pass  # Window might be already destroyed
                del self.active_windows[mode_name]
        except Exception as e:
            print(f"Error closing {mode_name} window: {e}")

    def run(self):
        # Căn giữa cửa sổ
        self.root.eval('tk::PlaceWindow . center')
        
        # Setup close handler
        self.root.protocol("WM_DELETE_WINDOW", self.on_closing)
        
        self.root.mainloop()

    def on_closing(self):
        """Handle application closing with proper cleanup"""
        try:
            # Close all active mode windows using tuple structure
            for mode_name, pair in list(self.active_windows.items()):
                try:
                    window, view = pair
                    window.destroy()
                except Exception:
                    pass  # Ignore cleanup errors
            
            # Close main window
            self.root.destroy()
            
        except Exception as e:
            print(f"Error during closing: {e}")
            self.root.destroy()


if __name__ == "__main__":
    app = MainView()
    app.run()