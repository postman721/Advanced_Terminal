# Advanced Terminal with Embedded Text Editor

A feature-rich terminal emulator built with PyQt5, offering multiple tabbed sessions and an embedded nano-like text editor.
Table of Contents

![screen](https://github.com/user-attachments/assets/8048afbb-235a-4e05-8d0a-8519f546a38e)


### Features

-    Tabbed Interface: Manage multiple terminal sessions within tabs.
-    Embedded Text Editor: Open and edit text files using a built-in editor with nano-like functionality.
-    Command Syntax Highlighting: Highlights common shell commands and file paths for better readability.
-    Command History: Navigate through previously entered commands using the up and down arrow keys.
-    Customizable Appearance: Adjust font sizes and enjoy a unified dark theme.
-    Context Menu: Right-click to access copy, paste, clear, reset, and font size options.
-    Supports Basic Shell Commands: Execute standard shell commands like cd, ls, grep, sudo etc.

### Prerequisites

    Python 3.6 or higher
    PyQt5

### Installation

sudo apt update

sudo apt install python3-pyqt5

### Usage

Run the application using Python:

chmod +x advanced_terminal.py

python3 advanced_terminal.py

### Terminal Commands

-    Standard Commands: You can use most standard shell commands like ls, cat, echo, etc.
-    Change Directory: Use cd <directory> to navigate between directories.
-    Clear Screen: Type clear to clear the terminal output.
-    Reset Terminal: Use reset to reset the terminal to its initial state.
-    Exit Application: Type exit to close the terminal emulator.

### Embedded Text Editor

-    Open Editor: Use the command text <filename> to open the embedded editor for a specific file.
-    Save Changes: Click the Save button within the editor to save your changes.
-    Exit Editor: Click the Exit button to return to the terminal.

### Tab Management

-    New Tab: Double-click on the tab bar to open a new terminal session.
-    Close Tab: Click the X on a tab to close it. The application requires at least one open tab.

### Context Menu

Right-click within the terminal area to access the context menu, which includes:

-    Copy
-    Paste
-    Clear
-    Reset


### License

This project is licensed under the Apache version 2.0. See the LICENSE file for details.

### Author

JJ Posti
Website: techtimejourney.net
Year: 2024
