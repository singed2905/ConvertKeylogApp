"""Refactored Equation View - Modular Architecture"""
import tkinter as tk
from tkinter import ttk, messagebox

# Import các component modules
from views.equation.equation_input_handler import EquationInputHandler
from views.equation.equation_result_handler import EquationResultHandler  
from views.equation.equation_ui_manager import EquationUIManager
from views.equation.equation_button_manager import EquationButtonManager
from views.equation.equation_config_manager import EquationConfigManager

class EquationView:
    """Main Equation View - Sử dụng các component modules"""
    
    def __init__(self, window, config=None):
        self.window = window
        self.window.title("Equation Mode - Giải Hệ Phương Trình Thực")
        self.window.geometry("850x1050")
        self.window.configure(bg="#F5F5F5")

        # Lưu config được truyền vào
        self.config = config or {}
        
        # Khởi tạo các biến trạng thái
        self._initialize_variables()
        
        # Khởi tạo các component managers
        self._initialize_components()
        
        # Thiết lập giao diện
        self._setup_ui()
        
        # Cập nhật hiển thị ban đầu
        self._update_input_fields()
        self._update_button_visibility()
    
    def _initialize_variables(self):
        """Khởi tạo các biến trạng thái"""
        # Biến giao diện
        self.so_an_var = tk.StringVar(value="2")
        self.phien_ban_var = tk.StringVar()
        
        # Trạng thái hiện tại
        self.is_imported_mode = False
        self.has_manual_data = False
        
        # Tham chiếu đến các widget chính
        self.input_frame = None
        self.result_frame = None
        self.solution_entry = None
        self.final_entry = None
        self.status_label = None
    
    def _initialize_components(self):
        """Khởi tạo các component managers"""
        # Config manager
        self.config_manager = EquationConfigManager(self.config)
        
        # Lấy danh sách phiên bản và thiết lập mặc định
        self.phien_ban_list = self.config_manager.get_available_versions()
        self.phien_ban_var.set(self.phien_ban_list[0] if self.phien_ban_list else "fx799")
        
        # UI manager
        self.ui_manager = EquationUIManager(self)
        
        # Input handler
        self.input_handler = EquationInputHandler(self)
        
        # Result handler
        self.result_handler = EquationResultHandler(self)
        
        # Button manager
        self.button_manager = EquationButtonManager(self)
    
    def _setup_ui(self):
        """Thiết lập giao diện chính"""
        # Sử dụng UI manager để tạo layout
        ui_components = self.ui_manager.setup_main_layout()
        
        # Lưu tham chiếu đến các frame chính
        self.input_frame = ui_components['input_frame']
        self.result_frame = ui_components['result_frame']
        self.status_label = ui_components['status_label']
        
        # Thiết lập các frame đặc biệt
        _, self.solution_entry = self.ui_manager._create_solution_frame(ui_components['main_frame'])
        _, self.final_entry = self.ui_manager._create_final_frame(ui_components['main_frame'])
        
        # Tạo các nút chức năng
        button_frame = ui_components['button_frame']
        self.button_manager.create_buttons(button_frame)
    
    def _update_input_fields(self):
        """Cập nhật các ô nhập liệu và kết quả dựa trên số ẩn"""
        try:
            so_an = int(self.so_an_var.get())
            
            # Cập nhật ô nhập liệu
            if self.input_handler and self.input_frame:
                self.input_handler.create_input_fields(self.input_frame, so_an)
            
            # Cập nhật grid kết quả
            if self.result_handler and self.result_frame:
                self.result_handler.create_result_grid(self.result_frame, so_an)
        
        except Exception as e:
            print(f"Lỗi khi cập nhật ô nhập liệu: {e}")
    
    def _update_button_visibility(self):
        """Cập nhật hiển thị nút"""
        if self.button_manager:
            self.button_manager.update_button_visibility()
    
    # ========== EVENT HANDLERS ==========
    def _on_so_an_changed(self, event=None):
        """Cập nhật số ô nhập liệu khi số ẩn thay đổi"""
        self._update_input_fields()
        if self.status_label:
            self.status_label.config(
                text=f"Đã chọn hệ {self.so_an_var.get()} phương trình {self.so_an_var.get()} ẩn"
            )
    
    def _on_phien_ban_changed(self, event=None):
        """Cập nhật khi phiên bản thay đổi"""
        selected_version = self.phien_ban_var.get()
        
        # Lấy prefix từ config nếu có
        prefixes = self.config_manager.get_equation_prefixes()
        prefix_info = ""
        if prefixes and selected_version in prefixes:
            prefix_info = f" - Prefix: {prefixes[selected_version]['base_prefix']}"
        
        if self.status_label:
            self.status_label.config(text=f"Đã chọn phiên bản: {selected_version}{prefix_info}")
    
    def _on_manual_input(self, event=None):
        """Xử lý khi người dùng nhập liệu thủ công"""
        self.has_manual_data = True
        self.is_imported_mode = False
        self._update_button_visibility()
    
    # ========== PUBLIC METHODS FOR FUTURE INTEGRATION ==========
    def get_current_equations(self):
        """Lấy dữ liệu phương trình hiện tại"""
        if self.input_handler:
            return self.input_handler.get_input_data()
        return []
    
    def set_equations(self, equation_data):
        """Thiết lập dữ liệu phương trình"""
        if self.input_handler:
            self.input_handler.set_inputs(equation_data)
    
    def get_encoded_results(self):
        """Lấy kết quả mã hóa hiện tại"""
        if self.result_handler:
            return self.result_handler.get_encoded_string()
        return ""
    
    def set_results(self, encoded_results, solutions=None, final_encoded=None):
        """Thiết lập kết quả đầy đủ"""
        if self.result_handler:
            # Cập nhật kết quả mã hóa
            self.result_handler.update_results(encoded_results)
            
            # Cập nhật nghiệm nếu có
            if solutions and self.solution_entry:
                self.result_handler.update_solution_display(self.solution_entry, solutions)
            
            # Cập nhật kết quả cuối cùng nếu có
            if final_encoded and self.final_entry:
                self.result_handler.update_final_result(
                    self.final_entry, final_encoded,
                    {"version": self.phien_ban_var.get()}
                )
    
    def reset_view(self):
        """Reset toàn bộ view về trạng thái ban đầu"""
        # Reset trạng thái
        self.is_imported_mode = False
        self.has_manual_data = False
        
        # Xóa dữ liệu nhập
        if self.input_handler:
            self.input_handler.clear_inputs()
            self.input_handler.unlock_inputs()
        
        # Xóa kết quả
        if self.result_handler:
            self.result_handler.clear_results()
        
        # Reset hiển thị kết quả
        if self.solution_entry:
            self.solution_entry.config(state='normal')
            self.solution_entry.delete(0, tk.END)
            self.solution_entry.insert(0, "Chưa có kết quả nghiệm")
            self.solution_entry.config(bg="#FFF9E6", fg="#FF6F00", state='readonly')
        
        if self.final_entry:
            self.final_entry.config(state='normal')
            self.final_entry.delete(0, tk.END)
            config_info = "Config loaded successfully" if self.config else "Using fallback config"
            self.final_entry.insert(0, f"Equation Mode v2.0 - {config_info}")
            self.final_entry.config(bg="#F1F8E9", state='readonly')
        
        # Cập nhật nút và trạng thái
        self._update_button_visibility()
        if self.status_label:
            self.status_label.config(
                text="🟢 Sẵn sàng nhập liệu và giải hệ phương trình",
                fg="#2E7D32"
            )
    
    # ========== LEGACY COMPATIBILITY METHODS ==========
    def _placeholder_action(self):
        """Hành động placeholder cho backward compatibility"""
        messagebox.showinfo("Thông báo", "Chức năng đang phát triển. Chỉ là giao diện v2.0!")


if __name__ == "__main__":
    root = tk.Tk()
    app = EquationView(root)
    root.mainloop()