"""Refactored Geometry View - Modular Architecture v2.0"""
import tkinter as tk
from tkinter import messagebox

# Import các component modules
from views.geometry.geometry_ui_manager import GeometryUIManager
from views.geometry.geometry_state_manager import GeometryStateManager
from views.geometry.geometry_operation_manager import GeometryOperationManager
from views.geometry.geometry_service_adapter import GeometryServiceAdapter
from views.geometry.geometry_excel_controller import GeometryExcelController
from views.geometry.geometry_result_display import GeometryResultDisplay
from views.geometry.geometry_memory_monitor import GeometryMemoryMonitor
from views.geometry.geometry_events import GeometryEvents
from views.geometry.input_panels.geometry_input_manager import GeometryInputManager

class GeometryView:
    """Main Geometry View v2.0 - Sử dụng các component modules"""
    
    def __init__(self, window, config=None):
        self.window = window
        self.window.title("Geometry Mode - Anti-Crash Excel! 💪")
        self.window.geometry("900x900")
        self.window.configure(bg="#F8F9FA")

        # Lưu config được truyền vào
        self.config = config or {}
        
        # Khởi tạo các biến trạng thái
        self._initialize_variables()
        
        # Khởi tạo các component managers
        self._initialize_components()
        
        # Thiết lập giao diện
        self._setup_ui()
        
        # Khởi tạo hệ thống
        self._initialize_system()
    
    def _initialize_variables(self):
        """Khởi tạo tất cả biến"""
        self.dropdown1_var = tk.StringVar(value="")
        self.dropdown2_var = tk.StringVar(value="")
        self.kich_thuoc_A_var = tk.StringVar(value="3")
        self.kich_thuoc_B_var = tk.StringVar(value="3")
        self.pheptoan_var = tk.StringVar(value="Khoảng cách")
        
        # Phiên bản mặc định
        self.phien_ban_list = self._get_available_versions()
        self.phien_ban_var = tk.StringVar(value=self.phien_ban_list[0])
        
        # Tham chiếu đến các widget chính
        self.entry_tong = None
        self.frame_buttons_manual = None
        self.frame_buttons_import = None
        self.geometry_service = None
    
    def _get_available_versions(self):
        """Lấy danh sách phiên bản từ config hoặc sử dụng mặc định"""
        try:
            if self.config and 'common' in self.config and 'versions' in self.config['common']:
                versions_data = self.config['common']['versions']
                if 'versions' in versions_data:
                    return [f"Phiên bản {v}" for v in versions_data['versions']]
        except Exception as e:
            print(f"Warning: Không thể load versions từ config: {e}")
        
        # Fallback nếu không có config
        return ["Phiên bản fx799", "Phiên bản fx880", "Phiên bản fx801"]
    
    def _initialize_components(self):
        """Khởi tạo các component managers"""
        # Service adapter (cần đầu tiên)
        self.service_adapter = GeometryServiceAdapter(self)
        self.service_adapter.initialize_service()
        
        # UI manager
        self.ui_manager = GeometryUIManager(self)
        
        # State manager
        self.state_manager = GeometryStateManager(self)
        
        # Operation manager
        self.operation_manager = GeometryOperationManager(self)
        
        # Input panels manager
        self.input_panels = GeometryInputManager(self)
        
        # Excel controller
        self.excel_controller = GeometryExcelController(self)
        
        # Result display
        self.result_display = GeometryResultDisplay(self)
        
        # Memory monitor
        self.memory_monitor = GeometryMemoryMonitor(self)
        
        # Events handler
        self.events = GeometryEvents(self)
    
    def _setup_ui(self):
        """Thiết lập giao diện chính"""
        # Sử dụng UI manager để tạo layout
        ui_components = self.ui_manager.setup_main_layout()
        
        # Tạo tất cả input frames
        self.input_panels.create_all_input_frames(ui_components['main_container'])
        
        # Tạo control frame và result display
        control_frame, entry_tong = self.ui_manager.create_control_frame()
        self.entry_tong = entry_tong
        
        # Setup result display
        self.result_display.setup_result_display(ui_components['main_container'], entry_tong)
        
        # Tạo các button frames
        button_components = self.ui_manager.create_button_frames(control_frame)
        self.frame_buttons_manual = button_components['frame_buttons_manual']
        self.frame_buttons_import = button_components['frame_buttons_import']
        
        # Tạo các nút thủ công
        self._create_manual_buttons()
        
        # Tạo các nút import
        self._create_import_buttons()
        
        # Bind import button
        button_components['btn_import_excel'].config(command=self.excel_controller.import_excel)
        
        # Setup memory monitor
        if hasattr(self.ui_manager, 'memory_status_label'):
            self.memory_monitor.setup_memory_monitor(self.ui_manager.memory_status_label)
        
        # Initially hide import buttons
        self.frame_buttons_import.grid_remove()
        self.frame_buttons_manual.grid_remove()
    
    def _create_manual_buttons(self):
        """Tạo các nút cho chế độ thủ công"""
        tk.Button(self.frame_buttons_manual, text="🔄 Xử lý Nhóm A",
                  command=self._process_group_A,
                  bg="#2196F3", fg="white", font=("Arial", 9)).grid(row=0, column=0, padx=5)
        
        tk.Button(self.frame_buttons_manual, text="🔄 Xử lý Nhóm B",
                  command=self._process_group_B,
                  bg="#2196F3", fg="white", font=("Arial", 9)).grid(row=0, column=1, padx=5)
        
        tk.Button(self.frame_buttons_manual, text="🚀 Thực thi tất cả",
                  command=self._process_all,
                  bg="#4CAF50", fg="white", font=("Arial", 9, "bold")).grid(row=0, column=2, padx=5)
        
        tk.Button(self.frame_buttons_manual, text="💾 Xuất Excel",
                  command=self._export_excel,
                  bg="#FF9800", fg="white", font=("Arial", 9, "bold")).grid(row=0, column=3, padx=5)
    
    def _create_import_buttons(self):
        """Tạo các nút cho chế độ import"""
        tk.Button(self.frame_buttons_import, text="🔥 Xử lý File Excel",
                  command=self.excel_controller.process_excel_batch,
                  bg="#F44336", fg="white", font=("Arial", 9, "bold")).grid(row=0, column=0, padx=5)
        
        tk.Button(self.frame_buttons_import, text="📁 Import File Khác",
                  command=self.excel_controller.import_excel,
                  bg="#2196F3", fg="white", font=("Arial", 9)).grid(row=0, column=1, padx=5)
        
        tk.Button(self.frame_buttons_import, text="📝 Tạo Template",
                  command=self.excel_controller.create_template,
                  bg="#9C27B0", fg="white", font=("Arial", 9)).grid(row=0, column=2, padx=5)
        
        tk.Button(self.frame_buttons_import, text="↩️ Quay lại",
                  command=self.excel_controller.quit_import_mode,
                  bg="#607D8B", fg="white", font=("Arial", 9)).grid(row=0, column=3, padx=5)
    
    def _initialize_system(self):
        """Khởi tạo hệ thống"""
        # Khởi tạo operations
        self.operation_manager.initialize_operations()
        
        # Setup events
        self.events.initialize_all_bindings()
        
        # Cập nhật state ban đầu cho service
        if self.service_adapter.is_service_ready():
            self.service_adapter.set_kich_thuoc(
                self.kich_thuoc_A_var.get(), 
                self.kich_thuoc_B_var.get()
            )
        
        # Đảm bảo hiển thị đúng ngay lần đầu
        self.operation_manager._on_operation_changed()
        
        # Hiển thông báo ban đầu
        self.result_display.show_ready_message()
    
    # ========== DATA EXTRACTION METHODS ==========
    def _get_input_data_A(self):
        """Lấy dữ liệu nhập cho nhóm A"""
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
        """Lấy dữ liệu nhập cho nhóm B"""
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
        """Xử lý nhóm A"""
        try:
            if not self.service_adapter.is_service_ready():
                messagebox.showerror("Lỗi", "GeometryService chưa được khởi tạo!")
                return
            
            data_A = self._get_input_data_A()
            result = self.service_adapter.thuc_thi_A(data_A)
            self.result_display.update_result_display(f"Nhóm A đã xử lý: {result}")
        except Exception as e:
            messagebox.showerror("Lỗi", f"Lỗi xử lý nhóm A: {str(e)}")
    
    def _process_group_B(self):
        """Xử lý nhóm B"""
        try:
            if not self.service_adapter.is_service_ready():
                messagebox.showerror("Lỗi", "GeometryService chưa được khởi tạo!")
                return
                
            data_B = self._get_input_data_B()
            result = self.service_adapter.thuc_thi_B(data_B)
            self.result_display.update_result_display(f"Nhóm B đã xử lý: {result}")
        except Exception as e:
            messagebox.showerror("Lỗi", f"Lỗi xử lý nhóm B: {str(e)}")
    
    def _process_all(self):
        """Thực thi tất cả - Core function!"""
        try:
            if not self.service_adapter.is_service_ready():
                messagebox.showerror("Lỗi", "GeometryService chưa được khởi tạo!")
                return
            
            # Kiểm tra xem đã chọn phép toán và hình dạng chưa
            if not self.pheptoan_var.get():
                messagebox.showwarning("Cảnh báo", "Vui lòng chọn phép toán!")
                return
            
            if not self.dropdown1_var.get():
                messagebox.showwarning("Cảnh báo", "Vui lòng chọn hình dạng cho nhóm A!")
                return
            
            # Lấy dữ liệu
            data_A = self._get_input_data_A()
            data_B = self._get_input_data_B()
            
            # Xử lý
            result_A, result_B = self.service_adapter.thuc_thi_tat_ca(data_A, data_B)
            
            # Sinh kết quả cuối cùng
            final_result = self.service_adapter.generate_final_result()
            
            # Hiển thị "chỉ 1 dòng" mã hóa với font Flexio Fx799VN (nếu có)
            self.result_display.show_single_line_result(final_result)
            
            # Cập nhật trạng thái có kết quả
            self.state_manager.set_has_result(True)
            
        except Exception as e:
            messagebox.showerror("Lỗi", f"Lỗi thực thi: {str(e)}")
    
    def _export_excel(self):
        """Xuất kết quả ra Excel"""
        try:
            if not self.service_adapter.is_service_ready():
                messagebox.showerror("Lỗi", "GeometryService chưa sẵn sàng!")
                return
            
            final_result = self.service_adapter.generate_final_result()
            if not final_result:
                messagebox.showwarning("Cảnh báo", "Chưa có kết quả nào để xuất!\n\nVui lòng thực thi tính toán trước.")
                return
            
            from tkinter import filedialog
            from datetime import datetime
            
            default_name = f"geometry_export_{datetime.now().strftime('%Y%m%d_%H%M%S')}.xlsx"
            
            output_path = filedialog.asksaveasfilename(
                title="Xuất kết quả ra Excel",
                defaultextension=".xlsx",
                filetypes=[("Excel files", "*.xlsx")],
                initialfile=default_name
            )
            
            if not output_path:
                return
            
            exported_file = self.service_adapter.export_single_result(output_path)
            messagebox.showinfo("Xuất thành công", f"Kết quả đã lưu tại:\n{exported_file}")
            
        except Exception as e:
            messagebox.showerror("Lỗi Xuất", f"Lỗi xuất Excel: {str(e)}")
    
    # ========== PUBLIC API METHODS (for backward compatibility) ==========
    def get_current_state(self):
        """Lấy trạng thái hiện tại"""
        return {
            'is_import_mode': self.state_manager.is_import_mode(),
            'is_manual_mode': self.state_manager.is_manual_mode(),
            'has_result': self.state_manager.has_result,
            'operation': self.operation_manager.get_current_operation(),
            'shapes': (self.dropdown1_var.get(), self.dropdown2_var.get()),
            'dimensions': (self.kich_thuoc_A_var.get(), self.kich_thuoc_B_var.get())
        }
    
    def reset_view(self):
        """Reset toàn bộ view về trạng thái ban đầu"""
        self.state_manager.reset_state()
        self.result_display.clear_display()
        self.result_display.show_ready_message()


if __name__ == "__main__":
    root = tk.Tk()
    app = GeometryView(root)
    root.mainloop()