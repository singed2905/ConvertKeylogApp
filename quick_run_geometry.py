from services.geometry import GeometryService
from utils.config_loader import config_loader

# Quick smoke test to ensure service imports and basic call works
if __name__ == "__main__":
    config = config_loader.get_mode_config("Geometry Mode")
    service = GeometryService(config)
    service.set_current_operation("Khoảng cách")
    service.set_current_shapes("Điểm", "Điểm")
    service.set_kich_thuoc("2", "2")
    a = {"point_input": "1,2"}
    b = {"point_input": "3,4"}
    service.thuc_thi_tat_ca(a, b)
    print(service.generate_final_result())
