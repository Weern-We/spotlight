import sys
import os
import subprocess
import webbrowser
import re
import json
from PyQt6.QtWidgets import (QApplication, QWidget, QVBoxLayout, QHBoxLayout, QLineEdit, QListWidget, QListWidgetItem,QPushButton, QGraphicsDropShadowEffect)
from PyQt6.QtCore import Qt, QSize, QPropertyAnimation, QRect, QEasingCurve
from PyQt6.QtGui import QFont, QKeySequence, QShortcut, QIcon, QColor

os.environ["QT_LOGGING_RULES"] = "qt.svg.warning=false"


ICON_PASTE_PATH = "your_path_to_spotlight.py"
ICON_SCREENSHOT_PATH = "your_path_to_spotlight.py"
ICON_TERMINAL_PATH = "your_path_to_spotliht.py"

ICON_PASTE_PATH = "your_path"
ICON_SCREENSHOT_PATH = "your_path"
ICON_TERMINAL_PATH = "your_path"



class SpotlightClone(QWidget):
    def __init__(self):
        super().__init__()
        self.pinned_file = os.path.expanduser("~/.spotlight_pinned.json")
        self.pinned_apps = self.load_pinned()
        self.apps = self.load_apps()
        self.current_target_height = 80
        self.initUI()
        self.update_results("")

    def load_pinned(self):
        if os.path.exists(self.pinned_file):
            try:
                with open(self.pinned_file, 'r', encoding='utf-8') as f:
                    return json.load(f)
            except Exception:
                return []
        return []

    def save_pinned(self):
        try:
            with open(self.pinned_file, 'w', encoding='utf-8') as f:
                json.dump(self.pinned_apps, f, ensure_ascii=False, indent=4)
        except Exception as e:
            print(f"Error: {e}")

    def initUI(self):
        self.setWindowFlags(Qt.WindowType.FramelessWindowHint | Qt.WindowType.WindowStaysOnTopHint | Qt.WindowType.Tool)
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)

        self.resize(800, self.current_target_height)
        self.center_on_screen()

        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(15, 15, 15, 15)
        main_layout.setAlignment(Qt.AlignmentFlag.AlignTop)
        main_layout.setSpacing(0)

        top_panel = QWidget()
        top_layout = QHBoxLayout(top_panel)
        top_layout.setContentsMargins(0, 0, 0, 0)
        top_layout.setSpacing(12)

        element_style = """
            background-color: rgba(225, 230, 253, 0.85); 
            color: #1a1a1a;
            border-radius: 25px;
        """

        self.input_field = QLineEdit()
        self.input_field.setPlaceholderText("Spotlight Search")
        self.input_field.setFont(QFont("Cantarell", 18))
        self.input_field.setFixedHeight(50)
        self.input_field.setStyleSheet(f"""
            QLineEdit {{
                {element_style}
                padding-left: 20px;
                border: 1px solid rgba(255, 255, 255, 0.4);
            }}
            QLineEdit:focus {{
                background-color: rgba(240, 244, 255, 0.95);
                border: 1px solid rgba(0, 122, 255, 0.4);
            }}
        """)
        self.input_field.textChanged.connect(self.update_results)
        self.input_field.returnPressed.connect(self.execute_action)

        btn_qss = f"""
            QPushButton {{
                {element_style}
                border: 1px solid rgba(255, 255, 255, 0.4);
                border-radius: 25px;
            }}
            QPushButton:hover {{ 
                background-color: rgba(255, 255, 255, 0.95); 
                border: 1px solid rgba(0, 122, 255, 0.3);
            }}
        """

        self.btn_paste = QPushButton()
        self.btn_paste.setFixedSize(50, 50)
        self.btn_paste.setStyleSheet(btn_qss)
        self.btn_paste.setIcon(QIcon(ICON_PASTE_PATH))
        self.btn_paste.setIconSize(QSize(22, 22))
        self.btn_paste.clicked.connect(self.paste_from_clipboard)

        self.btn_screenshot = QPushButton()
        self.btn_screenshot.setFixedSize(50, 50)
        self.btn_screenshot.setStyleSheet(btn_qss)
        self.btn_screenshot.setIcon(QIcon(ICON_SCREENSHOT_PATH))
        self.btn_screenshot.setIconSize(QSize(22, 22))
        self.btn_screenshot.clicked.connect(self.take_screenshot)

        self.btn_terminal = QPushButton()
        self.btn_terminal.setFixedSize(50, 50)
        self.btn_terminal.setStyleSheet(btn_qss)
        self.btn_terminal.setIcon(QIcon(ICON_TERMINAL_PATH))
        self.btn_terminal.setIconSize(QSize(22, 22))
        self.btn_terminal.clicked.connect(self.open_terminal)

        top_layout.addWidget(self.input_field)
        top_layout.addWidget(self.btn_paste)
        top_layout.addWidget(self.btn_screenshot)
        top_layout.addWidget(self.btn_terminal)

        self.result_list = QListWidget()
        self.result_list.setFont(QFont("Cantarell", 16))
        self.result_list.setIconSize(QSize(32, 32))

        self.result_list.setStyleSheet("""
            QListWidget {
                background-color: rgba(245, 246, 248, 0.9); 
                border-radius: 18px;
                padding: 8px;
                color: #1a1a1a;
                border: 1px solid rgba(0, 0, 0, 0.06);
                margin-top: 12px;
                outline: none;
            }
            QListWidget::item {
                padding: 10px 15px;
                border-radius: 10px;
                margin-bottom: 2px;
                color: #222222;
            }
            QListWidget::item:selected {
                background-color: #007aff; 
                color: #ffffff;
            }
        """)
        self.result_list.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        self.result_list.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)

        shadow = QGraphicsDropShadowEffect()
        shadow.setBlurRadius(35)
        shadow.setColor(QColor(0, 0, 0, 70))
        shadow.setOffset(0, 8)
        self.setGraphicsEffect(shadow)

        main_layout.addWidget(top_panel)
        main_layout.addWidget(self.result_list)

        QShortcut(QKeySequence("Down"), self.input_field, self.select_next)
        QShortcut(QKeySequence("Up"), self.input_field, self.select_prev)
        QShortcut(QKeySequence("Escape"), self, QApplication.quit)
        QShortcut(QKeySequence("Ctrl+P"), self.input_field, self.toggle_pin)

        self.animation = QPropertyAnimation(self, b"geometry")
        self.animation.setDuration(180)
        self.animation.setEasingCurve(QEasingCurve.Type.OutCubic)

    def center_on_screen(self):
        screen = QApplication.primaryScreen().geometry()
        x = (screen.width() - self.width()) // 2
        y = int(screen.height() * 0.15)
        self.move(x, y)

    def animate_window_height(self, target_height):
        if self.current_target_height == target_height:
            return
        self.current_target_height = target_height

        start_geo = self.geometry()
        end_geo = QRect(start_geo.x(), start_geo.y(), start_geo.width(), target_height)

        self.animation.stop()
        self.animation.setStartValue(start_geo)
        self.animation.setEndValue(end_geo)
        self.animation.start()

    def load_apps(self):
        apps = []
        seen_names = set()
        directories = ['/usr/share/applications', os.path.expanduser('~/.local/share/applications')]
        for directory in directories:
            if not os.path.exists(directory): continue
            for filename in os.listdir(directory):
                if filename.endswith('.desktop'):
                    path = os.path.join(directory, filename)
                    name, exec_cmd, icon = None, None, None
                    try:
                        with open(path, 'r', encoding='utf-8', errors='ignore') as f:
                            in_desktop_entry = False
                            for line in f:
                                line = line.strip()
                                if line == '[Desktop Entry]':
                                    in_desktop_entry = True
                                elif line.startswith('[') and in_desktop_entry:
                                    break

                                if in_desktop_entry:
                                    if line.startswith('Name=') and not name:
                                        name = line.split('=', 1)[1]
                                    elif line.startswith('Exec=') and not exec_cmd:
                                        exec_cmd = line.split('=', 1)[1].split(' %')[0]
                                    elif line.startswith('Icon=') and not icon:
                                        icon = line.split('=', 1)[1]
                        if name and exec_cmd and name not in seen_names:
                            seen_names.add(name)
                            apps.append({'name': name, 'exec': exec_cmd, 'icon': icon})
                    except Exception:
                        pass
        return apps

    def paste_from_clipboard(self):
        clipboard = QApplication.clipboard()
        self.input_field.setText(clipboard.text())

    def toggle_pin(self):
        item = self.result_list.currentItem()
        if not item: return
        data = item.data(Qt.ItemDataRole.UserRole)
        if not data or data.get("type") != "app": return

        app_name = data["name"]
        if app_name in self.pinned_apps:
            self.pinned_apps.remove(app_name)
        else:
            self.pinned_apps.append(app_name)

        self.save_pinned()
        self.update_results(self.input_field.text())

    def update_results(self, text):
        self.result_list.clear()

        if not text.strip():
            if self.pinned_apps:
                for pinned_name in self.pinned_apps:
                    app_data = next((a for a in self.apps if a['name'] == pinned_name), None)
                    item = QListWidgetItem(f" ★  {pinned_name}")
                    if app_data and app_data.get('icon'):
                        icon = QIcon.fromTheme(app_data['icon'])
                        if not icon.isNull(): item.setIcon(icon)

                    item.setData(Qt.ItemDataRole.UserRole, {
                        "type": "app",
                        "name": pinned_name,
                        "exec": app_data['exec'] if app_data else pinned_name
                    })
                    self.result_list.addItem(item)

                self.result_list.show()
                self.result_list.setCurrentRow(0)
                items_count = self.result_list.count()
                target_h = 80 + (items_count * 56) + 20
                self.animate_window_height(min(target_h, 500))
            else:
                self.result_list.hide()
                self.animate_window_height(80)
            return

        self.result_list.show()

        math_text = text.replace('^', '**')
        if re.match(r'^[0-9\+\-\*\/\(\)\.\s]+$', math_text):
            try:
                result = eval(math_text)
                if isinstance(result, float) and result.is_integer():
                    result = int(result)

                item = QListWidgetItem(f"   {math_text}   =   {result}")
                font = QFont("Cantarell", 18, QFont.Weight.Bold)
                item.setFont(font)
                item.setData(Qt.ItemDataRole.UserRole, {"type": "math", "value": str(result)})
                self.result_list.addItem(item)
            except Exception:
                pass

        query = text.lower()
        matched_apps = [app for app in self.apps if query in app['name'].lower()]

        matched_apps.sort(key=lambda app: (
            not app['name'].lower().startswith(query),
            not any(word.startswith(query) for word in app['name'].lower().split()),
            len(app['name']),
            app['name'].lower()
        ))

        matched_names = set()
        for app in matched_apps:
            if app['name'] not in matched_names and len(matched_names) < 6:
                matched_names.add(app['name'])
                is_pinned = app['name'] in self.pinned_apps
                prefix = " ★  " if is_pinned else "     "
                item = QListWidgetItem(f"{prefix}{app['name']}")

                if app.get('icon'):
                    icon = QIcon.fromTheme(app['icon'])
                    if not icon.isNull(): item.setIcon(icon)
                item.setData(Qt.ItemDataRole.UserRole, {"type": "app", "name": app['name'], "exec": app['exec']})
                self.result_list.addItem(item)

        if len(text.strip()) >= 2:
            try:
                safe_text = text.replace("'", "'\\''")
                cmd = f"find ~ -maxdepth 4 \\( -path '*/.*' -prune \\) -o -type f -iname '*{safe_text}*' -print 2>/dev/null | head -n 5"
                output = subprocess.check_output(cmd, shell=True, text=True)
                for path in output.splitlines():
                    path = path.strip()
                    if path:
                        name = os.path.basename(path)
                        short_path = path.replace(os.path.expanduser("~"), "~")
                        item = QListWidgetItem(f" 📄  {name}  ({os.path.dirname(short_path)})")
                        item.setIcon(QIcon.fromTheme("text-x-generic"))
                        item.setData(Qt.ItemDataRole.UserRole, {"type": "file", "path": path})
                        self.result_list.addItem(item)
            except Exception:
                pass

        web_item = QListWidgetItem(f"      Search: {text}")
        web_item.setIcon(QIcon.fromTheme("edit-find"))
        web_item.setData(Qt.ItemDataRole.UserRole, {"type": "web", "query": text})
        self.result_list.addItem(web_item)

        self.result_list.setCurrentRow(0)

        items_count = self.result_list.count()
        target_h = 80 + (items_count * 56) + 20
        self.animate_window_height(min(target_h, 540))

    def execute_action(self):
        item = self.result_list.currentItem()
        if not item: return
        data = item.data(Qt.ItemDataRole.UserRole)

        if data["type"] == "app":
            subprocess.Popen(data["exec"], shell=True, start_new_session=True)
        elif data["type"] == "file":
            subprocess.Popen(["xdg-open", data["path"]])
        elif data["type"] == "web":
            webbrowser.open(f"https://google.com/search?q={data['query']}")
        elif data["type"] == "math":
            QApplication.clipboard().setText(data["value"])

        QApplication.quit()

    def take_screenshot(self):
        subprocess.Popen("flameshot gui", shell=True)
        QApplication.quit()

    def open_terminal(self):
        subprocess.Popen("konsole", shell=True) #change to your preffered terminal
        QApplication.quit()

    def select_next(self):
        row = self.result_list.currentRow()
        if row < self.result_list.count() - 1: self.result_list.setCurrentRow(row + 1)

    def select_prev(self):
        row = self.result_list.currentRow()
        if row > 0: self.result_list.setCurrentRow(row - 1)

    def focusOutEvent(self, event):
        QApplication.quit()


if __name__ == '__main__':
    app = QApplication(sys.argv)
    ex = SpotlightClone()
    ex.show()
    sys.exit(app.exec())

