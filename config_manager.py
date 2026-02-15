import yaml
from pathlib import Path

THEMES = {
    "blue": {
        "background_start": "#0a0e27",
        "background_end":   "#16213e",
        "accent":           "#00d9ff",
        "accent_bright":    "#00ffff",
        "accent_dim":       "#0099cc",
        "accent_dark":      "#1a5f7a",
        "accent_darker":    "#0d2b3e",
        "delete_color":     "#ff3366",
        "generate_color":   "#00ff88",
        "text":             "#00d9ff",
    },
    "pink": {
        "background_start": "#1a0a1a",
        "background_end":   "#2d0d2d",
        "accent":           "#ff00cc",
        "accent_bright":    "#ff66dd",
        "accent_dim":       "#cc0099",
        "accent_dark":      "#7a1a6e",
        "accent_darker":    "#3e0d38",
        "delete_color":     "#ff3333",
        "generate_color":   "#ff66aa",
        "text":             "#ff00cc",
    },
    "green": {
        "background_start": "#0a1a0a",
        "background_end":   "#0d2b0d",
        "accent":           "#00ff88",
        "accent_bright":    "#66ffaa",
        "accent_dim":       "#00cc66",
        "accent_dark":      "#1a6e3a",
        "accent_darker":    "#0d3e1e",
        "delete_color":     "#ff3333",
        "generate_color":   "#00ffcc",
        "text":             "#00ff88",
    },
    "purple": {
        "background_start": "#0e0a1a",
        "background_end":   "#1a0d2d",
        "accent":           "#bf00ff",
        "accent_bright":    "#dd66ff",
        "accent_dim":       "#9900cc",
        "accent_dark":      "#5c1a7a",
        "accent_darker":    "#2e0d3e",
        "delete_color":     "#ff3333",
        "generate_color":   "#7700ff",
        "text":             "#bf00ff",
    },
}

class ConfigManager:
    def __init__(self):
        self.config_file = Path("config.yml")
        self.config = self._load()

    def _load(self) -> dict:
        if self.config_file.exists():
            with open(self.config_file, 'r') as f:
                return yaml.safe_load(f)
        # Fallback defaults if config.yml is missing
        return {
            "theme": {"name": "blue"},
            "app": {
                "title": "SECURE VAULT SYSTEM",
                "width": 1000,
                "height": 650,
                "font": "Consolas",
                "min_master_password_length": 8,
                "clipboard_clear_seconds": 30,
            }
        }

    def get_colors(self) -> dict:
        """Return color dict for current theme"""
        theme_name = self.config.get("theme", {}).get("name", "blue")
        return THEMES.get(theme_name, THEMES["blue"])

    def get_app(self) -> dict:
        return self.config.get("app", {})

    def get_stylesheet(self, extra: str = "") -> str:
        """Build full QSS stylesheet from current theme colors"""
        c = self.get_colors()
        font = self.get_app().get("font", "Consolas")
        return f"""
            QDialog, QMainWindow {{
                background: qlineargradient(x1:0, y1:0, x2:1, y2:1,
                    stop:0 {c['background_start']}, stop:1 {c['background_end']});
            }}
            QWidget {{
                background-color: transparent;
                color: {c['text']};
                font-family: '{font}', 'Courier New', monospace;
            }}
            QLabel {{
                color: {c['accent']};
                font-size: 13px;
            }}
            QLineEdit, QTextEdit {{
                padding: 10px;
                border: 2px solid {c['accent_dark']};
                border-radius: 6px;
                background-color: rgba(10, 25, 47, 0.8);
                color: {c['accent']};
                font-size: 12px;
            }}
            QLineEdit:focus, QTextEdit:focus {{
                border: 2px solid {c['accent']};
                background-color: rgba(0, 217, 255, 0.05);
            }}
            QLineEdit:read-only, QTextEdit:read-only {{
                background-color: rgba(10, 25, 47, 0.5);
                border: 2px solid {c['accent_darker']};
            }}
            QListWidget {{
                background-color: rgba(10, 25, 47, 0.7);
                border: 2px solid {c['accent_dark']};
                border-radius: 8px;
                padding: 8px;
                font-size: 13px;
            }}
            QListWidget::item {{
                padding: 12px;
                border-radius: 5px;
                border-left: 3px solid transparent;
            }}
            QListWidget::item:selected {{
                background: rgba(0, 217, 255, 0.2);
                border-left: 3px solid {c['accent']};
                color: {c['accent_bright']};
            }}
            QListWidget::item:hover {{
                background-color: rgba(0, 217, 255, 0.1);
                border-left: 3px solid {c['accent_dim']};
            }}
            QPushButton {{
                padding: 10px 20px;
                border: 2px solid {c['accent']};
                border-radius: 8px;
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                    stop:0 {c['accent_dark']}, stop:1 {c['accent_darker']});
                color: {c['accent']};
                font-size: 13px;
                font-weight: bold;
            }}
            QPushButton:hover {{
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                    stop:0 {c['accent']}, stop:1 {c['accent_dark']});
                color: {c['background_start']};
            }}
            QPushButton:pressed {{
                background-color: {c['accent_darker']};
            }}
            QPushButton#deleteBtn {{
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                    stop:0 {c['delete_color']}, stop:1 #aa0033);
                border: 2px solid {c['delete_color']};
                color: white;
            }}
            QPushButton#deleteBtn:hover {{
                background: {c['delete_color']};
                color: {c['background_start']};
            }}
            QPushButton#generateBtn {{
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                    stop:0 {c['generate_color']}, stop:1 #00aa55);
                border: 2px solid {c['generate_color']};
                color: {c['background_start']};
            }}
            QPushButton#generateBtn:hover {{
                background: {c['generate_color']};
            }}
            QStatusBar {{
                background-color: rgba(0, 217, 255, 0.1);
                color: {c['accent']};
                border-top: 1px solid {c['accent_dark']};
            }}
            QMessageBox {{
                background-color: {c['background_start']};
                color: {c['accent']};
            }}
            {extra}
        """