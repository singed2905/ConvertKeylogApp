import tkinter as tk
from tkinter import ttk, messagebox, filedialog
import json
import os
from typing import Dict, Any
from utils.config_loader import config_loader

class MainView:
    """Main application window with enhanced mode selector"""
    
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("ConvertKeylogApp v2.2 - Keylog Generator Suite")
        self.root.geometry("800x600")
        self.root.resizable(True, True)
        
        # Load modes configuration
        self.modes_config = self.load_modes_config()
        
        # Active windows tracking
        self.active_windows = {}
        
        self.setup_ui()
        self.setup_styles()
        
    def load_modes_config(self) -> Dict[str, Any]:
        """Load modes configuration from JSON file"""
        try:
            config_path = "config/modes.json"
            if os.path.exists(config_path):
                with open(config_path, 'r', encoding='utf-8') as f:
                    return json.load(f)
            else:
                print(f"Warning: {config_path} not found, using legacy config")
                return self.get_legacy_modes_config()
        except Exception as e:
            print(f"Error loading modes config: {e}")
            return self.get_legacy_modes_config()
    
    def get_legacy_modes_config(self) -> Dict[str, Any]:
        """Legacy modes configuration for backward compatibility"""
        try:
            # Try to use existing config_loader
            legacy_modes = config_loader.get_available_modes()
            modes_dict = {}
            
            for mode in legacy_modes:
                mode_key = mode.lower().replace(" ", "_").replace("equation", "equation")
                modes_dict[mode_key] = {
                    "name": mode,
                    "version": "2.2" if "Equation" in mode else "2.1",
                    "description": f"Chế độ {mode}",
                    "icon": self.get_mode_icon(mode),
                    "status": "production",
                    "enabled": True
                }
            
            return {
                "modes": modes_dict,
                "display_order": list(modes_dict.keys())
            }
        except:
            # Ultimate fallback
            return {
                "modes": {
                    "equation": {
                        "name": "Equation Mode",
                        "version": "2.2",
                        "description": "Giải hệ phương trình tuyến tính",
                        "icon": "🧠",
                        "status": "production",
                        "enabled": True
                    },
                    "polynomial": {
                        "name": "Polynomial Mode", 
                        "version": "2.1",
                        "description": "Giải phương trình đa thức",
                        "icon": "📈",
                        "status": "production",
                        "enabled": True
                    },
                    "geometry": {
                        "name": "Geometry Mode",
                        "version": "2.1",
                        "description": "Xử lý bài toán hình học",
                        "icon": "📐", 
                        "status": "production",
                        "enabled": True
                    },
                    "vector": {
                        "name": "Vector Mode",
                        "version": "1.0",
                        "description": "Tính toán vector 2D/3D",
                        "icon": "🔢",
                        "status": "beta",
                        "enabled": True
                    }
                },
                "display_order": ["equation", "polynomial", "geometry", "vector"]
            }
    
    def get_mode_icon(self, mode_name: str) -> str:
        """Get icon for mode based on name"""
        icons = {
            "Equation Mode": "🧠",
            "Polynomial Equation Mode": "📈", 
            "Geometry Mode": "📐",
            "Vector Mode": "🔢"
        }
        return icons.get(mode_name, "📊")
    
    def setup_styles(self):
        """Setup custom styles for UI components"""
        style = ttk.Style()
        
        # Configure theme
        try:
            style.theme_use('clam')
        except:
            pass
        
        # Mode button styles
        style.configure("ModeButton.TButton", 
                       padding=(20, 15),
                       font=("Arial", 11, "bold"))
        
        style.configure("ProductionMode.TButton",
                       foreground="#2E7D32")
        
        style.configure("BetaMode.TButton", 
                       foreground="#F57C00")
        
        style.configure("ExperimentalMode.TButton",
                       foreground="#D32F2F")
    
    def setup_ui(self):
        """Setup main user interface"""
        # Main container with modern styling
        main_frame = ttk.Frame(self.root, padding="20")
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        # Header
        self.create_header(main_frame)
        
        # Mode selector
        self.create_mode_selector(main_frame)
        
        # Footer with info
        self.create_footer(main_frame)
        
        # Status bar
        self.create_status_bar()
    
    def create_header(self, parent):
        """Create application header"""
        header_frame = ttk.Frame(parent)
        header_frame.pack(fill=tk.X, pady=(0, 30))
        
        # Main title
        title_label = ttk.Label(header_frame, 
                               text="ConvertKeylogApp v2.2",
                               font=("Arial", 24, "bold"))
        title_label.pack()
        
        # Subtitle
        subtitle_label = ttk.Label(header_frame,
                                  text="Keylog Generator Suite for Casio Calculators",
                                  font=("Arial", 12))
        subtitle_label.pack(pady=(5, 0))
        
        # Description
        desc_label = ttk.Label(header_frame,
                              text="Chuyển đổi biểu thức toán học thành mã keylog tương thích máy tính Casio",
                              font=("Arial", 10),
                              foreground="gray")
        desc_label.pack(pady=(10, 0))
    
    def create_mode_selector(self, parent):
        """Create enhanced mode selection interface"""
        selector_frame = ttk.LabelFrame(parent, text="Chọn chế độ tính toán", padding="20")
        selector_frame.pack(fill=tk.BOTH, expand=True, pady=(0, 20))
        
        # Get enabled modes in display order
        modes = self.modes_config.get("modes", {})
        display_order = self.modes_config.get("display_order", list(modes.keys()))
        
        # Create mode buttons grid (2 columns)
        row = 0
        col = 0
        max_cols = 2
        
        for mode_key in display_order:
            if mode_key not in modes or not modes[mode_key].get("enabled", True):
                continue
                
            mode_info = modes[mode_key]
            self.create_mode_button(selector_frame, mode_key, mode_info, row, col)
            
            col += 1
            if col >= max_cols:
                col = 0
                row += 1
    
    def create_mode_button(self, parent, mode_key: str, mode_info: Dict[str, Any], row: int, col: int):
        """Create individual mode button with enhanced info display"""
        # Mode container
        mode_frame = ttk.Frame(parent)
        mode_frame.grid(row=row, column=col, padx=15, pady=15, sticky="nsew")
        
        # Configure grid weights
        parent.columnconfigure(col, weight=1)
        parent.rowconfigure(row, weight=1)
        
        # Mode button with icon and name
        button_style = self.get_button_style(mode_info.get("status", "production"))
        
        mode_button = ttk.Button(mode_frame,
                                text=f"{mode_info.get('icon', '📊')} {mode_info.get('name', mode_key)}",
                                style=f"{button_style}.TButton",
                                command=lambda: self.open_mode(mode_key))
        mode_button.pack(fill=tk.X, pady=(0, 10))
        
        # Version and status with color coding
        status = mode_info.get('status', 'production')
        version_text = f"v{mode_info.get('version', '1.0')}"
        status_colors = {
            'production': '#2E7D32',
            'beta': '#F57C00', 
            'experimental': '#D32F2F'
        }
        
        status_frame = ttk.Frame(mode_frame)
        status_frame.pack(fill=tk.X, pady=(0, 5))
        
        version_label = ttk.Label(status_frame, text=version_text, font=("Arial", 9))
        version_label.pack(side=tk.LEFT)
        
        status_label = ttk.Label(status_frame, text=f"({status})", 
                                font=("Arial", 8),
                                foreground=status_colors.get(status, '#666666'))
        status_label.pack(side=tk.RIGHT)
        
        # Description
        desc_label = ttk.Label(mode_frame, 
                              text=mode_info.get('description', 'No description'),
                              font=("Arial", 9),
                              wraplength=350,
                              justify=tk.CENTER,
                              foreground="#444444")
        desc_label.pack(pady=(0, 10))
        
        # Key features (first 3)
        features = mode_info.get('features', [])
        if features:
            features_text = "• " + "\n• ".join(features[:3])
            if len(features) > 3:
                features_text += f"\n... và {len(features) - 3} tính năng khác"
                
            features_label = ttk.Label(mode_frame,
                                      text=features_text,
                                      font=("Arial", 8),
                                      foreground="#666666",
                                      wraplength=350,
                                      justify=tk.LEFT)
            features_label.pack()
    
    def get_button_style(self, status: str) -> str:
        """Get button style based on mode status"""
        status_styles = {
            "production": "ProductionMode",
            "beta": "BetaMode", 
            "experimental": "ExperimentalMode"
        }
        return status_styles.get(status, "ModeButton")
    
    def create_footer(self, parent):
        """Create application footer"""
        footer_frame = ttk.Frame(parent)
        footer_frame.pack(fill=tk.X, pady=(20, 0))
        
        # System requirements
        system_info = ttk.Label(footer_frame,
                               text="Hỗ trợ: Windows 10+, macOS 10.14+, Ubuntu 18.04+ | Python 3.9+",
                               font=("Arial", 8),
                               foreground="gray")
        system_info.pack(side=tk.LEFT)
        
        # Version and copyright
        version_info = ttk.Label(footer_frame,
                                text="ConvertKeylogApp v2.2 | © 2025",
                                font=("Arial", 8),
                                foreground="gray")
        version_info.pack(side=tk.RIGHT)
    
    def create_status_bar(self):
        """Create status bar"""
        self.status_bar = ttk.Label(self.root, text="Sẵn sàng", relief=tk.SUNKEN, padding="5")
        self.status_bar.pack(side=tk.BOTTOM, fill=tk.X)
    
    def open_mode(self, mode_key: str):
        """Open specific calculation mode with error handling"""
        try:
            # Prevent multiple instances of same mode
            if mode_key in self.active_windows:
                try:
                    # Bring existing window to front
                    self.active_windows[mode_key].root.lift()
                    self.active_windows[mode_key].root.focus_force()
                    self.update_status(f"Đã chuyển đến {mode_key} mode")
                    return
                except tk.TclError:
                    # Window was closed, remove from tracking
                    del self.active_windows[mode_key]
            
            # Import and create view based on mode
            if mode_key == "equation":
                from views.equation_view import EquationView
                # Try to load config, fallback to None
                try:
                    config = config_loader.get_mode_config("Equation Mode")
                    window = EquationView(self.root, config=config)
                except:
                    window = EquationView(self.root)
                
            elif mode_key == "polynomial":
                from views.polynomial_equation_view import PolynomialEquationView
                try:
                    config = config_loader.get_mode_config("Polynomial Equation Mode")
                    window = PolynomialEquationView(self.root, config=config)
                except:
                    window = PolynomialEquationView(self.root)
                
            elif mode_key == "geometry":
                from views.geometry_view import GeometryView
                try:
                    config = config_loader.get_mode_config("Geometry Mode")
                    window = GeometryView(self.root, config=config)
                except:
                    window = GeometryView(self.root)
                
            elif mode_key == "vector":
                from views.vector_view import VectorView
                window = VectorView(self.root)
                
            else:
                # Handle legacy mode names
                self.open_legacy_mode(mode_key)
                return
            
            # Track active window
            self.active_windows[mode_key] = window
            
            # Setup window close callback
            window.root.protocol("WM_DELETE_WINDOW", 
                               lambda: self.on_mode_window_close(mode_key))
            
            self.update_status(f"Đã mở {mode_key} mode")
            
        except ImportError as e:
            messagebox.showerror("Lỗi Import", 
                               f"Không thể import {mode_key} mode:\n{str(e)}\n\nVui lòng kiểm tra file views/{mode_key}_view.py")
            self.update_status(f"Lỗi mở {mode_key} mode")
            
        except Exception as e:
            messagebox.showerror("Lỗi", f"Lỗi mở {mode_key} mode: {str(e)}")
            self.update_status(f"Lỗi mở {mode_key} mode")
    
    def open_legacy_mode(self, mode_name: str):
        """Handle opening legacy mode names for backward compatibility"""
        legacy_mappings = {
            "Equation Mode": "equation",
            "Polynomial Equation Mode": "polynomial", 
            "Geometry Mode": "geometry"
        }
        
        if mode_name in legacy_mappings:
            self.open_mode(legacy_mappings[mode_name])
        else:
            messagebox.showerror("Lỗi", f"Mode '{mode_name}' chưa được implement")
    
    def on_mode_window_close(self, mode_key: str):
        """Handle mode window closing"""
        try:
            if mode_key in self.active_windows:
                self.active_windows[mode_key].root.destroy()
                del self.active_windows[mode_key]
                self.update_status(f"Đã đóng {mode_key} mode")
        except Exception as e:
            print(f"Error closing {mode_key} window: {e}")
    
    def update_status(self, message: str):
        """Update status bar message with auto-clear"""
        self.status_bar.config(text=message)
        # Auto-clear status after 3 seconds
        self.root.after(3000, lambda: self.status_bar.config(text="Sẵn sàng"))
    
    def run(self):
        """Run the main application"""
        try:
            # Center window on screen
            self.center_window()
            
            # Set icon if available
            self.set_window_icon()
            
            # Setup close handler
            self.root.protocol("WM_DELETE_WINDOW", self.on_closing)
            
            # Show startup message
            self.update_status("ConvertKeylogApp v2.2 khởi động thành công!")
            
            # Start main loop
            self.root.mainloop()
            
        except Exception as e:
            messagebox.showerror("Lỗi khởi động", f"Lỗi khởi động ứng dụng: {str(e)}")
    
    def center_window(self):
        """Center window on screen"""
        self.root.update_idletasks()
        width = self.root.winfo_width()
        height = self.root.winfo_height()
        x = (self.root.winfo_screenwidth() // 2) - (width // 2)
        y = (self.root.winfo_screenheight() // 2) - (height // 2)
        self.root.geometry(f"{width}x{height}+{x}+{y}")
    
    def set_window_icon(self):
        """Set window icon if available"""
        try:
            # Try to set icon from file
            icon_paths = ["assets/icon.ico", "icon.ico", "app.ico"]
            for icon_path in icon_paths:
                if os.path.exists(icon_path):
                    self.root.iconbitmap(icon_path)
                    break
        except Exception:
            pass  # Ignore icon errors
    
    def on_closing(self):
        """Handle application closing with cleanup"""
        try:
            # Close all active mode windows
            for mode_key, window in list(self.active_windows.items()):
                try:
                    window.root.destroy()
                except:
                    pass
            
            # Close main window
            self.root.destroy()
            
        except Exception as e:
            print(f"Error during closing: {e}")
            self.root.destroy()


# ========== BACKWARD COMPATIBILITY METHODS ==========
    def _load_modes(self):
        """Legacy method for backward compatibility"""
        try:
            modes_data = config_loader.get_available_modes()
            # Add Vector Mode to legacy list
            if "Vector Mode" not in modes_data:
                modes_data.append("Vector Mode")
            return modes_data
        except Exception as e:
            return ["Equation Mode", "Polynomial Equation Mode", "Geometry Mode", "Vector Mode"]
    
    def _open_selected_mode(self):
        """Legacy method - redirect to new implementation"""
        selected = getattr(self, 'mode_var', tk.StringVar()).get()
        
        if selected == "Geometry Mode":
            self.open_mode("geometry")
        elif selected == "Equation Mode":
            self.open_mode("equation")
        elif selected == "Polynomial Equation Mode":
            self.open_mode("polynomial")
        elif selected == "Vector Mode":
            self.open_mode("vector")
        else:
            messagebox.showwarning("Cảnh báo", "Vui lòng chọn một chế độ hợp lệ.")
    
    # Legacy individual mode openers - redirect to new system
    def _open_geometry_mode(self):
        self.open_mode("geometry")
    
    def _open_equation_mode(self):
        self.open_mode("equation")
    
    def _open_polynomial_mode(self):
        self.open_mode("polynomial")


# ========== APPLICATION ENTRY POINT ==========
if __name__ == "__main__":
    try:
        app = MainView()
        app.run()
    except Exception as e:
        print(f"Critical error: {e}")
        import traceback
        traceback.print_exc()