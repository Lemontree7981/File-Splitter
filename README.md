Modern File Splitter & Joiner
A cross-platform, GUI-based tool for splitting large files into smaller parts and joining them back together using Python and PyQt5.


(Replace screenshot.png with your actual screenshot file)

Features
Split Files: Divide any file into multiple parts with a customizable chunk size.
Join Files: Seamlessly reassemble previously split file parts.
Modern UI: Clean and modern interface built with PyQt5.
Cross-Platform: Works on Windows, macOS, and Linux.
Real-Time Feedback: Interactive progress bar and status updates during operations.
Prerequisites
Python 3.6+
PyQt5
Installation
Clone the Repository:

bash
Copy
Edit
git clone https://github.com/yourusername/modern-file-splitter-joiner.git
cd modern-file-splitter-joiner
Create and Activate a Virtual Environment (Optional but Recommended):

bash
Copy
Edit
python3 -m venv venv
source venv/bin/activate  # On Windows use: venv\Scripts\activate
Install Dependencies:

bash
Copy
Edit
pip install PyQt5
Usage
Run the Application:

bash
Copy
Edit
python3 file_splitter.py
Using the Interface:

Split File Tab:

Click the input field to select a file.
Choose a chunk size using the slider or spinbox (with unit selection).
Select an output directory and set a prefix for the parts.
Click "Split File" to begin splitting.
Join Files Tab:

Select the directory containing file parts.
Specify the prefix of the parts (e.g., part_).
Choose an output file location.
Click "Join Files" to reassemble the file.
Progress and Status:

A progress bar and status messages will update in real-time during the split or join operations.
How It Works
The application utilizes multithreading with PyQt5's QThread to handle file splitting and joining in the background. This keeps the user interface responsive during long-running operations.

SplitWorker: Reads the input file in chunks and writes each part to the specified output directory.
JoinWorker: Reads all file parts with the given prefix, then concatenates them into a single output file.
Contributing
Contributions are welcome! Feel free to open issues or submit pull requests if you have ideas for improvements or bug fixes.

Fork the repository.
Create a new branch (git checkout -b feature/YourFeature).
Commit your changes.
Push to your fork.
Open a pull request.
License
This project is licensed under the MIT License.
