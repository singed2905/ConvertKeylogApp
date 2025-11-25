"""
Unit Vector Calculator - Vecto đơn vị

Chuẩn hóa vecto thành vecto đơn vị.
"""


class UnitVectorCalculator:
    """
    Calculator cho phép chuẩn hóa vecto.
    """
    
    @staticmethod
    def calculate(vector):
        """
        Chuẩn hóa vecto thành vecto đơn vị.
        
        Args:
            vector: Vecto cần chuẩn hóa
            
        Returns:
            Vecto đơn vị
        """
        return vector.normalize()
    
    @staticmethod
    def get_magnitude(vector) -> float:
        """
        Lấy độ dài vecto.
        
        Args:
            vector: Vecto
            
        Returns:
            Độ dài
        """
        return vector.magnitude()
