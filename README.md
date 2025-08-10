# Keil Builder - Automated Keil Build Tool

[![Python](https://img.shields.io/badge/Python-3.7+-blue.svg)](https://www.python.org/)
[![License](https://img.shields.io/badge/License-MIT-green.svg)](LICENSE)
[![Platform](https://img.shields.io/badge/Platform-Windows-lightgrey.svg)](https://www.microsoft.com/windows)

A script for automating Keil project builds, supporting multi-core parallelism, real-time output, and automatic project detection.

## Features

- Automatically detects Keil project files in the current directory
- Supports multi-core parallel builds
- Real-time display of build output
- Automatically copies generated hex/bin files to the current directory
- Command-line arguments to configure build options
- Generates a build log

## System Requirements

- Windows 7 or later
- Python 3.7 or later
- Keil μVision 4/5
- `.uvprojx` or `.uvproj` project files

## Quick Start

### Installation

1. Clone the repository:

   ```bash
   git clone https://github.com/Elsa-is-My-Muse/keil_builder.git
   cd keil_builder
   ```

2. (Optional) Create and activate a virtual environment:

   ```bash
   python -m venv venv
   venv\Scripts\activate
   ```

3. Install dependencies (no third-party dependencies required; works with Python 3.7+ standard library)

### Usage

1. Place `keil_builder.py` in the root directory of your Keil project (or clone this repository into your project directory).

2. Open a command prompt, navigate to your project directory, and run:

   ```bash
   python keil_builder.py
   ```

   By default, the script will automatically detect `.uvprojx` or `.uvproj` files in the current directory and build them.

#### Common Command-Line Arguments

- Specify a project file:

  ```bash
  python keil_builder.py your_project.uvprojx
  ```

- Specify a build target:

  ```bash
  python keil_builder.py your_project.uvprojx YourTargetName
  ```

- Specify the number of parallel build jobs (e.g., 4 cores):

  ```bash
  python keil_builder.py -j4
  ```

- Show help:

  ```bash
  python keil_builder.py -h
  ```

### Build Output

- The build log will be saved to `keil_builder.log`.
- Generated `.hex` and `.bin` files will be automatically copied to the current directory.

## License

This project is open-sourced under the MIT License. See [LICENSE](LICENSE) for details.
