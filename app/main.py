"""Application entry point cho ConvertKeylogApp - giống TL main.py."""

from gui.windows.main_window_tl_style import MainWindow


def main():
    """Main entry point cho application - giống TL."""
    try:
        app = MainWindow()
        app.run()
    except Exception as e:
        print(f"Lỗi khởi động ứng dụng: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()
