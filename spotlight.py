#!/usr/bin/env python3
import sys
import os
import subprocess
import webbrowser
import re
from PyQt6.QtWidgets import (QApplication, QWidget, QVBoxLayout, QHBoxLayout,QLineEdit, QListWidget, QListWidgetItem, QPushButton,QGraphicsDropShadowEffect)
from PyQt6.QtCore import Qt, QSize
from PyQt6.QtGui import QFont, QKeySequence, QShortcut, QIcon, QColor


class SpotlightClone(QWidget):
    def __init__(self):
        super().__init__()
        self.apps = self.load_apps()
        self.initUI()
        self.update_results("")

    def initUI(self):
        self.setWindowFlags(Qt.WindowType.FramelessWindowHint | Qt.WindowType.WindowStaysOnTopHint | Qt.WindowType.Tool)
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)

        self.resize(800, 500)
        self.center_on_screen()

        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(15, 15, 15, 15)
        main_layout.setAlignment(Qt.AlignmentFlag.AlignTop)
        top_panel = QWidget()
        top_layout = QHBoxLayout(top_panel)
        top_layout.setContentsMargins(0, 0, 0, 0)
        top_layout.setSpacing(12)

        element_style = """
            background-color: rgba(225, 230, 250, 0.85); 
            color: #1a1a1a;
            border-radius: 25px;
        """

        self.input_field = QLineEdit()
        self.input_field.setPlaceholderText("Search")
        self.input_field.setFont(QFont("Cantarell", 18))
        self.input_field.setFixedHeight(50)
        self.input_field.setStyleSheet(f"""
            QLineEdit {{
                {element_style}
                padding-left: 20px;
                border: 1px solid rgba(255, 255, 255, 0.4);
            }}
            QLineEdit:focus {{
                background-color: rgba(235, 240, 255, 0.95);
                border: 1px solid rgba(255, 255, 255, 0.8);
            }}
        """)
        self.input_field.textChanged.connect(self.update_results)
        self.input_field.returnPressed.connect(self.execute_action)

        btn_qss = f"""
            QPushButton {{
                {element_style}
                font-size: 20px;
                border: 1px solid rgba(255, 255, 255, 0.4);
            }}
            QPushButton:hover {{ 
                background-color: rgba(255, 255, 255, 0.95); 
                border: 1px solid rgba(255, 255, 255, 0.8);
            }}
        """

        self.btn_screenshot = QPushButton("📸")
        self.btn_screenshot.setFixedSize(50, 50)
        self.btn_screenshot.setStyleSheet(btn_qss)
        self.btn_screenshot.clicked.connect(self.take_screenshot)

        self.btn_terminal = QPushButton("💻")
        self.btn_terminal.setFixedSize(50, 50)
        self.btn_terminal.setStyleSheet(btn_qss)
        self.btn_terminal.clicked.connect(self.open_terminal)

        top_layout.addWidget(self.input_field)
        top_layout.addWidget(self.btn_screenshot)
        top_layout.addWidget(self.btn_terminal)

        self.result_list = QListWidget()
        self.result_list.setFont(QFont("Cantarell", 16))
        self.result_list.setIconSize(QSize(32, 32))

        self.result_list.setStyleSheet("""
                    QListWidget {
                        background-color: rgba(255, 255, 255, 0.85); 
                        border-radius: 20px;
                        padding: 10px;
                        color: #000000;
                        border: 1px solid rgba(255, 255, 255, 0.3);
                        outline: none;
                    }
                    QListWidget::item {
                        padding: 12px;
                        border-radius: 10px;
                        color: #333;
                    }
                    QListWidget::item:selected {
                        background-color: rgba(0, 122, 255, 0.15); 
                        color: #007aff;
                        font-weight: bold;
                    }
                """)

        self.input_field.setStyleSheet(f"""
                    QLineEdit {{
                        background-color: rgba(255, 255, 255, 0.95);
                        color: #000;
                        border-radius: 25px;
                        padding-left: 20px;
                        border: 1px solid rgba(0,0,0,0.1);
                    }}
                """)
        self.result_list.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        self.result_list.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)

        shadow = QGraphicsDropShadowEffect()
        shadow.setBlurRadius(30)
        shadow.setColor(QColor(0, 0, 0, 150))
        shadow.setOffset(0, 10)
        self.result_list.setGraphicsEffect(shadow)

        self.result_list.hide()

        main_layout.addWidget(top_panel)
        main_layout.addWidget(self.result_list)

        QShortcut(QKeySequence("Down"), self.input_field, self.select_next)
        QShortcut(QKeySequence("Up"), self.input_field, self.select_prev)
        QShortcut(QKeySequence("Escape"), self, QApplication.quit)

    def center_on_screen(self):
        screen = QApplication.primaryScreen().geometry()
        x = (screen.width() - self.width()) // 2
        y = int(screen.height() * 0.15)
        self.move(x, y)

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

    def update_results(self, text):
        self.result_list.clear()

        if not text.strip():
            self.result_list.hide()
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
        matched_names = set()

        for app in matched_apps:
            if app['name'] not in matched_names and len(matched_names) < 6:
                matched_names.add(app['name'])
                item = QListWidgetItem(f"   {app['name']}")
                if app.get('icon'):
                    icon = QIcon.fromTheme(app['icon'])
                    if not icon.isNull(): item.setIcon(icon)
                item.setData(Qt.ItemDataRole.UserRole, {"type": "app", "exec": app['exec']})
                self.result_list.addItem(item)

        web_item = QListWidgetItem(f"   Search: {text}")
        web_item.setIcon(QIcon.fromTheme("edit-find"))
        web_item.setData(Qt.ItemDataRole.UserRole, {"type": "web", "query": text})
        self.result_list.addItem(web_item)

        self.result_list.setCurrentRow(0)

    def execute_action(self):
        item = self.result_list.currentItem()
        if not item: return
        data = item.data(Qt.ItemDataRole.UserRole)

        if data["type"] == "app":
            subprocess.Popen(data["exec"], shell=True, start_new_session=True)
        elif data["type"] == "web":
            webbrowser.open(f"https://google.com/search?q={data['query']}")
        elif data["type"] == "math":
            QApplication.clipboard().setText(data["value"])

        QApplication.quit()

    def take_screenshot(self):
        subprocess.Popen("flameshot gui", shell=True)
        QApplication.quit()

    def open_terminal(self):
        subprocess.Popen("konsole", shell=True) #change it to your preferred terminal
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