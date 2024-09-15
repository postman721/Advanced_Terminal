#License: This project is licensed under the Apache License 2.0.
#Author: JJ Posti - techtimejourney.net - 2024
#This is beta version 1.

import sys
import subprocess
import os
from PySide2.QtWidgets import QApplication, QMainWindow, QVBoxLayout, QWidget, QPlainTextEdit, QMenu, QAction, QTabWidget, QTabBar, QInputDialog, QLineEdit
from PySide2.QtCore import Qt, QEvent, Signal
from PySide2.QtGui import QTextCharFormat, QSyntaxHighlighter, QTextCursor, QColor

# Unified color scheme
BACKGROUND_COLOR = "#2b2b2b"  # Dark gray
TEXT_COLOR = "#ffffff"  # White
HIGHLIGHT_COLOR = "#444444"  # Slightly lighter gray for selection
TAB_BACKGROUND_COLOR = "#007bff"  # Blue background for tabs
TAB_SELECTED_COLOR = "#0056b3"  # Darker blue for selected tab

class CommandSyntaxHighlighter(QSyntaxHighlighter):
    def __init__(self, document):
        super().__init__(document)
        self.keyword_format = QTextCharFormat()
        self.keyword_format.setForeground(QColor("#FFCC00"))  # Yellow for commands
        self.path_format = QTextCharFormat()
        self.path_format.setForeground(QColor("#00FF00"))  # Green for paths

    def highlightBlock(self, text):
        if text.startswith("$ "):
            text = text[2:]  # Remove the prompt
        keywords = ["cd", "ls", "cat", "echo", "pwd", "whoami", "apt-get", "grep", "find", "mkdir", "rm", "rmdir", "cp", "mv", "sudo", "chmod", "chown", "exit", "clear", "touch", "reset", "az", "kubectl", "docker"]
        paths = [p for p in text.split() if os.path.exists(p)]

        for keyword in keywords:
            index = text.find(keyword)
            while index >= 0:
                self.setFormat(index, len(keyword), self.keyword_format)
                index = text.find(keyword, index + len(keyword))

        for path in paths:
            index = text.find(path)
            while index >= 0:
                self.setFormat(index, len(path), self.path_format)
                index = text.find(path, index + len(path))

class CustomTabBar(QTabBar):
    doubleClickTab = Signal(int)  # Custom signal to indicate tab double-click

    def __init__(self, parent=None):
        super().__init__(parent)
        
    def mouseDoubleClickEvent(self, event):
        super().mouseDoubleClickEvent(event)
        if event.button() == Qt.LeftButton:
            # Double-click detected, emit the custom signal with the current tab index
            self.doubleClickTab.emit(self.currentIndex())

class TerminalWidget(QPlainTextEdit):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.cwd = os.getcwd()  # Start with the current working directory
        self.highlighter = CommandSyntaxHighlighter(self.document())
        self.updatePrompt()
        self.initUI()

    def updatePrompt(self):
        """Update the prompt with the current directory."""
        self.prompt = f"{os.getlogin()}@{os.uname().nodename}:{self.cwd}$ "

    def initUI(self):
        self.setStyleSheet(f"""
            background-color: black; 
            color: white; 
            border: none;
            padding: 10px;
            font-family: Consolas, monospace;
            font-size: 14px;
        """)
        self.setReadOnly(False)
        self.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOn)
        self.appendPlainText(self.prompt)
        self.moveCursorToEnd()
        self.installEventFilter(self)
        self.setContextMenuPolicy(Qt.CustomContextMenu)
        self.customContextMenuRequested.connect(self.showContextMenu)

    def moveCursorToEnd(self):
        cursor = self.textCursor()
        cursor.movePosition(cursor.End)
        self.setTextCursor(cursor)

    def eventFilter(self, source, event):
        if source is self and event.type() == QEvent.KeyPress:
            if event.key() in (Qt.Key_Return, Qt.Key_Enter):
                self.executeCommand()
                return True
            elif event.key() == Qt.Key_Tab:
                self.autoCompleteCommand()
                return True
            elif event.key() == Qt.Key_Up:
                return True
            elif event.key() == Qt.Key_Down:
                return True
            elif event.key() == Qt.Key_Backspace:
                text_cursor = self.textCursor()
                if text_cursor.position() <= self.promptPosition():
                    return True
            elif event.key() == Qt.Key_C and event.modifiers() == Qt.ControlModifier:
                self.insertPlainText("^C\n")
                self.appendPlainText(self.prompt)
                self.moveCursorToEnd()
                return True
            elif event.key() == Qt.Key_L and event.modifiers() == Qt.ControlModifier:
                self.clear()
                self.appendPlainText(self.prompt)
                return True
            elif event.key() == Qt.Key_D and event.modifiers() == Qt.ControlModifier:
                QApplication.quit()  # Close the terminal on Ctrl+D
                return True
        return super().eventFilter(source, event)

    def promptPosition(self):
        return self.toPlainText().rfind(self.prompt) + len(self.prompt)

    def executeCommand(self):
        text_cursor = self.textCursor()
        text_cursor.movePosition(text_cursor.StartOfLine)
        text_cursor.movePosition(text_cursor.EndOfLine, text_cursor.KeepAnchor)
        command = text_cursor.selectedText()[len(self.prompt):].strip()

        if not command:
            self.appendPlainText(self.prompt)
            self.moveCursorToEnd()
            return
            
    # Add support for 'whoami' command
        if command == "whoami":
            try:
                result = subprocess.run(['whoami'], text=True, capture_output=True, check=True)
                self.appendPlainText(result.stdout)
            except subprocess.CalledProcessError as e:
                self.appendPlainText(f"Command failed with error:\n{e.stderr}")
            except Exception as e:
                self.appendPlainText(f"Error executing command: {e}")
            self.updatePrompt()
            self.appendPlainText(self.prompt)
            self.moveCursorToEnd()
            return            
            
        if command == "exit":
            QApplication.quit()
            return
             
        if command == "clear":
            self.clear()
            self.appendPlainText(self.prompt)
            return

        if command == "reset":
            self.resetTerminal()
            return

        self.appendPlainText("")

        if command.startswith("sudo "):
            # Handle sudo commands interactively with password input
            password, ok = QInputDialog.getText(self, "Password Required", "Enter your password:", echo=QLineEdit.Password)
            if ok and password:
                try:
                    # Use Popen to allow interaction for password entry
                    process = subprocess.Popen(
                        ['sudo', '-S', '/bin/bash', '-c', command[5:]],
                        cwd=self.cwd,
                        text=True,
                        stdin=subprocess.PIPE,
                        stdout=subprocess.PIPE,
                        stderr=subprocess.PIPE
                    )
                    # Pass the password followed by a newline to sudo's stdin
                    stdout, stderr = process.communicate(input=f"{password}\n")
                    if stdout:
                        self.appendPlainText(stdout)
                    if stderr:
                        self.appendPlainText(stderr)
                except subprocess.CalledProcessError as e:
                    self.appendPlainText(f"Command failed with error:\n{e.stderr}")
                except Exception as e:
                    self.appendPlainText(f"Error executing command: {e}")
            else:
                self.appendPlainText("Password input canceled.")
            return

        # For non-sudo commands
        try:
            result = subprocess.run(['/bin/bash', '-c', command], cwd=self.cwd, text=True, capture_output=True, check=True)
            if result.stdout:
                self.appendPlainText(result.stdout)
            if result.stderr:
                self.appendPlainText(result.stderr)
        except subprocess.CalledProcessError as e:
            self.appendPlainText(f"Command failed with error:\n{e.stderr}")
        except Exception as e:
            self.appendPlainText(f"Error executing command: {e}")

        if command.startswith('cd '):
            try:
                new_dir = command.split(' ', 1)[1]
                os.chdir(new_dir)
                self.cwd = os.getcwd()
            except Exception as e:
                self.appendPlainText(str(e))

        self.updatePrompt()
        self.appendPlainText(self.prompt)
        self.moveCursorToEnd()

    def resetTerminal(self):
        """Reset the terminal to its initial state."""
        self.clear()
        self.cwd = os.getcwd()  # Reset to the current working directory
        self.updatePrompt()
        self.appendPlainText(self.prompt)
        self.moveCursorToEnd()

    def autoCompleteCommand(self):
        text_cursor = self.textCursor()
        current_line = self.document().findBlockByLineNumber(text_cursor.blockNumber()).text()

        # Strip the prompt from the current line
        if current_line.startswith(self.prompt):
            current_line = current_line[len(self.prompt):]

        if not current_line.strip():
            return  # Do nothing if there's no text to complete

        # Split the current command from the line
        parts = current_line.split()
        if len(parts) == 0:
            return

        command = parts[0]

        # Commands for auto-completion
        commands = ["cd", "ls", "cat", "echo", "grep", "find", "mkdir", "rm", "rmdir", "cp", "mv", "sudo", "chmod", "chown", "exit", "clear", "touch", "reset"]

        # Find matching commands
        matches = [cmd for cmd in commands if cmd.startswith(command)]
        if matches:
            text_cursor.movePosition(text_cursor.StartOfLine, text_cursor.KeepAnchor)
            text_cursor.removeSelectedText()
            self.insertPlainText(self.prompt + matches[0])

        self.moveCursorToEnd()

    def keyPressEvent(self, event):
        if event.key() == Qt.Key_V and event.modifiers() == Qt.ControlModifier:
            clipboard = QApplication.clipboard()
            self.insertPlainText(clipboard.text())
        else:
            super().keyPressEvent(event)

    def showContextMenu(self, point):
        menu = QMenu(self)
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

        menu.exec_(self.mapToGlobal(point))

class TerminalTabWidget(QTabWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setTabBar(CustomTabBar(self))  # Use custom tab bar
        self.setTabsClosable(True)
        self.setMovable(True)
        self.tabCloseRequested.connect(self.closeTab)
        self.setStyleSheet(f"""
            QTabWidget::pane {{
                border: none;
            }}
            QTabBar::tab {{
                background: {TAB_BACKGROUND_COLOR};
                color: white;
                padding: 5px;
                margin: 0;
                border: 1px solid #444;
            }}
            QTabBar::tab:selected {{
                background: {TAB_SELECTED_COLOR};
            }}
        """)
        self.addNewTab()

        # Connect the doubleClickTab signal to the addNewTab slot
        self.tabBar().doubleClickTab.connect(self.addNewTab)

    def addNewTab(self):
        """This method is used to create and add a new terminal tab."""
        terminal = TerminalWidget(self)
        super().addTab(terminal, f"Session {self.count() + 1}")  # Call the parent class's addTab() method
        self.setCurrentWidget(terminal)

    def closeTab(self, index):
        if self.count() > 1:
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

if __name__ == "__main__":
    app = QApplication(sys.argv)
    main_window = MainWindow()
    main_window.show()
    sys.exit(app.exec_())
