import os, sys
from PyQt5.QtWidgets import QApplication, QWidget, QPushButton, QVBoxLayout, QTextEdit, QFileDialog

class DirectoryStructureViewer(QWidget):
    def __init__(self):
        super().__init__()
        self.initUI()

    def initUI(self):
        self.setWindowTitle('Directory Structure Viewer')
        self.setGeometry(100, 100, 600, 400)

        layout = QVBoxLayout()

        self.browse_button = QPushButton('Browse Folder', self)
        self.browse_button.clicked.connect(self.browse_folder)
        layout.addWidget(self.browse_button)

        self.text_area = QTextEdit(self)
        self.text_area.setReadOnly(True)
        layout.addWidget(self.text_area)

        # Create a new text edit area for file contents
        self.file_contents_area = QTextEdit(self)
        self.file_contents_area.setReadOnly(True)
        layout.addWidget(self.file_contents_area)

        self.setLayout(layout)

    def browse_folder(self):
        folder_path = QFileDialog.getExistingDirectory(self, 'Select Folder')
        if folder_path:
            structure = self.get_directory_structure(folder_path)
            self.text_area.setText(structure)

            # Get the file contents and format them
            self.format_file_contents(folder_path)

    def get_directory_structure(self, path, prefix=''):
        result = ''
        root_directory = os.path.basename(path)  # Get the root directory name
        result += f"{prefix}└── {root_directory}/\n"  # Prepend the root directory

        ignore_patterns = self.read_gitignore(path)
        for entry in os.listdir(path):
            full_path = os.path.join(path, entry)
            if entry == 'venv' or entry == '.git' or entry == 'migrations' or entry == '__pycache__':
                continue
            if os.path.isdir(full_path) and not any(pattern in entry for pattern in ignore_patterns):
                result += f"{prefix}│   ├── {entry}/\n"
                result += self.get_directory_structure(full_path, prefix + "│   │   ")
            elif os.path.isfile(full_path) and not any(pattern in entry for pattern in ignore_patterns):
                result += f"{prefix}│   └── {entry}\n"
        return result

    def read_gitignore(self, path):
        ignore_patterns = []
        gitignore_path = os.path.join(path, '.gitignore')
        if os.path.exists(gitignore_path):
            with open(gitignore_path, 'r') as file:
                for line in file:
                    pattern = line.strip()
                    if pattern and not pattern.startswith('#'):
                        ignore_patterns.append(pattern)
        return ignore_patterns

    def format_file_contents(self, folder_path):
        file_contents = []  # Initialize as a list to gather all file contents
        exclude_files = {'.DS_Store', 'requirements.txt'}  # Set of files to exclude

        for filename in os.listdir(folder_path):
            if filename in exclude_files:
                continue  # Skip excluded files

            file_path = os.path.join(folder_path, filename)
            if os.path.isfile(file_path):
                try:
                    with open(file_path, 'r', encoding='utf-8') as file:
                        contents = file.read()
                except UnicodeDecodeError:
                    try:
                        with open(file_path, 'r', encoding='latin-1') as file:
                            contents = file.read()
                    except UnicodeDecodeError:
                        contents = "Unable to decode file contents."
                
                # Format the file contents as per your requirements
                formatted_contents = f"```{filename}\n{contents}\n```\n"
                file_contents.append(formatted_contents)

        # Join all formatted file contents with an extra newline between them
        complete_contents = "\n".join(file_contents)
        
        # Set the complete contents to the QTextEdit widget
        self.file_contents_area.setText(complete_contents)

        return complete_contents

if __name__ == '__main__':
    app = QApplication([])
    ex = DirectoryStructureViewer()
    ex.show()
    sys.exit(app.exec_())