"""Geometry View Components - Memory Monitor"""
import psutil

class GeometryMemoryMonitor:
    """Theo dõi memory và update màu sắc"""
    
    def __init__(self, parent_view):
        self.parent = parent_view
        self.memory_label = None
    
    def setup_memory_monitor(self, memory_label):
        """Thiết lập memory monitor"""
        self.memory_label = memory_label
        self._start_memory_monitoring()
    
    def _get_memory_usage(self) -> float:
        """Lấy memory usage hiện tại tính bằng MB"""
        try:
            process = psutil.Process()
            return process.memory_info().rss / 1024 / 1024
        except:
            return 0.0
    
    def _start_memory_monitoring(self):
        """Bắt đầu theo dõi memory định kỳ"""
        def update_memory():
            try:
                memory_mb = self._get_memory_usage()
                
                # Màu sắc theo usage
                if memory_mb > 800:
                    color = "#F44336"  # Red
                    status = "🔥 High"
                elif memory_mb > 500:
                    color = "#FF9800"  # Orange
                    status = "⚠️ Medium"
                else:
                    color = "#4CAF50"  # Green
                    status = "✅ OK"
                
                if self.memory_label:
                    self.memory_label.config(
                        text=f"💾 Memory: {memory_mb:.1f}MB ({status})",
                        fg=color
                    )
                
            except Exception:
                pass
            
            # Lập lịch cập nhật tiếp theo
            if hasattr(self.parent, 'window'):
                self.parent.window.after(5000, update_memory)  # Cập nhật mỗi 5 giây
        
        update_memory()
    
    def get_current_memory(self):
        """Lấy memory hiện tại"""
        return self._get_memory_usage()