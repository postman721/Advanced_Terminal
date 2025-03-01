# License: This project is licensed under the Apache 2.0.
# Author: JJ Posti - techtimejourney.net - 2024
import sys
import os
import subprocess
import threading
from PyQt5.QtWidgets import (
    QApplication, QMainWindow, QVBoxLayout, QWidget, QPlainTextEdit,
    QMenu, QAction, QTabWidget, QTabBar, QInputDialog, QLineEdit, QTextEdit, QPushButton, QHBoxLayout, QLabel, QStackedLayout
)
from PyQt5.QtCore import Qt, pyqtSignal, QEvent
from PyQt5.QtGui import QTextCharFormat, QSyntaxHighlighter, QTextCursor, QColor, QFont

# Unified color scheme
BACKGROUND_COLOR = "#1e1e1e"  # Darker gray for background
TEXT_COLOR = "#e0e0e0"        # Slightly darker white for text
TAB_BACKGROUND_COLOR = "#2a2a2a"  # Dark gray for inactive tabs
TAB_SELECTED_COLOR = "#1a1a1a"    # Darker gray for selected tab

class CommandSyntaxHighlighter(QSyntaxHighlighter):
    def __init__(self, document):
        super().__init__(document)
        self.keyword_format = QTextCharFormat()
        self.keyword_format.setForeground(QColor("#FFCC00"))  # Yellow for commands
        self.path_format = QTextCharFormat()
        self.path_format.setForeground(QColor("#00FF00"))     # Green for paths

    def highlightBlock(self, text):
        keywords = ["cd", "ls", "cat", "echo", "pwd", "whoami", "apt-get", "grep", "find",
                    "mkdir", "rm", "rmdir", "cp", "mv", "sudo", "chmod", "chown", "exit",
                    "clear", "touch", "reset", "az", "kubectl", "docker", "text"]
        paths = [p for p in text.split() if os.path.exists(p)]

        for keyword in keywords:
            index = text.find(keyword)
            while index >= 0:
                if (index == 0 or not text[index - 1].isalnum()) and \
                   (index + len(keyword) == len(text) or not text[index + len(keyword)].isalnum()):
                    self.setFormat(index, len(keyword), self.keyword_format)
                index = text.find(keyword, index + len(keyword))

        for path in paths:
            index = text.find(path)
            while index >= 0:
                self.setFormat(index, len(path), self.path_format)
                index = text.find(path, index + len(path))

class CustomTabBar(QTabBar):
    doubleClickTab = pyqtSignal(int)

    def __init__(self, parent=None):
        super().__init__(parent)

    def mouseDoubleClickEvent(self, event):
        super().mouseDoubleClickEvent(event)
        if event.button() == Qt.LeftButton:
            self.doubleClickTab.emit(self.currentIndex())

class EditorWidget(QWidget):
    """A simple nano-like text editor embedded within the terminal application."""
    def __init__(self, file_path, on_close_callback, parent=None):
        super().__init__(parent)
        self.file_path = file_path
        self.on_close_callback = on_close_callback
        self.initUI()

    def initUI(self):
        layout = QVBoxLayout(self)

        # Label to show editing file
        self.label = QLabel(f"Editing: {self.file_path}")
        self.label.setStyleSheet(f"color: {TEXT_COLOR};")
        layout.addWidget(self.label)

        # Text edit area
        self.text_edit = QTextEdit(self)
        self.text_edit.setStyleSheet(f"""
            background-color: {BACKGROUND_COLOR};
            color: {TEXT_COLOR};
            font-family: Consolas, monospace;
            font-size: 14px;
        """)
        self.text_edit.setFont(QFont("Consolas", 14))
        layout.addWidget(self.text_edit)

        # Buttons for Save and Exit
        button_layout = QHBoxLayout()
        self.save_button = QPushButton("Save")
        self.save_button.setStyleSheet(f"""
            QPushButton {{
                background-color: #4CAF50;
                color: white;
                border: none;
                padding: 5px 10px;
                text-align: center;
                text-decoration: none;
                font-size: 14px;
                margin: 4px 2px;
                cursor: pointer;
            }}
            QPushButton:hover {{
                background-color: #45a049;
            }}
        """)
        self.exit_button = QPushButton("Exit")
        self.exit_button.setStyleSheet(f"""
            QPushButton {{
                background-color: #f44336;
                color: white;
                border: none;
                padding: 5px 10px;
                text-align: center;
                text-decoration: none;
                font-size: 14px;
                margin: 4px 2px;
                cursor: pointer;
            }}
            QPushButton:hover {{
                background-color: #da190b;
            }}
        """)
        button_layout.addWidget(self.save_button)
        button_layout.addWidget(self.exit_button)
        layout.addLayout(button_layout)

        # Connect buttons
        self.save_button.clicked.connect(self.save_file)
        self.exit_button.clicked.connect(self.exit_editor)

        # Load file content
        self.load_file()

    def load_file(self):
        try:
            with open(self.file_path, 'r') as f:
                content = f.read()
                self.text_edit.setPlainText(content)
        except FileNotFoundError:
            # If file doesn't exist, create it
            open(self.file_path, 'a').close()
            self.text_edit.setPlainText("")
        except Exception as e:
            self.text_edit.setPlainText(f"Error loading file: {e}")

    def save_file(self):
        try:
            with open(self.file_path, 'w') as f:
                content = self.text_edit.toPlainText()
                f.write(content)
            self.on_close_callback("File saved successfully.\n")
        except Exception as e:
            self.on_close_callback(f"Error saving file: {e}\n")

    def exit_editor(self):
        self.on_close_callback("Exited editor.\n")
        self.parentWidget().closeEditor()
        self.close()

class TerminalWidget(QPlainTextEdit):
    outputWritten = pyqtSignal(str)
    commandFinished = pyqtSignal()
    promptUpdated = pyqtSignal(str)

    def __init__(self, parent=None):
        super().__init__(parent)
        self.cwd = os.getcwd()
        self.highlighter = CommandSyntaxHighlighter(self.document())
        self.updatePrompt()
        self.initUI()

        self.in_editor = False

        self.outputWritten.connect(self.appendPlainText)
        self.commandFinished.connect(self.onCommandFinished)
        self.promptUpdated.connect(self.updatePromptDisplay)

    def updatePrompt(self):
        try:
            username = os.getlogin()
        except OSError:
            username = "user"
        try:
            hostname = os.uname().nodename
        except AttributeError:
            hostname = "host"
        self.prompt = f"{username}@{hostname}:{self.cwd}$ "

    def initUI(self):
        self.setStyleSheet(f"""
            background-color: {BACKGROUND_COLOR};
            color: {TEXT_COLOR};
            border: none;
            padding: 10px;
            font-family: Consolas, monospace;
            font-size: 14px;
        """)
        self.setFont(QFont("Consolas", 14))
        self.setReadOnly(False)
        self.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOn)
        self.appendPlainText(f"# Welcome to terminal!\n# Use 'text <filename>' to open the editor.\n")
        self.appendPlainText(self.prompt)
        self.moveCursorToEnd()
        self.installEventFilter(self)
        self.setContextMenuPolicy(Qt.CustomContextMenu)
        self.customContextMenuRequested.connect(self.showContextMenu)

    def moveCursorToEnd(self):
        cursor = self.textCursor()
        cursor.movePosition(QTextCursor.End)
        self.setTextCursor(cursor)

    def eventFilter(self, source, event):
        if self.in_editor:
            return super().eventFilter(source, event)

        if source is self and event.type() == QEvent.KeyPress:
            cursor = self.textCursor()
            if event.key() in (Qt.Key_Return, Qt.Key_Enter):
                self.executeCommand()
                return True
            elif event.key() == Qt.Key_Backspace:
                if cursor.positionInBlock() <= len(self.prompt):
                    return True
            elif event.key() == Qt.Key_Left:
                if cursor.positionInBlock() <= len(self.prompt):
                    return True
            elif event.key() == Qt.Key_Home:
                cursor.movePosition(QTextCursor.StartOfLine)
                cursor.movePosition(QTextCursor.Right, QTextCursor.MoveAnchor, len(self.prompt))
                self.setTextCursor(cursor)
                return True
            elif event.key() == Qt.Key_Up:
                self.showPreviousCommand()
                return True
            elif event.key() == Qt.Key_Down:
                self.showNextCommand()
                return True
        return super().eventFilter(source, event)

    def executeCommand(self):
        text_cursor = self.textCursor()
        text_cursor.movePosition(text_cursor.StartOfLine)
        text_cursor.movePosition(text_cursor.EndOfLine, QTextCursor.KeepAnchor)
        command = text_cursor.selectedText()[len(self.prompt):].strip()

        if command:
            if command == "exit":
                self.runCommand(command)
            elif command == "clear":
                self.clear()
                self.updatePromptDisplay(self.prompt)
                self.moveCursorToEnd()
            elif command == "reset":
                self.resetTerminal()
            elif command.startswith("cd "):
                try:
                    new_dir = command.split(' ', 1)[1]
                    os.chdir(new_dir)
                    self.cwd = os.getcwd()
                except Exception as e:
                    self.outputWritten.emit(f"Error: {str(e)}\n")
                self.updatePrompt()
                self.appendPlainText(self.prompt)
                self.moveCursorToEnd()
            elif command.startswith("text"):
                parts = command.split(maxsplit=1)
                if len(parts) == 2:
                    filename = parts[1]
                    self.runText(filename)
                else:
                    self.outputWritten.emit("Usage: text <filename>\n")
                    self.updatePromptDisplay(self.prompt)
                    self.moveCursorToEnd()
            else:
                threading.Thread(target=self.runCommand, args=(command,), daemon=True).start()

    def runText(self, filename):
        self.in_editor = True
        self.outputWritten.emit("")  # Move to new line

        # Now call 'openEditor' on the parent 'TabContentWidget'
        self.parentWidget().openEditor(filename, self.onEditorClosed)

    def onEditorClosed(self, message):
        self.outputWritten.emit(message)
        self.updatePromptDisplay(self.prompt)
        self.moveCursorToEnd()
        self.in_editor = False
        self.commandFinished.emit()

    def runCommand(self, command):
        self.outputWritten.emit(f"\n{self.prompt}{command}\n")

        if command == "exit":
            self.commandFinished.emit()
            QApplication.quit()
            return

        if command.startswith('cd '):
            try:
                new_dir = command.split(' ', 1)[1]
                os.chdir(new_dir)
                self.cwd = os.getcwd()
            except Exception as e:
                self.outputWritten.emit(f"Error: {str(e)}\n")
            self.updatePrompt()
            self.promptUpdated.emit(self.prompt)
            self.commandFinished.emit()
            return

        try:
            process = subprocess.Popen(
                ['/bin/bash', '-c', command],
                cwd=self.cwd,
                text=True,
                stdin=subprocess.PIPE,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE
            )
            stdout, stderr = process.communicate()

            if stdout:
                self.outputWritten.emit(stdout)
            if stderr:
                self.outputWritten.emit(stderr)
        except Exception as e:
            self.outputWritten.emit(f"Error executing command: {e}\n")

        self.updatePrompt()
        self.promptUpdated.emit(self.prompt)
        self.commandFinished.emit()

    def onCommandFinished(self):
        self.appendPlainText(self.prompt)
        self.moveCursorToEnd()

    def updatePromptDisplay(self, prompt):
        self.updatePrompt()
        self.moveCursorToEnd()

    def showContextMenu(self, point):
        menu = QMenu(self)
        menu.setStyleSheet("""
            QMenu {
                background-color: #333333;
                color: white;
            }
            QMenu::item:selected {
                background-color: white;
                color: black;
            }
        """)
        copy_action = QAction("Copy", self)
        paste_action = QAction("Paste", self)
        clear_action = QAction("Clear", self)
        reset_action = QAction("Reset", self)

        copy_action.triggered.connect(self.copy)
        paste_action.triggered.connect(self.paste)
        clear_action.triggered.connect(self.clear)
        reset_action.triggered.connect(self.resetTerminal)

        menu.addAction(copy_action)
        menu.addAction(paste_action)
        menu.addAction(clear_action)
        menu.addAction(reset_action)
        menu.addSeparator()

        menu.exec_(self.mapToGlobal(point))

    def showPreviousCommand(self):
        pass

    def showNextCommand(self):
        pass

    def replaceCurrentLine(self, text):
        cursor = self.textCursor()
        cursor.movePosition(QTextCursor.StartOfLine)
        cursor.movePosition(QTextCursor.EndOfLine, QTextCursor.KeepAnchor)
        cursor.removeSelectedText()
        cursor.insertText(self.prompt + text)
        self.setTextCursor(cursor)

class TabContentWidget(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.stack = QStackedLayout(self)
        self.terminal = TerminalWidget(self)
        self.stack.addWidget(self.terminal)
        self.editor = None

    def openEditor(self, filename, callback):
        if self.editor is None:
            self.editor = EditorWidget(filename, callback, self)
            self.stack.addWidget(self.editor)
        else:
            self.editor.file_path = filename
            self.editor.load_file()
        self.stack.setCurrentWidget(self.editor)

    def closeEditor(self):
        if self.editor:
            self.stack.setCurrentWidget(self.terminal)

class TerminalTabWidget(QTabWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setTabBar(CustomTabBar(self))
        self.setTabsClosable(True)
        self.setMovable(True)
        self.tabCloseRequested.connect(self.closeTab)
        self.setStyleSheet(f"""
            QTabWidget::pane {{
                border: none;
                background-color: {BACKGROUND_COLOR};
            }}
            QTabBar::tab {{
                background: {TAB_BACKGROUND_COLOR};
                color: {TEXT_COLOR};
                padding: 5px;
                margin: 0;
                border: 1px solid #444;
            }}
            QTabBar::tab:selected {{
                background: {TAB_SELECTED_COLOR};
            }}
        """)
        self.addNewTab()
        self.tabBar().doubleClickTab.connect(self.addNewTab)

    def addNewTab(self):
        tab_content = TabContentWidget(self)
        super().addTab(tab_content, f"Session {self.count() + 1}")
        self.setCurrentWidget(tab_content)

    def closeTab(self, index):
        if self.count() > 1:
            self.widget(index).deleteLater()
            self.removeTab(index)

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Advanced Terminal")
        self.setGeometry(100, 100, 800, 600)
        self.central_widget = QWidget()
        self.setCentralWidget(self.central_widget)

        self.layout = QVBoxLayout(self.central_widget)
        self.terminal_tabs = TerminalTabWidget(self)
        self.layout.addWidget(self.terminal_tabs)

        self.setStyleSheet(f"""
            background-color: {BACKGROUND_COLOR};
            color: {TEXT_COLOR};
        """)

if __name__ == "__main__":
    app = QApplication(sys.argv)
    main_window = MainWindow()
    main_window.show()
    sys.exit(app.exec_())
