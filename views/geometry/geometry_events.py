"""Geometry View Components - Events Handler"""

class GeometryEvents:
    """Quản lý các events và bindings"""
    
    def __init__(self, parent_view):
        self.parent = parent_view
    
    def setup_input_bindings(self):
        """Thiết lập bindings cho input change detection"""
        entries = self._get_all_input_entries()
        for entry in entries:
            if hasattr(entry, 'bind'):
                entry.bind('<KeyRelease>', self._on_input_data_changed)
    
    def setup_variable_bindings(self):
        """Thiết lập bindings cho các biến"""
        # Bind các thay đổi để cập nhật service
        self.parent.dropdown1_var.trace('w', self._on_shape_changed)
        self.parent.dropdown2_var.trace('w', self._on_shape_changed)
        self.parent.kich_thuoc_A_var.trace('w', self._on_dimension_changed)
        self.parent.kich_thuoc_B_var.trace('w', self._on_dimension_changed)
    
    def _get_all_input_entries(self):
        """Lấy tất cả input entry widgets"""
        entries = []
        
        # Thu thập tất cả entry widgets
        for attr_name in dir(self.parent):
            if attr_name.startswith('entry_') and hasattr(self.parent, attr_name):
                entry = getattr(self.parent, attr_name)
                if hasattr(entry, 'get'):  # Đó là Entry widget
                    entries.append(entry)
        
        return entries
    
    def _on_input_data_changed(self, event):
        """Xử lý khi dữ liệu nhập thay đổi"""
        if hasattr(self.parent, 'state_manager'):
            self.parent.state_manager.on_input_data_changed(event)
    
    def _on_shape_changed(self, *args):
        """Xử lý khi thay đổi hình dạng"""
        if hasattr(self.parent, 'service_adapter'):
            self.parent.service_adapter.set_current_shapes(
                self.parent.dropdown1_var.get(), 
                self.parent.dropdown2_var.get()
            )
        
        if hasattr(self.parent, 'input_panels'):
            self.parent.input_panels.update_input_frames()
    
    def _on_dimension_changed(self, *args):
        """Xử lý khi thay đổi kích thước"""
        if hasattr(self.parent, 'service_adapter'):
            self.parent.service_adapter.set_kich_thuoc(
                self.parent.kich_thuoc_A_var.get(), 
                self.parent.kich_thuoc_B_var.get()
            )
    
    def initialize_all_bindings(self):
        """Khởi tạo tất cả bindings"""
        # Đợi 1 giây để UI được tạo xong
        self.parent.window.after(1000, self._delayed_setup)
    
    def _delayed_setup(self):
        """Thiết lập muộn sau khi UI hoàn thành"""
        self.setup_input_bindings()
        self.setup_variable_bindings()