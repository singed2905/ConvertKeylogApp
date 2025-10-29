"""Geometry Components Package - Init file"""

# Import các component chính
from .geometry_ui_manager import GeometryUIManager
from .geometry_state_manager import GeometryStateManager
from .geometry_operation_manager import GeometryOperationManager
from .geometry_service_adapter import GeometryServiceAdapter
from .geometry_excel_controller import GeometryExcelController
from .geometry_result_display import GeometryResultDisplay
from .geometry_memory_monitor import GeometryMemoryMonitor
from .geometry_events import GeometryEvents

__all__ = [
    'GeometryUIManager',
    'GeometryStateManager',
    'GeometryOperationManager', 
    'GeometryServiceAdapter',
    'GeometryExcelController',
    'GeometryResultDisplay',
    'GeometryMemoryMonitor',
    'GeometryEvents'
]

# Package metadata
__version__ = '2.0.0'
__author__ = 'ConvertKeylogApp Team'
__description__ = 'Modular components for Geometry View - Refactored from 1300+ line monolithic design'

# Component descriptions
COMPONENT_INFO = {
    'GeometryUIManager': 'Quản lý layout và giao diện tổng thể',
    'GeometryStateManager': 'Quản lý trạng thái import/manual, has_result',
    'GeometryOperationManager': 'Cập nhật dropdown theo phép toán, ẩn/hiện B',
    'GeometryServiceAdapter': 'Bọc GeometryService và các method chính',
    'GeometryExcelController': 'Import/process/template/quit Excel operations',
    'GeometryResultDisplay': 'Hiển thị kết quả 1 dòng + log, copy clipboard',
    'GeometryMemoryMonitor': 'Theo dõi memory và update màu sắc',
    'GeometryEvents': 'Bind input events và debounce'
}