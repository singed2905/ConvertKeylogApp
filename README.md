# ConvertKeylogApp

Giao diện được chuyển từ dự án TL, chỉ giữ phần UI (không kèm logic). Cấu trúc thư mục gọn gàng hơn.

## Cấu trúc
- main.py: entry point
- views/: giao diện Tkinter
  - main_view.py: màn hình chọn chế độ
  - keylog_converter_view.py: giao diện chuyển đổi keylog (UI only)
- config/modes.json: danh sách chế độ
- utils/file_utils.py: tiện ích đọc file cấu hình

## Chạy thử
```bash
python main.py
```
