import tkinter as tk
from tkinter import ttk, messagebox, filedialog
import csv
from services.integral.integral_encoding_service import IntegralEncodingService

class IntegralView:

    def __init__(self, parent):
        self.parent = parent
        self.root = tk.Toplevel(parent)
        self.root.title("Integral Mode - ConvertKeylogApp")
        self.root.geometry("800x600")
        self.root.configure(bg="#F0F8FF")
        self.root.resizable(False, False)

        self.service = IntegralEncodingService()
        self.mode_var = tk.StringVar(value="3")  # ← Mặc định là mode 3
        self.latex_entry = None
        self.keylog_output = None
        self.batch_results = []

        self.mode_data = {
            "1": {
                "title": "Mode 1: Tích phân xác định",
                "description": "Tích phân có cận trên và cận dưới. Format: y{function})${lower}${upper})",
                "example": "\\int_{0}^{1} x^2 dx"
            },
            "2": {
                "title": "Mode 2: Tích phân xác định",
                "description": "Tích phân có cận trên và cận dưới. Format: y{function})${lower}${upper})",
                "example": "\\int_{a}^{b} x^3 dx"
            },
            "3": {
                "title": "Mode 3: Tích phân xác định",
                "description": "Tích phân có cận trên và cận dưới. Format: y{function}),{lower},{upper})",
                "example": "\\int_{0}^{1} \\sin(x) dx"
            },
            "4": {
                "title": "Mode 4: Tích phân xác định",
                "description": "Tích phân có cận trên và cận dưới. Format: y{function}),{lower},{upper})",
                "example": "\\int_{1}^{2} \\frac{1}{x} dx"
            }
        }

        self._setup_ui()

    def _setup_ui(self):
        main = tk.Frame(self.root, bg="#F0F8FF")
        main.pack(fill="both", expand=True, padx=15, pady=10)

        header = tk.Frame(main, bg="#8E44AD", height=60)
        header.pack(fill="x", pady=(0, 12))
        header.pack_propagate(False)

        bar = tk.Frame(header, bg="#8E44AD")
        bar.pack(expand=True, fill="both")
        icon = tk.Label(bar, text="∫", font=("Arial", 28), bg="#8E44AD", fg="white")
        icon.pack(side="left", padx=(20, 10))
        title = tk.Label(bar, text="INTEGRAL MODE", font=("Arial", 16, "bold"), bg="#8E44AD", fg="white")
        title.pack(side="left")
        subtitle = tk.Label(bar, text="LaTeX → Keylog (4 Format Modes)", font=("Arial", 10), bg="#8E44AD", fg="#E8DAEF")
        subtitle.pack(side="right", padx=(0, 20))

        mode_label = tk.Label(main, text="Chọn Mode Keylog Format:", font=("Arial", 12, "bold"), bg="#F0F8FF",
                              fg="#8E44AD")
        mode_label.pack(anchor="w", padx=10, pady=(10, 3))

        mode_dropdown = ttk.Combobox(main, textvariable=self.mode_var, state="readonly", font=("Arial", 11), width=75)
        mode_dropdown['values'] = (
            "1 - MathI /MathO",
            "2 - MathI /DecimalO",
            "3 - LineI /LineO",
            "4 - LineI /DecimalO"
        )
        mode_dropdown.current(2)  # ← chọn index 2 (mode 3) mặc định
        mode_dropdown.pack(padx=10, pady=5)
        mode_dropdown.bind("<<ComboboxSelected>>", self._on_mode_change)

        self.info_frame = tk.Frame(main, bg="#E8F4F8", bd=2, relief="solid")
        self.info_frame.pack(fill="x", padx=10, pady=(10, 5))

        # Mặc định: mode 3
        mode3_info = self.mode_data["3"]
        self.info_title = tk.Label(self.info_frame, text="📌 " + mode3_info["title"],
                                   font=("Arial", 11, "bold"), bg="#E8F4F8", fg="#8E44AD", anchor="w")
        self.info_title.pack(fill="x", padx=10, pady=(8, 3))

        self.info_desc = tk.Label(self.info_frame, text=mode3_info["description"],
                                  font=("Arial", 10), bg="#E8F4F8", fg="#5A6C7D", anchor="w")
        self.info_desc.pack(fill="x", padx=10, pady=(0, 8))

        label = tk.Label(main, text="Nhập LaTeX:", font=("Arial", 12, "bold"), bg="#F0F8FF", fg="#8E44AD")
        label.pack(anchor="w", padx=10, pady=(10, 3))
        self.latex_entry = tk.Entry(main, font=("Courier New", 13), bd=2, relief="groove", width=80)
        self.latex_entry.pack(padx=10, pady=5)
        self.latex_entry.insert(0, mode3_info["example"])

        btn_frame = tk.Frame(main, bg="#F0F8FF")
        btn_frame.pack(fill="x", pady=12)

        self.btn_import = tk.Button(btn_frame, text="📁 Import Excel", command=self._import_excel, bg="#16A085",
                                    fg="white", font=("Arial", 10, "bold"), width=15)
        self.btn_import.pack(side="left", padx=5)

        self.btn_encode = tk.Button(btn_frame, text="🚀 Encode", command=self._encode, bg="#8E44AD", fg="white",
                                    font=("Arial", 10, "bold"), width=15)
        self.btn_encode.pack(side="left", padx=5)

        self.btn_copy = tk.Button(btn_frame, text="📋 Copy", command=self._copy, bg="#9C27B0", fg="white",
                                  font=("Arial", 10, "bold"), width=12)
        self.btn_copy.pack(side="left", padx=5)

        self.btn_clear = tk.Button(btn_frame, text="🧹 Clear", command=self._clear, bg="#607D8B", fg="white",
                                   font=("Arial", 10, "bold"), width=10)
        self.btn_clear.pack(side="left", padx=5)

        output_label = tk.Label(main, text="Keylog Output:", font=("Arial", 12, "bold"), bg="#F0F8FF", fg="#8E44AD")
        output_label.pack(anchor="w", padx=10, pady=(10, 3))
        self.keylog_output = tk.Text(main, font=("Flexio Fx799VN", 11), height=6, bd=2, relief="groove", wrap="word")
        self.keylog_output.pack(padx=10, pady=5, fill="both", expand=True)
        self.keylog_output.config(state="disabled")

        self.status_label = tk.Label(self.root, text="⚠️ Chưa encode", font=("Arial", 10, "bold"), bg="#F0F8FF",
                                     fg="#E67E22", relief="sunken", bd=1, anchor="w", pady=4)
        self.status_label.pack(side="bottom", fill="x")

    def _on_mode_change(self, event):
        selected = self.mode_var.get().split(" - ")[0]
        mode_info = self.mode_data.get(selected)

        if mode_info:
            self.info_title.config(text="📌 " + mode_info["title"])
            self.info_desc.config(text=mode_info["description"])
            self.latex_entry.delete(0, tk.END)
            self.latex_entry.insert(0, mode_info["example"])
            self._set_status(f"Đã chọn {mode_info['title']}")

    def _import_excel(self):
        file_path = filedialog.askopenfilename(
            title="Chọn file CSV/Excel",
            filetypes=[("CSV files", "*.csv"), ("Excel files", "*.xlsx"), ("All files", "*.*")]
        )

        if not file_path:
            return

        try:
            self._set_status("🔄 Đang đọc file...")

            rows = []
            latex_col_idx = -1
            mode_col_idx = -1

            if file_path.endswith('.csv'):
                with open(file_path, 'r', encoding='utf-8') as f:
                    reader = csv.reader(f)
                    for row_idx, row in enumerate(reader):
                        if row_idx == 0:
                            for col_idx, header in enumerate(row):
                                header_lower = header.strip().lower()
                                if header_lower in ['latex', 'int_input']:
                                    latex_col_idx = col_idx
                                elif header_lower == 'mode':
                                    mode_col_idx = col_idx

                            if latex_col_idx == -1:
                                messagebox.showerror("Lỗi",
                                                     "❌ Không tìm thấy cột 'latex' hoặc 'int_input' trong hàng header")
                                self._set_status("❌ Thiếu cột latex")
                                return
                        else:
                            if len(row) > latex_col_idx and row[latex_col_idx].strip():
                                latex = row[latex_col_idx].strip()
                                mode = "3"
                                if mode_col_idx != -1 and len(row) > mode_col_idx and row[mode_col_idx].strip():
                                    mode = row[mode_col_idx].strip()
                                rows.append((latex, mode))
            else:
                try:
                    import openpyxl
                    wb = openpyxl.load_workbook(file_path)
                    ws = wb.active
                    for row_idx, row in enumerate(ws.iter_rows(values_only=True), 1):
                        if row_idx == 1:
                            for col_idx, header in enumerate(row):
                                if header:
                                    header_lower = str(header).strip().lower()
                                    if header_lower in ['latex', 'int_input']:
                                        latex_col_idx = col_idx
                                    elif header_lower == 'mode':
                                        mode_col_idx = col_idx

                            if latex_col_idx == -1:
                                messagebox.showerror("Lỗi",
                                                     "❌ Không tìm thấy cột 'latex' hoặc 'int_input' trong hàng header")
                                self._set_status("❌ Thiếu cột latex")
                                return
                        else:
                            if row and latex_col_idx < len(row) and row[latex_col_idx]:
                                latex = str(row[latex_col_idx]).strip()
                                mode = "3"
                                if mode_col_idx != -1 and mode_col_idx < len(row) and row[mode_col_idx]:
                                    mode = str(row[mode_col_idx]).strip()
                                rows.append((latex, mode))
                except ImportError:
                    messagebox.showerror("Lỗi", "Cần cài đặt openpyxl để đọc Excel\npip install openpyxl")
                    return

            if not rows:
                messagebox.showwarning("Cảnh báo", "File không có dữ liệu hợp lệ")
                return

            self._process_batch(rows)

        except Exception as e:
            messagebox.showerror("Lỗi", f"Lỗi đọc file: {str(e)}")
            self._set_status("❌ Lỗi đọc file")

    # ... (không đổi các hàm còn lại)
