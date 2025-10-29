import tkinter as tk
from tkinter import ttk, messagebox

class EquationView:
    def __init__(self, window, config=None):
        self.window = window
        self.window.title("Equation Mode - Giải Hệ Phương Trình Thực")
        self.window.geometry("850x1050")
        self.window.configure(bg="#F5F5F5")

        # Lưu config được truyền vào
        self.config = config or {}

        # Khởi tạo biến
        self.so_an_var = tk.StringVar(value="2")
        self.phien_ban_var = tk.StringVar()

        # Biến lưu các ô nhập liệu và kết quả
        self.input_entries = []
        self.result_entries = []

        # Trạng thái hiện tại
        self.is_imported_mode = False
        self.has_manual_data = False

        # Load danh sách phiên bản từ config
        self.phien_ban_list = self._get_available_versions()
        self.phien_ban_var.set(self.phien_ban_list[0] if self.phien_ban_list else "fx799")

        self._setup_ui()
        self._update_input_fields()
        self._update_button_visibility()
    
    def _get_available_versions(self):
        """Lấy danh sách phiên bản từ config hoặc sử dụng mặc định"""
        try:
            if self.config and 'common' in self.config and 'versions' in self.config['common']:
                versions_data = self.config['common']['versions']
                if 'versions' in versions_data:
                    return versions_data['versions']
        except Exception as e:
            print(f"Warning: Không thể load versions từ config: {e}")
        
        # Fallback nếu không có config
        return ["fx799", "fx800", "fx801", "fx802", "fx803"]
    
    def _get_equation_prefixes(self):
        """Lấy prefixes cho equation từ config"""
        try:
            if self.config and 'equation' in self.config and 'prefixes' in self.config['equation']:
                prefixes_data = self.config['equation']['prefixes']
                if 'versions' in prefixes_data:
                    return prefixes_data['versions']
        except Exception as e:
            print(f"Warning: Không thể load equation prefixes từ config: {e}")
        
        return None

    def _setup_ui(self):
        # Frame chính với scrollbar
        main_frame = tk.Frame(self.window, bg="#F5F5F5")
        main_frame.pack(fill="both", expand=True, padx=20, pady=15)

        # Tiêu đề
        title_label = tk.Label(
            main_frame,
            text="🧠 EQUATION MODE v2.0 - GIẢI HỆ PHƯNG TRÌNH",
            font=("Arial", 18, "bold"),
            bg="#F5F5F5",
            fg="#2E7D32"
        )
        title_label.pack(pady=(0, 15))

        # === KHUNG LỰA CHỌ4N THAM SỐ ===
        control_frame = tk.LabelFrame(
            main_frame,
            text="⚙️ THIẾ4T LẬP PHƯNG TRÌNH",
            font=("Arial", 11, "bold"),
            bg="#FFFFFF",
            fg="#1B5299",
            bd=2,
            relief="groove"
        )
        control_frame.pack(fill="x", pady=10, padx=10)

        # Dòng 1: Chọn số ẩn
        row1 = tk.Frame(control_frame, bg="#FFFFFF")
        row1.pack(fill="x", padx=15, pady=10)

        tk.Label(
            row1,
            text="Số ẩn:",
            font=("Arial", 10, "bold"),
            bg="#FFFFFF",
            fg="#333333",
            width=12
        ).pack(side="left")

        so_an_menu = ttk.Combobox(
            row1,
            textvariable=self.so_an_var,
            values=["2", "3", "4"],
            state="readonly",
            width=15,
            font=("Arial", 10)
        )
        so_an_menu.pack(side="left", padx=5)
        so_an_menu.bind("<<ComboboxSelected>>", self._on_so_an_changed)

        # Dòng 2: Chọn phiên bản
        row2 = tk.Frame(control_frame, bg="#FFFFFF")
        row2.pack(fill="x", padx=15, pady=10)

        tk.Label(
            row2,
            text="Phiên bản máy:",
            font=("Arial", 10, "bold"),
            bg="#FFFFFF",
            fg="#333333",
            width=12
        ).pack(side="left")

        phien_ban_menu = ttk.Combobox(
            row2,
            textvariable=self.phien_ban_var,
            values=self.phien_ban_list,
            state="readonly",
            width=15,
            font=("Arial", 10)
        )
        phien_ban_menu.pack(side="left", padx=5)
        phien_ban_menu.bind("<<ComboboxSelected>>", self._on_phien_ban_changed)
        
        # Config status
        config_status = "Config: ✅ Loaded" if self.config else "Config: ⚠️ Fallback"
        tk.Label(
            row2,
            text=config_status,
            font=("Arial", 8),
            bg="#FFFFFF",
            fg="#666666"
        ).pack(side="right", padx=20)

        # === KHUNG HƯỚNG DẪN ===
        guide_frame = tk.LabelFrame(
            main_frame,
            text="💡 HƯỚNG DẪN NHẬP LIỆU",
            font=("Arial", 10, "bold"),
            bg="#E3F2FD",
            fg="#1565C0",
            bd=1,
            relief="solid"
        )
        guide_frame.pack(fill="x", pady=5, padx=10)

        guide_text = (
            "• Hỗ trợ biểu thức: sqrt(5), sin(pi/2), 1/2, 2^3, log(10), v.v.\n"
            "• Nhập hệ số cách nhau bằng dấu phẩy\n"
            "• Ô trống sẽ tự động điền số 0"
        )

        guide_label = tk.Label(
            guide_frame,
            text=guide_text,
            font=("Arial", 9),
            bg="#E3F2FD",
            fg="#333333",
            justify="left"
        )
        guide_label.pack(padx=10, pady=8)

        # === KHUNG NHẬP LIỆU ===
        self.input_frame = tk.LabelFrame(
            main_frame,
            text="📝 NHẬP HỆ SỐ PHƯNG TRÌNH",
            font=("Arial", 11, "bold"),
            bg="#FFFFFF",
            fg="#1B5299",
            bd=2,
            relief="groove"
        )
        self.input_frame.pack(fill="x", pady=10, padx=10)

        # === KHUNG KẾT QUẢ MÃ HÓA ===
        self.result_frame = tk.LabelFrame(
            main_frame,
            text="🔐 KẾT QUẢ MÃ HÓA",
            font=("Arial", 11, "bold"),
            bg="#FFFFFF",
            fg="#7B1FA2",
            bd=2,
            relief="groove"
        )
        self.result_frame.pack(fill="x", pady=10, padx=10)

        # === KHUNG KẾT QUẢ NGHIỆM ===
        self.frame_nghiem = tk.LabelFrame(
            main_frame,
            text="🎯 KẾT QUẢ NGHIỆM",
            font=("Arial", 11, "bold"),
            bg="#FFFFFF",
            fg="#D35400",
            bd=2,
            relief="groove"
        )
        self.frame_nghiem.pack(fill="x", pady=10, padx=10)

        self.entry_nghiem = tk.Entry(
            self.frame_nghiem,
            width=80,
            font=("Arial", 10),
            justify="center"
        )
        self.entry_nghiem.pack(padx=15, pady=12, fill="x")
        self.entry_nghiem.insert(0, "Chưa có kết quả nghiệm")
        self.entry_nghiem.config(bg="#FFF9E6", fg="#FF6F00")

        # === KHUNG KẾT QUẢ TỔNG ===
        self.frame_tong = tk.LabelFrame(
            main_frame,
            text="📦 KẾT QUẢ TỔNG (CHO MÁY TÍNH)",
            font=("Arial", 11, "bold"),
            bg="#FFFFFF",
            fg="#2E7D32",
            bd=2,
            relief="groove"
        )
        self.frame_tong.pack(fill="x", pady=10, padx=10)

        self.entry_tong = tk.Entry(
            self.frame_tong,
            width=80,
            font=("Courier New", 9),
            justify="center"
        )
        self.entry_tong.pack(padx=15, pady=12, fill="x")
        
        # Hiển thị config info trong kết quả tổng
        config_info = "Config loaded successfully" if self.config else "Using fallback config"
        self.entry_tong.insert(0, f"Equation Mode v2.0 - {config_info}")
        self.entry_tong.config(bg="#F1F8E9")

        # === KHUNG NÚT CHỨC NĂNG ===
        button_frame = tk.Frame(main_frame, bg="#F5F5F5")
        button_frame.pack(fill="x", pady=20)

        # Nút Import Excel (ban đầu hiển thị)
        self.btn_import = tk.Button(
            button_frame,
            text="📁 Import Excel",
            bg="#FF9800",
            fg="white",
            font=("Arial", 10, "bold"),
            width=14,
            height=1,
            command=self._placeholder_action
        )
        self.btn_import.pack(side="left", padx=5)

        # Nút Xử lý (luôn hiển thị)
        self.btn_process = tk.Button(
            button_frame,
            text="🔄 Xử lý & Giải nghiệm",
            bg="#2196F3",
            fg="white",
            font=("Arial", 10, "bold"),
            width=16,
            height=1,
            command=self._placeholder_action
        )
        self.btn_process.pack(side="left", padx=5)

        # Nút Import File Excel Khác (ban đầu ẩn)
        self.btn_import_other = tk.Button(
            button_frame,
            text="📂 Import File Khác",
            bg="#9C27B0",
            fg="white",
            font=("Arial", 10, "bold"),
            width=14,
            height=1,
            command=self._placeholder_action
        )

        # Nút Quay lại (ban đầu ẩn)
        self.btn_quay_lai = tk.Button(
            button_frame,
            text="↩️ Quay lại",
            bg="#607D8B",
            fg="white",
            font=("Arial", 10, "bold"),
            width=14,
            height=1,
            command=self._placeholder_action
        )

        # === THÔNG BÁO TRẠNG THÁI ===
        self.status_label = tk.Label(
            main_frame,
            text="🟢 Sẵn sàng nhập liệu và giải hệ phương trình",
            font=("Arial", 10, "bold"),
            bg="#F5F5F5",
            fg="#2E7D32"
        )
        self.status_label.pack(pady=10)

        # Nút đóng
        close_btn = tk.Button(
            main_frame,
            text="Đóng",
            command=self.window.destroy,
            bg="#F44336",
            fg="white",
            font=("Arial", 10, "bold"),
            width=15,
            height=1
        )
        close_btn.pack(pady=10)

        # Footer
        footer_label = tk.Label(
            main_frame,
            text="Phiên bản: v2.0 Giải nghiệm thực • Hỗ trợ biểu thức phức tạp • Config-driven",
            font=("Arial", 8),
            bg="#F5F5F5",
            fg="#666666"
        )
        footer_label.pack(side="bottom", pady=5)

    def _on_so_an_changed(self, event=None):
        """Cập nhật số ô nhập liệu khi số ẩn thay đổi"""
        self._update_input_fields()
        self.status_label.config(text=f"Đã chọn hệ {self.so_an_var.get()} phương trình {self.so_an_var.get()} ẩn")

    def _on_phien_ban_changed(self, event=None):
        """Cập nhật khi phiên bản thay đổi"""
        selected_version = self.phien_ban_var.get()
        # Lấy prefix từ config nếu có
        prefixes = self._get_equation_prefixes()
        prefix_info = ""
        if prefixes and selected_version in prefixes:
            prefix_info = f" - Prefix: {prefixes[selected_version]['base_prefix']}"
        
        self.status_label.config(text=f"Đã chọn phiên bản: {selected_version}{prefix_info}")

    def _update_input_fields(self):
        """Cập nhật các ô nhập liệu và kết quả dựa trên số ẩn"""
        try:
            so_an = int(self.so_an_var.get())

            # Xóa các widget cũ
            for widget in self.input_frame.winfo_children():
                widget.destroy()
            for widget in self.result_frame.winfo_children():
                widget.destroy()

            self.input_entries = []
            self.result_entries = []

            # Tạo các ô nhập liệu
            tk.Label(
                self.input_frame,
                text=f"Nhập {so_an + 1} hệ số cho mỗi phương trình (cách nhau bằng dấu phẩy):",
                font=("Arial", 9, "bold"),
                bg="#FFFFFF",
                fg="#333333"
            ).pack(anchor="w", padx=15, pady=8)

            # Tạo label và entry cho từng phương trình
            labels = self._get_input_labels(so_an)
            for i, label_text in enumerate(labels):
                row_frame = tk.Frame(self.input_frame, bg="#FFFFFF")
                row_frame.pack(fill="x", padx=15, pady=6)

                tk.Label(
                    row_frame,
                    text=label_text,
                    font=("Arial", 9),
                    bg="#FFFFFF",
                    fg="#333333",
                    width=35
                ).pack(side="left")

                entry = tk.Entry(row_frame, width=45, font=("Arial", 9))
                entry.pack(side="left", padx=5, fill="x", expand=True)
                entry.bind('<KeyRelease>', self._on_manual_input)
                self.input_entries.append(entry)

            # Tạo các ô kết quả mã hóa
            tk.Label(
                self.result_frame,
                text=f"Kết quả mã hóa ({self._get_result_count(so_an)} hệ số):",
                font=("Arial", 9, "bold"),
                bg="#FFFFFF",
                fg="#333333"
            ).pack(anchor="w", padx=15, pady=8)

            # Tạo grid cho ô kết quả
            if so_an == 2:
                labels_2an = ["a11", "a12", "c1", "a21", "a22", "c2"]
                self._create_result_grid(labels_2an, 2, 3)
            elif so_an == 3:
                labels_3an = ["a11", "a12", "a13", "c1", "a21", "a22", "a23", "c2", "a31", "a32", "a33", "c3"]
                self._create_result_grid(labels_3an, 3, 4)
            elif so_an == 4:
                labels_4an = ["a11", "a12", "a13", "a14", "c1", "a21", "a22", "a23", "a24", "c2",
                              "a31", "a32", "a33", "a34", "c3", "a41", "a42", "a43", "a44", "c4"]
                self._create_result_grid(labels_4an, 4, 5)

        except Exception as e:
            print(f"Lỗi khi cập nhật ô nhập liệu: {e}")

    def _create_result_grid(self, labels, rows, cols):
        """Tạo grid cho kết quả mã hóa"""
        for row in range(rows):
            row_frame = tk.Frame(self.result_frame, bg="#FFFFFF")
            row_frame.pack(fill="x", padx=15, pady=4)

            tk.Label(
                row_frame,
                text=f"PT {row + 1}:",
                font=("Arial", 8, "bold"),
                bg="#FFFFFF",
                fg="#333333",
                width=6
            ).pack(side="left", padx=2)

            for col in range(cols):
                idx = row * cols + col
                if idx < len(labels):
                    # Label hệ số
                    label_frame = tk.Frame(row_frame, bg="#FFFFFF")
                    label_frame.pack(side="left", padx=2)

                    tk.Label(
                        label_frame,
                        text=labels[idx] + ":",
                        font=("Arial", 8, "bold"),
                        bg="#FFFFFF",
                        fg="#7B1FA2",
                        width=4
                    ).pack(side="top")

                    # Entry kết quả
                    entry = tk.Entry(label_frame, width=12, font=("Arial", 8), state='readonly', bg="#F3E5F5")
                    entry.pack(side="top", padx=2)
                    self.result_entries.append(entry)

    def _get_input_labels(self, so_an):
        """Lấy danh sách label cho các ô nhập liệu"""
        config = {
            2: [
                "Phương trình 1 (a₁₁, a₁₂, c₁):",
                "Phương trình 2 (a₂₁, a₂₂, c₂):"
            ],
            3: [
                "Phương trình 1 (a₁₁, a₁₂, a₁₃, c₁):",
                "Phương trình 2 (a₂₁, a₂₂, a₂₃, c₂):",
                "Phương trình 3 (a₃₁, a₃₂, a₃₃, c₃):"
            ],
            4: [
                "Phương trình 1 (a₁₁, a₁₂, a₁₃, a₁₄, c₁):",
                "Phương trình 2 (a₂₁, a₂₂, a₂₃, a₂₄, c₂):",
                "Phương trình 3 (a₃₁, a₃₂, a₃₃, a₃₄, c₃):",
                "Phương trình 4 (a₄₁, a₄₂, a₄₃, a₄₄, c₄):"
            ]
        }
        return config.get(so_an, config[2])

    def _get_result_count(self, so_an):
        """Tính số ô kết quả cần hiển thị"""
        config = {
            2: 6,  # 2 ẩn: 6 hệ số
            3: 12,  # 3 ẩn: 12 hệ số
            4: 20  # 4 ẩn: 20 hệ số
        }
        return config.get(so_an, 6)

    def _on_manual_input(self, event=None):
        """Xử lý khi người dùng nhập liệu thủ công"""
        self.has_manual_data = True
        self.is_imported_mode = False
        self._update_button_visibility()

    def _update_button_visibility(self):
        """Ẩn ứng hiển thị nút dựa trên trạng thái hiện tại"""
        # Ẩn tất cả các nút trước
        self.btn_import.pack_forget()
        self.btn_import_other.pack_forget()
        self.btn_quay_lai.pack_forget()

        if self.is_imported_mode:
            # Trạng thái import từ Excel
            self.btn_import_other.pack(side="left", padx=5)
            self.btn_quay_lai.pack(side="left", padx=5)
            self.btn_process.pack(side="left", padx=5)
        elif self.has_manual_data:
            # Trạng thái nhập liệu thủ công
            self.btn_process.pack(side="left", padx=5)
        else:
            # Trạng thái ban đầu
            self.btn_import.pack(side="left", padx=5)
            self.btn_process.pack(side="left", padx=5)

    def _placeholder_action(self):
        """Hành động placeholder"""
        messagebox.showinfo("Thông báo", "Chức năng đang phát triển. Chỉ là giao diện v2.0!")


if __name__ == "__main__":
    root = tk.Tk()
    app = EquationView(root)
    root.mainloop()
