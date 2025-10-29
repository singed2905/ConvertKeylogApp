import tkinter as tk
from tkinter import filedialog, messagebox

class KeylogConverterView:
    def __init__(self, window):
        self.window = window
        self.window.title("Keylog Converter Mode")
        self.window.geometry("720x480")
        self.window.configure(bg="#F5F5F5")

        self._setup_ui()

    def _setup_ui(self):
        main_frame = tk.Frame(self.window, bg="#F5F5F5")
        main_frame.pack(fill="both", expand=True, padx=20, pady=15)

        title_label = tk.Label(
            main_frame,
            text="⌨️ KEYLOG CONVERTER",
            font=("Arial", 18, "bold"),
            bg="#F5F5F5",
            fg="#2E7D32"
        )
        title_label.pack(pady=(0, 15))

        guide_frame = tk.LabelFrame(
            main_frame,
            text="💡 HƯỚNG DẪN",
            font=("Arial", 10, "bold"),
            bg="#E3F2FD",
            fg="#1565C0",
            bd=1,
            relief="solid"
        )
        guide_frame.pack(fill="x", pady=5, padx=10)

        guide_text = (
            "• Chọn file keylog để chuyển đổi\n"
            "• Hỗ trợ drag & drop (todo)\n"
            "• Kết quả hiển thị bên dưới"
        )
        tk.Label(
            guide_frame,
            text=guide_text,
            font=("Arial", 9),
            bg="#E3F2FD",
            fg="#333333",
            justify="left"
        ).pack(padx=10, pady=8)

        action_frame = tk.Frame(main_frame, bg="#F5F5F5")
        action_frame.pack(fill="x", pady=10)

        btn_open = tk.Button(
            action_frame,
            text="📁 Chọn file keylog",
            bg="#FF9800",
            fg="white",
            font=("Arial", 10, "bold"),
            width=18,
            height=1,
            command=self._choose_file
        )
        btn_open.pack(side="left", padx=5)

        btn_process = tk.Button(
            action_frame,
            text="🔄 Chuyển đổi",
            bg="#2196F3",
            fg="white",
            font=("Arial", 10, "bold"),
            width=14,
            height=1,
            command=self._process
        )
        btn_process.pack(side="left", padx=5)

        result_frame = tk.LabelFrame(
            main_frame,
            text="📦 KẾT QUẢ",
            font=("Arial", 11, "bold"),
            bg="#FFFFFF",
            fg="#2E7D32",
            bd=2,
            relief="groove"
        )
        result_frame.pack(fill="both", expand=True, pady=10, padx=10)

        self.entry_result = tk.Text(result_frame, height=12, font=("Courier New", 10), bg="#F1F8E9")
        self.entry_result.pack(padx=15, pady=12, fill="both", expand=True)

        footer_label = tk.Label(
            main_frame,
            text="Giao diện chỉ demo - chưa có logic xử lý",
            font=("Arial", 8),
            bg="#F5F5F5",
            fg="#666666"
        )
        footer_label.pack(side="bottom", pady=5)

    def _choose_file(self):
        filedialog.askopenfilename(title="Chọn file keylog")

    def _process(self):
        messagebox.showinfo("Thông báo", "Chức năng đang phát triển. Chỉ là giao diện!")
