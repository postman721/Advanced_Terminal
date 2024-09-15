# Advanced Terminal for Linux

An advanced terminal emulator application built with PySide2 and Python, featuring syntax highlighting and a tabbed interface with customizable functionality.

![terminal](https://github.com/user-attachments/assets/b0a2fa36-7c09-46a4-b010-eca2ae78bce8)

## Features

- **Tabbed Interface**: Manage multiple terminal sessions in tabs.
- **Syntax Highlighting**: Command syntax highlighting for enhanced readability.
- **Double-Click to Create New Tab**: Easily add new terminal tabs with a double-click.
- **Context Menu**: Copy, paste,clear and reset functionalities through the right click menu.
- **Password Handling:** Supports sudo commands with interactive password input.
- No history: Command history functionalities are not added. This enhances security. This may change in the future releases.
## Supported Commands

The terminal application supports a variety of commands for interacting with the system and performing basic terminal operations. Below is a list of commands that are supported:
Basic Commands

    cd <directory>
    Change the current working directory to <directory>. For example, cd /home/user changes to the /home/user directory.

    ls
    List the files and directories in the current working directory.

    cat <file>
    Display the contents of <file>.

    echo <text>
    Print <text> to the terminal.

    pwd
    Print the current working directory.

    clear
    Clear the terminal screen.

    reset
    Reset the terminal to its initial state.

    whoami
    Display the current username.

File and Directory Management

    mkdir <directory>
    Create a new directory named <directory>.

    rm <file>
    Remove <file>. Use with caution as it deletes files permanently.

    rmdir <directory>
    Remove the specified directory. The directory must be empty.

    cp <source> <destination>
    Copy <source> to <destination>.

    mv <source> <destination>
    Move or rename <source> to <destination>.

Permissions and Ownership

    chmod <permissions> <file>
    Change the permissions of <file>.

    chown <owner> <file>
    Change the ownership of <file> to <owner>.

Special Commands

    sudo <command>
    Execute <command> with superuser privileges. You will be prompted for your password.

    exit
    Exit the terminal session.

    touch <file>
    Create an empty file named <file>. If the file already exists, update its access and modification times.

    az <command>
    Execute an Azure CLI command (requires Azure CLI to be installed).

    kubectl <command>
    Execute a Kubernetes CLI command (requires Kubernetes CLI to be installed).

    docker <command>
    Execute a Docker CLI command (requires Docker to be installed).

Auto-Completion

    Tab Key
    Use the Tab key for auto-completing commands from the list of supported commands.

Terminal Operations

    Ctrl + C
    Send an interrupt signal to terminate the current command.

    Ctrl + L
    Clear the terminal screen.

    Ctrl + D
    Close the terminal session.


## Installation

To run this application, you need Python 3 and PySide2 installed. You can set up your environment using the following steps:

### On Debian-based Systems

1. **Update package lists and install dependencies, Debian example:**

   ```bash
   sudo apt-get update
   sudo apt-get update && sudo apt-get install -y python3 python3-pip libqt5core5a libqt5gui5 libqt5widgets5 python3-pyside*



## Usage

### Starting the Application
- Launch the application using the command:
  ```bash
  
  chmod +x advanced_terminal.py
  python3 advanced_terminal.py

Use the GUI to manage terminal tabs, execute commands, and utilize features like syntax highlighting and split view.

Creating a New Tab

    Double-click on a tab area to create a new terminal tab. 

Context Menu

    Right-click within the terminal area to access the context menu.




You can customize the appearance of Term by modifying the stylesheet in the python file.
Contributing

Feel free to submit issues or pull requests to contribute to the development of Term. For any bugs or feature requests, please open an issue on the GitHub repository.
License

This project is licensed under the Apache License 2.0.

Author

    JJ Posti - techtimejourney.net - 2024


