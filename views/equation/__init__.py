"""Equation Components Package - Init file"""

# Import các component chính
from .equation_input_handler import EquationInputHandler
from .equation_result_handler import EquationResultHandler
from .equation_ui_manager import EquationUIManager
from .equation_button_manager import EquationButtonManager
from .equation_config_manager import EquationConfigManager

__all__ = [
    'EquationInputHandler',
    'EquationResultHandler', 
    'EquationUIManager',
    'EquationButtonManager',
    'EquationConfigManager'
]

# Package metadata
__version__ = '2.0.0'
__author__ = 'ConvertKeylogApp Team'
__description__ = 'Modular components for Equation View - Refactored from monolithic design'

# Component descriptions
COMPONENT_INFO = {
    'EquationInputHandler': 'Xử lý các ô nhập liệu hệ số phương trình',
    'EquationResultHandler': 'Quản lý hiển thị kết quả mã hóa và nghiệm',
    'EquationUIManager': 'Quản lý layout và giao diện tổng thể',
    'EquationButtonManager': 'Xử lý các nút chức năng và event',
    'EquationConfigManager': 'Quản lý cấu hình và fallback settings'
}