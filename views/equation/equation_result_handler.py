"""Equation View Components - Result display handler"""
import tkinter as tk

class EquationResultHandler:
    """Xử lý hiển thị kết quả mã hóa và nghiệm"""
    
    def __init__(self, parent_view):
        self.parent = parent_view
        self.result_entries = []
    
    def create_result_grid(self, container, so_an):
        """Tạo grid hiển thị kết quả mã hóa"""
        try:
            # Xóa các widget cũ
            for widget in container.winfo_children():
                widget.destroy()
            
            self.result_entries = []
            
            # Tạo label hướng dẫn
            tk.Label(
                container,
                text=f"Kết quả mã hóa ({self._get_result_count(so_an)} hệ số):",
                font=("Arial", 9, "bold"),
                bg="#FFFFFF",
                fg="#333333"
            ).pack(anchor="w", padx=15, pady=8)
            
            # Tạo grid tương ứng với số ẩn
            if so_an == 2:
                labels_2an = ["a11", "a12", "c1", "a21", "a22", "c2"]
                self._create_grid_layout(container, labels_2an, 2, 3)
            elif so_an == 3:
                labels_3an = ["a11", "a12", "a13", "c1", "a21", "a22", "a23", "c2", "a31", "a32", "a33", "c3"]
                self._create_grid_layout(container, labels_3an, 3, 4)
            elif so_an == 4:
                labels_4an = ["a11", "a12", "a13", "a14", "c1", "a21", "a22", "a23", "a24", "c2",
                              "a31", "a32", "a33", "a34", "c3", "a41", "a42", "a43", "a44", "c4"]
                self._create_grid_layout(container, labels_4an, 4, 5)
        
        except Exception as e:
            print(f"Lỗi khi tạo grid kết quả: {e}")
    
    def _create_grid_layout(self, container, labels, rows, cols):
        """Tạo layout grid cho kết quả"""
        for row in range(rows):
            row_frame = tk.Frame(container, bg="#FFFFFF")
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
    
    def _get_result_count(self, so_an):
        """Tính số ô kết quả cần hiển thị"""
        config = {
            2: 6,   # 2 ẩn: 6 hệ số
            3: 12,  # 3 ẩn: 12 hệ số
            4: 20   # 4 ẩn: 20 hệ số
        }
        return config.get(so_an, 6)
    
    def update_results(self, encoded_results):
        """Cập nhật kết quả mã hóa"""
        for i, entry in enumerate(self.result_entries):
            if i < len(encoded_results):
                entry.config(state='normal')
                entry.delete(0, tk.END)
                entry.insert(0, str(encoded_results[i]))
                entry.config(state='readonly')
    
    def clear_results(self):
        """Xóa toàn bộ kết quả"""
        for entry in self.result_entries:
            entry.config(state='normal')
            entry.delete(0, tk.END)
            entry.config(state='readonly')
    
    def get_encoded_string(self):
        """Lấy chuỗi mã hóa hoàn chỉnh"""
        results = []
        for entry in self.result_entries:
            results.append(entry.get())
        return ','.join(results)
    
    def update_solution_display(self, solution_entry, solutions):
        """Cập nhật hiển thị nghiệm"""
        solution_entry.config(state='normal')
        solution_entry.delete(0, tk.END)
        
        if solutions:
            solution_text = ", ".join([f"{var}={val}" for var, val in solutions.items()])
            solution_entry.insert(0, solution_text)
            solution_entry.config(bg="#E8F5E8", fg="#2E7D32")
        else:
            solution_entry.insert(0, "Không có nghiệm hoặc hệ vô nghiệm")
            solution_entry.config(bg="#FFEBEE", fg="#D32F2F")
        
        solution_entry.config(state='readonly')
    
    def update_final_result(self, final_entry, encoded_string, metadata=None):
        """Cập nhật kết quả cuối cùng cho máy tính"""
        final_entry.config(state='normal')
        final_entry.delete(0, tk.END)
        
        if encoded_string:
            display_text = encoded_string
            if metadata:
                display_text += f" | Version: {metadata.get('version', 'unknown')}"
            
            final_entry.insert(0, display_text)
            final_entry.config(bg="#F1F8E9", fg="#2E7D32")
        else:
            final_entry.insert(0, "Chưa có kết quả mã hóa")
            final_entry.config(bg="#FFF3E0", fg="#FF6F00")
        
        final_entry.config(state='readonly')