import tkinter as tk
from tkinter import messagebox

class GeometryView:
    def __init__(self, window):
        self.window = window
        self.window.title("Geometry Mode")
        self.window.geometry("700x700")
        self.window.configure(bg="#F8F9FA")

        # Biến và trạng thái
        self._initialize_variables()
        self._setup_ui()

    def _initialize_variables(self):
        """Khởi tạo tất cả biến"""
        self.dropdown1_var = tk.StringVar(value="")
        self.dropdown2_var = tk.StringVar(value="")
        self.kich_thuoc_A_var = tk.StringVar(value="3")
        self.kich_thuoc_B_var = tk.StringVar(value="3")
        self.pheptoan_var = tk.StringVar(value="")

        # Phên bản mặc định
        self.phien_ban_list = ["Phiên bản 1.0", "Phiên bản 2.0", "Phiên bản 3.0"]
        self.phien_ban_var = tk.StringVar(value=self.phien_ban_list[0])

    def _setup_ui(self):
        """Setup giao diện chính"""
        # Header
        self._create_header()
        
        self.main_container = tk.Frame(self.window, bg="#F8F9FA")
        self.main_container.pack(fill="both", expand=True, padx=10, pady=5)

        # Top frame với dropdown
        top_frame = tk.Frame(self.main_container, bg="#F8F9FA")
        top_frame.grid(row=0, column=0, columnspan=4, padx=10, pady=5, sticky="we")

        self._setup_dropdowns(top_frame)
        self._setup_group_a_frames()
        self._setup_group_b_frames()
        self._setup_control_frame()
        
        # Hiện thông báo
        self._show_ui_only_message()

    def _create_header(self):
        """Tạo header"""
        HEADER_COLORS = {
            "primary": "#2E86AB", "secondary": "#1B5299", "text": "#FFFFFF",
            "accent": "#F18F01", "success": "#4CAF50", "warning": "#FF9800"
        }

        # Main header frame
        self.header_frame = tk.Frame(self.window, bg=HEADER_COLORS["primary"], height=80)
        self.header_frame.pack(fill="x", padx=10, pady=5)
        self.header_frame.pack_propagate(False)

        header_content = tk.Frame(self.header_frame, bg=HEADER_COLORS["primary"])
        header_content.pack(fill="both", expand=True, padx=15, pady=10)

        # Logo và title
        left_section = tk.Frame(header_content, bg=HEADER_COLORS["primary"])
        left_section.pack(side="left", fill="y")

        logo_frame = tk.Frame(left_section, bg=HEADER_COLORS["primary"])
        logo_frame.pack(side="top", fill="x")
        tk.Label(logo_frame, text="🧠", font=("Arial", 20),
                 bg=HEADER_COLORS["primary"], fg=HEADER_COLORS["text"]).pack(side="left")
        tk.Label(logo_frame, text="Geometry Mode", font=("Arial", 16, "bold"),
                 bg=HEADER_COLORS["primary"], fg=HEADER_COLORS["text"]).pack(side="left", padx=(5, 20))

        # Operation selector
        operation_frame = tk.Frame(left_section, bg=HEADER_COLORS["primary"])
        operation_frame.pack(side="top", fill="x", pady=(5, 0))
        tk.Label(operation_frame, text="Phép toán:", font=("Arial", 10),
                 bg=HEADER_COLORS["primary"], fg=HEADER_COLORS["text"]).pack(side="left")

        operations = ["Tương giao", "Khoảng cách", "Diện tích", "Thể tích", "PT đường thẳng"]
        self.operation_menu = tk.OptionMenu(operation_frame, self.pheptoan_var, *operations)
        self.operation_menu.config(
            bg=HEADER_COLORS["secondary"], fg=HEADER_COLORS["text"],
            font=("Arial", 10, "bold"), width=15, relief="flat", borderwidth=0
        )
        self.operation_menu.pack(side="left", padx=(5, 0))

        # Phiên bản
        center_section = tk.Frame(header_content, bg=HEADER_COLORS["primary"])
        center_section.pack(side="left", fill="both", expand=True, padx=20)

        version_frame = tk.Frame(center_section, bg=HEADER_COLORS["primary"])
        version_frame.pack(side="top", fill="x")
        tk.Label(version_frame, text="Phiên bản:", font=("Arial", 9),
                 bg=HEADER_COLORS["primary"], fg=HEADER_COLORS["text"]).pack(side="left")

        self.version_menu = tk.OptionMenu(version_frame, self.phien_ban_var, *self.phien_ban_list)
        self.version_menu.config(
            bg=HEADER_COLORS["accent"], fg="white", font=("Arial", 9),
            width=15, relief="flat", borderwidth=0
        )
        self.version_menu.pack(side="left", padx=(5, 0))

    def _setup_dropdowns(self, parent):
        """Setup dropdown chọn nhóm"""
        shapes = ["Diểm", "Đường thẳng", "Mặt phẳng", "Đường tròn", "Mặt cầu"]

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

    def _setup_group_a_frames(self):
        """Setup frames cho nhóm A"""
        # Frame Điểm A
        self.frame_A_diem = tk.LabelFrame(
            self.main_container, text="🎯 NHÓM A - Điểm",
            bg="#FFFFFF", fg="#1B5299", font=("Arial", 10, "bold")
        )
        self.frame_A_diem.grid(row=1, column=0, columnspan=4, padx=10, pady=5, sticky="we")

        tk.Label(self.frame_A_diem, text="Kích thước:", bg="#FFFFFF").grid(row=0, column=0)
        tk.OptionMenu(self.frame_A_diem, self.kich_thuoc_A_var, "2", "3").grid(row=0, column=1)

        tk.Label(self.frame_A_diem, text="Nhập toạ độ:", bg="#FFFFFF").grid(row=1, column=0)
        self.entry_diem_A = tk.Entry(self.frame_A_diem, width=40)
        self.entry_diem_A.grid(row=1, column=1)

        # Frame Đường thẳng A
        self.frame_A_duong = tk.LabelFrame(
            self.main_container, text="📏 NHÓM A - Đường thẳng",
            bg="#FFFFFF", fg="#1B5299", font=("Arial", 10, "bold")
        )
        self.frame_A_duong.grid(row=2, column=0, columnspan=4, padx=10, pady=5, sticky="we")

        tk.Label(self.frame_A_duong, text="Nhập A1,B1,C1:", bg="#FFFFFF").grid(row=0, column=0)
        self.entry_duong_A = tk.Entry(self.frame_A_duong, width=40)
        self.entry_duong_A.grid(row=0, column=1)

        # Ẩn tất cả frame ban đầu
        self.frame_A_diem.grid_remove()
        self.frame_A_duong.grid_remove()

    def _setup_group_b_frames(self):
        """Setup frames cho nhóm B"""
        # Frame Điểm B
        self.frame_B_diem = tk.LabelFrame(
            self.main_container, text="🎯 NHÓM B - Điểm",
            bg="#FFFFFF", fg="#A23B72", font=("Arial", 10, "bold")
        )
        self.frame_B_diem.grid(row=3, column=0, columnspan=4, padx=10, pady=5, sticky="we")

        tk.Label(self.frame_B_diem, text="Kích thước:", bg="#FFFFFF").grid(row=0, column=0)
        tk.OptionMenu(self.frame_B_diem, self.kich_thuoc_B_var, "2", "3").grid(row=0, column=1)

        tk.Label(self.frame_B_diem, text="Nhập toạ độ:", bg="#FFFFFF").grid(row=1, column=0)
        self.entry_diem_B = tk.Entry(self.frame_B_diem, width=40)
        self.entry_diem_B.grid(row=1, column=1)

        # Ẩn frame ban đầu
        self.frame_B_diem.grid_remove()

    def _setup_control_frame(self):
        """Setup control frame với buttons và result display"""
        self.frame_tong = tk.LabelFrame(
            self.main_container, text="🎉 KẾ4T QUẢ & ĐIỀU KHIỂN",
            bg="#FFFFFF", font=("Arial", 10, "bold")
        )
        self.frame_tong.grid(row=4, column=0, columnspan=4, padx=10, pady=10, sticky="we")

        # Text widget hiển thị kết quả
        self.entry_tong = tk.Text(
            self.frame_tong,
            width=80,
            height=3,
            font=("Arial", 10),
            wrap=tk.WORD,
            bg="#F8F9FA",
            fg="black",
            relief="solid",
            bd=1,
            padx=5,
            pady=5
        )
        self.entry_tong.grid(row=0, column=0, columnspan=4, padx=5, pady=5, sticky="we")

        # Nút Import Excel
        self.btn_import_excel = tk.Button(
            self.frame_tong, text="📁 Import Excel",
            command=self._placeholder_action,
            bg="#FF9800", fg="white", font=("Arial", 9, "bold")
        )
        self.btn_import_excel.grid(row=1, column=0, columnspan=4, pady=5, sticky="we")

        # Frame cho nút thủ công
        self.frame_buttons = tk.Frame(self.frame_tong, bg="#FFFFFF")
        self.frame_buttons.grid(row=2, column=0, columnspan=4, pady=5, sticky="we")

        tk.Button(self.frame_buttons, text="🔄 Xử lý Nhóm A",
                  command=self._placeholder_action,
                  bg="#2196F3", fg="white", font=("Arial", 9)).grid(row=0, column=0, padx=5)
        tk.Button(self.frame_buttons, text="🔄 Xử lý Nhóm B",
                  command=self._placeholder_action,
                  bg="#2196F3", fg="white", font=("Arial", 9)).grid(row=0, column=1, padx=5)
        tk.Button(self.frame_buttons, text="🚀 Thực thi tất cả",
                  command=self._placeholder_action,
                  bg="#4CAF50", fg="white", font=("Arial", 9, "bold")).grid(row=0, column=2, padx=5)
        tk.Button(self.frame_buttons, text="💾 Xuất Excel",
                  command=self._placeholder_action,
                  bg="#FF9800", fg="white", font=("Arial", 9, "bold")).grid(row=0, column=3, padx=5)

    def _show_ui_only_message(self):
        """Hiện thông báo UI only"""
        self.entry_tong.insert(tk.END, "Giao diện Geometry Mode - Chỉ demo UI, không có logic xử lý")

    def _placeholder_action(self):
        """Hành động placeholder"""
        messagebox.showinfo("Thông báo", "Chức năng đang phát triển. Chỉ là giao diện!")


if __name__ == "__main__":
    root = tk.Tk()
    app = GeometryView(root)
    root.mainloop()
