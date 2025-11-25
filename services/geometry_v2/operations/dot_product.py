"""
Dot Product Calculator - Tích vô hướng

Tính tích vô hướng của 2 vecto.
"""


class DotProductCalculator:
    """
    Calculator cho phép tính tích vô hướng.
    """
    
    @staticmethod
    def calculate(vector_a, vector_b) -> float:
        """
        Tính tích vô hướng của 2 vecto.
        
        Args:
            vector_a: Vecto thứ nhất
            vector_b: Vecto thứ hai
            
        Returns:
            Tích vô hướng
        """
        return vector_a.dot(vector_b)
    
    @staticmethod
    def cross_product(vector_a, vector_b):
        """
        Tính tích có hướng (3D).
        
        Args:
            vector_a: Vecto thứ nhất
            vector_b: Vecto thứ hai
            
        Returns:
            Vecto kết quả
        """
        return vector_a.cross(vector_b)
