"""Main application window - tương tự MainView của TL."""

import tkinter as tk
from tkinter import messagebox
from gui.components.base_window import BaseWindow


class MainWindow(BaseWindow):
    """Main application window implementation - giống TL MainView."""
    
    def __init__(self):
        # Khởi tạo window với title và size giống TL
        self.root = tk.Tk()
        self.root.title("Convert Application - Mode Selector")
        self.root.geometry("480x320")
        self.root.configure(bg="#e8f0f7")  # Màu nền nhẹ xanh pastel giống TL

        # Load danh sách mode
        self.modes = self._load_modes()
        self.mode_var = tk.StringVar(value=self.modes[0] if self.modes else "Không có mode")

        self._setup_ui()

    def _load_modes(self):
        """Load modes từ config - giống TL logic"""
        try:
            # TODO: Implement load from config/modes.json
            return ["Geometry Mode", "Equation Mode", "Polynomial Equation Mode"]
        except Exception as e:
            messagebox.showwarning("Cảnh báo", f"Không thể load file modes.json mặc định:\n{str(e)}")
            return ["Geometry Mode"]

    def _setup_ui(self):
        """Tạo giao diện người dùng chính - hoàn toàn giống TL"""

        # === Tiêu đề lớn ===
        title_frame = tk.Frame(self.root, bg="#4A90E2")
        title_frame.pack(fill="x")

        title_label = tk.Label(
            title_frame,
            text="🧮 Convert Application",
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

        # Custom OptionMenu (dropdown) giống TL
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

        # Nút chọn mode - giống TL
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

        # Nút thoát - giống TL
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
            text="📁 File cấu hình: config/modes.json",
            font=("Segoe UI", 9),
            bg="#dfe7ef",
            fg="#444",
            pady=5
        )
        footer.pack(side="bottom", fill="x")

    def _open_selected_mode(self):
        """Xử lý khi chọn mode - giống TL logic"""
        selected = self.mode_var.get()

        if selected == "Geometry Mode":
            self._open_geometry_mode()
        elif selected == "Equation Mode":
            self._open_equation_mode()
        elif selected == "Polynomial Equation Mode":
            self._open_polynomial_mode()
        elif selected == "Không có mode":
            messagebox.showwarning("Cảnh báo", "Vui lòng chọn một chế độ hợp lệ.")
        else:
            messagebox.showinfo("Thông báo", f"Mode '{selected}' chưa được hỗ trợ.")

    def _open_geometry_mode(self):
        """Mở Geometry Mode window"""
        try:
            from gui.windows.geometry_window import GeometryWindow
            geometry_window = tk.Toplevel(self.root)
            GeometryWindow(geometry_window)
        except Exception as e:
            messagebox.showerror("Lỗi", f"Không thể mở Geometry Mode:\n{str(e)}")

    def _open_equation_mode(self):
        """Mở Equation Mode window"""
        try:
            from gui.windows.equation_window import EquationWindow
            equation_window = tk.Toplevel(self.root)
            EquationWindow(equation_window)
        except Exception as e:
            messagebox.showerror("Lỗi", f"Lỗi khởi động Equation Mode:\n{str(e)}")

    def _open_polynomial_mode(self):
        """Mở Polynomial Mode window"""
        try:
            from gui.windows.polynomial_window import PolynomialWindow
            polynomial_window = tk.Toplevel(self.root)
            PolynomialWindow(polynomial_window)
        except Exception as e:
            messagebox.showerror("Lỗi", f"Không thể mở Polynomial Mode:\n{str(e)}")

    def setup_ui(self):
        """Override từ BaseWindow - đã implement trong _setup_ui()"""
        pass

    def run(self):
        """Chạy ứng dụng - giống TL"""
        # Căn giữa cửa sổ
        self.root.eval('tk::PlaceWindow . center')
        self.root.mainloop()


if __name__ == "__main__":
    app = MainWindow()
    app.run()