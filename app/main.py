"""Application entry point for ConvertKeylogApp."""

from gui.windows.main_window import MainWindow


def main():
    """Main entry point for the application."""
    app = MainWindow()
    app.run()


if __name__ == "__main__":
    main()
