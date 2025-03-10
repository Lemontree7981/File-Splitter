#!/usr/bin/env python3
import os
import sys
from PyQt5.QtWidgets import (
    QApplication, QMainWindow,QPushButton, QTabWidget, QWidget, QVBoxLayout,
    QHBoxLayout, QLabel, QLineEdit, QProgressBar, QTextEdit, QFileDialog,
    QMessageBox, QGroupBox, QFormLayout, QComboBox, QDoubleSpinBox, QSlider
)
from PyQt5.QtCore import Qt, QThread, pyqtSignal
from PyQt5.QtGui import QFont, QIcon

def parse_size(size_str):
    """
    Parse a readable size string (example., 2MB, 500KB, 1GB) into integer bytes.
    """
    size_str = size_str.strip().upper()
    if size_str.endswith('GB') or size_str.endswith('G'):
        number = size_str[:-2] if size_str.endswith('GB') else size_str[:-1]
        return int(float(number) * 1024 * 1024 * 1024)
    elif size_str.endswith('MB') or size_str.endswith('M'):
        number = size_str[:-2] if size_str.endswith('MB') else size_str[:-1]
        return int(float(number) * 1024 * 1024)
    elif size_str.endswith('KB') or size_str.endswith('K'):
        number = size_str[:-2] if size_str.endswith('KB') else size_str[:-1]
        return int(float(number) * 1024)
    else:
        return int(size_str)

class FileBrowserLineEdit(QLineEdit):
    """
      "open" for opening a file,
      "directory" for selecting a directory,
      "save" for choosing a file to save.
    """
    def __init__(self, dialog_type="open", file_filter="All Files (*)", parent=None):
        super().__init__(parent)
        self.dialog_type = dialog_type
        self.file_filter = file_filter
        self.setReadOnly(True)
        if dialog_type == "open":
            self.setPlaceholderText("Click to select a file")
        elif dialog_type == "directory":
            self.setPlaceholderText("Click to select a directory")
        elif dialog_type == "save":
            self.setPlaceholderText("Click to select a file to save")
    
    def mousePressEvent(self, event):
        if self.dialog_type == "open":
            filename, _ = QFileDialog.getOpenFileName(self, "Select File", "", self.file_filter)
            if filename:
                self.setText(filename)
        elif self.dialog_type == "directory":
            directory = QFileDialog.getExistingDirectory(self, "Select Directory")
            if directory:
                self.setText(directory)
        elif self.dialog_type == "save":
            filename, _ = QFileDialog.getSaveFileName(self, "Save File As", "", self.file_filter)
            if filename:
                self.setText(filename)

class SplitWorker(QThread):
    progress_updated = pyqtSignal(int, str)
    finished = pyqtSignal()
    
    def __init__(self, input_file, chunk_size, output_prefix, destination):
        super().__init__()
        self.input_file = input_file
        self.chunk_size = chunk_size
        self.output_prefix = output_prefix
        self.destination = destination
        
    def run(self):
        if not os.path.exists(self.destination):
            os.makedirs(self.destination)
            
        # Get file size for progress tracking
        file_size = os.path.getsize(self.input_file)
        bytes_processed = 0
        
        with open(self.input_file, 'rb') as f:
            index = 0
            while True:
                chunk = f.read(self.chunk_size)
                if not chunk:
                    break
                filename = os.path.join(self.destination, f"{self.output_prefix}{index:04d}.part")
                with open(filename, 'wb') as chunk_file:
                    chunk_file.write(chunk)
                
                bytes_processed += len(chunk)
                progress = int((bytes_processed / file_size) * 100)
                self.progress_updated.emit(progress, f"Created {filename}")
                    
                index += 1
        
        self.progress_updated.emit(100, "Splitting complete.")
        self.finished.emit()

class JoinWorker(QThread):
    progress_updated = pyqtSignal(int, str)
    finished = pyqtSignal()
    
    def __init__(self, input_prefix, output_file, directory):
        super().__init__()
        self.input_prefix = input_prefix
        self.output_file = output_file
        self.directory = directory
        
    def run(self):
        # List and sort all files starting with the prefix
        parts = sorted([f for f in os.listdir(self.directory) if f.startswith(self.input_prefix)])
        if not parts:
            self.progress_updated.emit(0, "No files found with the given prefix in the specified directory.")
            self.finished.emit()
            return
        
        # Calculate total size for progress tracking
        total_size = sum(os.path.getsize(os.path.join(self.directory, part)) for part in parts)
        bytes_processed = 0
        
        with open(self.output_file, 'wb') as outfile:
            for i, part in enumerate(parts):
                part_path = os.path.join(self.directory, part)
                self.progress_updated.emit(int((i / len(parts)) * 100), f"Joining {part_path}...")
                
                with open(part_path, 'rb') as infile:
                    while True:
                        buffer = infile.read(1024 * 1024)  # Use a 1MB buffer for efficiency
                        if not buffer:
                            break
                        outfile.write(buffer)
                        bytes_processed += len(buffer)
                        progress = int((bytes_processed / total_size) * 100)
                        self.progress_updated.emit(progress, f"Processing {part}...")
        
        self.progress_updated.emit(100, f"All parts have been joined into {self.output_file}")
        self.finished.emit()

class ModernFileSplitterJoiner(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Modern File Splitter & Joiner")
        self.setMinimumSize(800, 600)
        #styling
        self.setStyleSheet("""
            QMainWindow, QWidget {
                background-color: #f5f5f7;
            }
            QPushButton {
                background-color: #0078d7;
                color: white;
                border: none;
                padding: 8px 16px;
                border-radius: 4px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #0063b1;
            }
            QPushButton:pressed {
                background-color: #004c8c;
            }
            QTabWidget::pane {
                border: 1px solid #cccccc;
                border-radius: 4px;
                background-color: white;
            }
            QTabBar::tab {
                background-color: #e1e1e1;
                padding: 8px 16px;
                margin-right: 2px;
                border-top-left-radius: 4px;
                border-top-right-radius: 4px;
            }
            QTabBar::tab:selected {
                background-color: white;
                border: 1px solid #cccccc;
                border-bottom-color: white;
            }
            QLineEdit, QComboBox, QSpinBox, QDoubleSpinBox {
                padding: 6px;
                border: 1px solid #cccccc;
                border-radius: 4px;
            }
            QGroupBox {
                border: 1px solid #cccccc;
                border-radius: 4px;
                margin-top: 12px;
                background-color: white;
            }
            QGroupBox::title {
                subcontrol-origin: margin;
                left: 10px;
                padding: 0 5px;
            }
            QTextEdit {
                border: 1px solid #cccccc;
                border-radius: 4px;
                background-color: white;
            }
            QProgressBar {
                border: 1px solid #cccccc;
                border-radius: 4px;
                text-align: center;
                height: 20px;
            }
            QProgressBar::chunk {
                background-color: #0078d7;
                width: 20px;
            }
        """)
        
        
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        main_layout = QVBoxLayout(central_widget)
        
        # Create tabs
        self.tab_widget = QTabWidget()
        main_layout.addWidget(self.tab_widget)
        
        # Create split tab
        self.split_tab = QWidget()
        self.tab_widget.addTab(self.split_tab, "Split File")
        self.setup_split_tab()
        
        # Create join tab
        self.join_tab = QWidget()
        self.tab_widget.addTab(self.join_tab, "Join Files")
        self.setup_join_tab()
        
        # Status area (common to both tabs)
        status_group = QGroupBox("Operation Status")
        main_layout.addWidget(status_group)
        status_layout = QVBoxLayout(status_group)
        
        self.progress_bar = QProgressBar()
        status_layout.addWidget(self.progress_bar)
        
        self.status_text = QTextEdit()
        self.status_text.setReadOnly(True)
        status_layout.addWidget(self.status_text)
        
        # Workers
        self.split_worker = None
        self.join_worker = None

    def setup_split_tab(self):
        layout = QVBoxLayout(self.split_tab)
        
        # Input File Selection (clickable field)
        input_group = QGroupBox("Input File")
        layout.addWidget(input_group)
        input_layout = QHBoxLayout(input_group)
        self.split_input_path = FileBrowserLineEdit(dialog_type="open", file_filter="All Files (*)")
        input_layout.addWidget(self.split_input_path)
        
        # Chunk Size Selection (Slider + SpinBox + Unit)
        chunk_group = QGroupBox("Chunk Size")
        layout.addWidget(chunk_group)
        chunk_layout = QHBoxLayout(chunk_group)
        
        # Slider for chunk size adjustment
        self.chunk_size_slider = QSlider(Qt.Horizontal)
        self.chunk_size_slider.setTickPosition(QSlider.TicksBelow)
        self.chunk_size_slider.setTickInterval(10)
        chunk_layout.addWidget(self.chunk_size_slider)
        
        # SpinBox to show/set the numeric value
        self.chunk_size_spinbox = QDoubleSpinBox()
        self.chunk_size_spinbox.setDecimals(1)
        chunk_layout.addWidget(self.chunk_size_spinbox)
        
        # Unit selection combo box
        self.chunk_size_unit = QComboBox()
        self.chunk_size_unit.addItems(["KB", "MB", "GB"])
        self.chunk_size_unit.setCurrentIndex(1)  # Default to MB
        chunk_layout.addWidget(self.chunk_size_unit)
        
        # Initialize ranges and values based on default unit ("MB")
        self.chunk_size_spinbox.setValue(10)
        self.update_chunk_size_range()
        self.chunk_size_slider.valueChanged.connect(self.on_slider_value_changed)
        self.chunk_size_spinbox.valueChanged.connect(self.on_spinbox_value_changed)
        self.chunk_size_unit.currentIndexChanged.connect(self.update_chunk_size_range)
        
        # Output Settings
        output_group = QGroupBox("Output Settings")
        layout.addWidget(output_group)
        output_layout = QFormLayout(output_group)
        # Output Directory (clickable field)
        self.split_output_dir = FileBrowserLineEdit(dialog_type="directory")
        output_layout.addRow("Output Directory:", self.split_output_dir)
        # Output Prefix
        self.output_prefix = QLineEdit("part_")
        output_layout.addRow("Output Prefix:", self.output_prefix)
        
        # Split Button (centered)
        split_btn_layout = QHBoxLayout()
        split_btn_layout.addStretch()
        self.split_btn =  QPushButton("Split File")
        self.split_btn.setMinimumWidth(150)
        self.split_btn.clicked.connect(self.start_split)
        split_btn_layout.addWidget(self.split_btn)
        split_btn_layout.addStretch()
        layout.addLayout(split_btn_layout)
        layout.addStretch()

    def setup_join_tab(self):
        layout = QVBoxLayout(self.join_tab)
        
        # Parts Directory Selection (clickable field)
        parts_group = QGroupBox("Parts Directory")
        layout.addWidget(parts_group)
        parts_layout = QHBoxLayout(parts_group)
        self.parts_dir = FileBrowserLineEdit(dialog_type="directory")
        self.parts_dir.textChanged.connect(self.update_default_join_output)
        parts_layout.addWidget(self.parts_dir)
        
        # Parts Prefix
        prefix_group = QGroupBox("Parts Prefix")
        layout.addWidget(prefix_group)
        prefix_layout = QHBoxLayout(prefix_group)
        self.parts_prefix = QLineEdit("part_")
        prefix_layout.addWidget(self.parts_prefix)
        
        # Output File Selection (clickable field)
        output_group = QGroupBox("Output File")
        layout.addWidget(output_group)
        output_layout = QHBoxLayout(output_group)
        self.join_output_path = FileBrowserLineEdit(dialog_type="save", file_filter="All Files (*)")
        output_layout.addWidget(self.join_output_path)
        
        # Join Button (centered)
        join_btn_layout = QHBoxLayout()
        join_btn_layout.addStretch()
        self.join_btn = QPushButton("Join Files")
        self.join_btn.setMinimumWidth(150)
        self.join_btn.clicked.connect(self.start_join)
        join_btn_layout.addWidget(self.join_btn)
        join_btn_layout.addStretch()
        layout.addLayout(join_btn_layout)
        layout.addStretch()
    
    def update_chunk_size_range(self):
        """
        Adjusts the slider and spinbox ranges based on the selected unit.
        """
        unit = self.chunk_size_unit.currentText()
        if unit == "KB":
            min_val = 1
            max_val = 10240  # e.g. up to 10MB in KB
        elif unit == "MB":
            min_val = 1
            max_val = 1024   # e.g. up to 1GB in MB
        elif unit == "GB":
            min_val = 0.1
            max_val = 10     # e.g. up to 10GB
        # Update spinbox range
        self.chunk_size_spinbox.blockSignals(True)
        self.chunk_size_spinbox.setMinimum(min_val)
        self.chunk_size_spinbox.setMaximum(max_val)
        # For slider, we work with integers; for "GB" we multiply values by 10
        self.chunk_size_slider.blockSignals(True)
        if unit == "GB":
            slider_min = int(min_val * 10)
            slider_max = int(max_val * 10)
            value = int(self.chunk_size_spinbox.value() * 10)
        else:
            slider_min = int(min_val)
            slider_max = int(max_val)
            value = int(self.chunk_size_spinbox.value())
        self.chunk_size_slider.setMinimum(slider_min)
        self.chunk_size_slider.setMaximum(slider_max)
        self.chunk_size_slider.setValue(value)
        self.chunk_size_slider.blockSignals(False)
        self.chunk_size_spinbox.blockSignals(False)
    def update_default_join_output(self, directory):
    # If the output file field is empty and a directory is selected,
    # set the output file to a default value within the selected directory.
        if directory and not self.join_output_path.text():
            default_filename = "joined_file"  # You can modify this default name as needed
            self.join_output_path.setText(os.path.join(directory, default_filename))

    def on_slider_value_changed(self, value):
        unit = self.chunk_size_unit.currentText()
        self.chunk_size_spinbox.blockSignals(True)
        if unit == "GB":
            self.chunk_size_spinbox.setValue(value / 10.0)
        else:
            self.chunk_size_spinbox.setValue(value)
        self.chunk_size_spinbox.blockSignals(False)
    
    def on_spinbox_value_changed(self, value):
        unit = self.chunk_size_unit.currentText()
        self.chunk_size_slider.blockSignals(True)
        if unit == "GB":
            self.chunk_size_slider.setValue(int(value * 10))
        else:
            self.chunk_size_slider.setValue(int(value))
        self.chunk_size_slider.blockSignals(False)
    def update_default_output_dir(self, filepath):
    
        if filepath and not self.split_output_dir.text():
            self.split_output_dir.setText(os.path.dirname(filepath))

    def get_chunk_size_string(self):
        value = self.chunk_size_spinbox.value()
        unit = self.chunk_size_unit.currentText()
        return f"{value}{unit}"
    
    def start_split(self):
        # Input file validation
        input_file = self.split_input_path.text()
        self.split_input_path.textChanged.connect(self.update_default_output_dir)
        if not input_file or not os.path.isfile(input_file):
            QMessageBox.critical(self, "Error", "Please select a valid input file")
            return
        
        try:
            chunk_size = parse_size(self.get_chunk_size_string())
            if chunk_size <= 0:
                raise ValueError("Chunk size must be positive")
        except ValueError as e:
            QMessageBox.critical(self, "Error", f"Invalid chunk size: {str(e)}")
            return
        
        output_dir = self.split_output_dir.text()
        if not output_dir:
            output_dir = os.path.dirname(input_file)
            self.split_output_dir.setText(output_dir)
        
        prefix = self.output_prefix.text()
        if not prefix:
            prefix = "part_"
            self.output_prefix.setText(prefix)
        
        # Clear status area
        self.status_text.clear()
        self.progress_bar.setValue(0)
        
        # Disable split button while processing
        self.split_btn.setEnabled(False)
        
        # Start the splitting worker thread
        self.split_worker = SplitWorker(input_file, chunk_size, prefix, output_dir)
        self.split_worker.progress_updated.connect(self.update_progress)
        self.split_worker.finished.connect(self.on_split_finished)
        self.split_worker.start()
    
    def on_split_finished(self):
        self.split_btn.setEnabled(True)
        self.split_worker = None
    
    def start_join(self):
        parts_dir = self.parts_dir.text()
        if not parts_dir or not os.path.isdir(parts_dir):
            QMessageBox.critical(self, "Error", "Please select a valid directory containing file parts")
            return
        
        prefix = self.parts_prefix.text()
        if not prefix:
            QMessageBox.critical(self, "Error", "Please enter a parts prefix")
            return
        
        output_file = self.join_output_path.text()
        if not output_file:
            QMessageBox.critical(self, "Error", "Please select an output file path")
            return
        
        # Check if parts exist
        parts = [f for f in os.listdir(parts_dir) if f.startswith(prefix)]
        if not parts:
            QMessageBox.critical(self, "Error", f"No files with prefix '{prefix}' found in the selected directory")
            return
        
        # Clear status area
        self.status_text.clear()
        self.progress_bar.setValue(0)
        
        # Disable join button while processing
        self.join_btn.setEnabled(False)
        
        # Start the joining worker thread
        self.join_worker = JoinWorker(prefix, output_file, parts_dir)
        self.join_worker.progress_updated.connect(self.update_progress)
        self.join_worker.finished.connect(self.on_join_finished)
        self.join_worker.start()
    
    def on_join_finished(self):
        self.join_btn.setEnabled(True)
        self.join_worker = None
    
    def update_progress(self, value, message):
        self.progress_bar.setValue(value)
        self.status_text.append(message)
        # Auto-scroll the status area to the bottom
        self.status_text.verticalScrollBar().setValue(
            self.status_text.verticalScrollBar().maximum()
        )

if __name__ == '__main__':  #Final
    app = QApplication(sys.argv)
    window = ModernFileSplitterJoiner()
    window.show()
    sys.exit(app.exec_())
