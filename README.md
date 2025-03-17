# resume-coach-app

This repository contains the code to run a Resume Coach Application. The application leverages machine learning models to analyze job descriptions and resumes, calculate similarity scores, and provide suggestions. This README provides step-by-step instructions to set up the environment, install required dependencies, and run the application on both Windows and Mac systems.

## Table of Contents
- [Prerequisites](#prerequisites)
- [Installation](#installation)
- [Setting Up a Virtual Environment](#setting-up-a-virtual-environment)
  - [Using `virtualenv`](#using-virtualenv)
  - [Using `venv`](#using-venv)
- [Installing Dependencies](#installing-dependencies)
- [Running the Application](#running-the-application)
- [Adding Paths for Poppler and Tesseract in Python](#adding-paths-for-poppler-and-tesseract-in-python)
- [Troubleshooting](#troubleshooting)

## Prerequisites
Before running the application, you need to install the following dependencies on your system:

1. **Python 3.10**: Ensure that Python is installed and accessible from the command line.
2. **pip**: Ensure that pip is installed for managing Python packages.

### Local Setup
```
python -m venv venv

source venv/bin/activate

pip install -r requirements.txt 

```

### Run app
```
streamlit run resume_coach.py
```

## Installation

### Installing Poppler

1. Install Poppler via Homebrew:
    ```bash
    brew install poppler
    ```

### Installing Tesseract

#### **Mac**
1. Install Tesseract via Homebrew:
    ```bash
    brew install tesseract
    ```

## Setting Up a Virtual Environment

It is recommended to use a virtual environment to manage dependencies for the project.

### Using `virtualenv`

#### **Windows**

`pip install virtualenv`

`virtualenv venv`

`.\venv\Scripts\activate`

#### **Mac/Linux**

`pip install virtualenv`

`virtualenv venv`

`source venv/bin/activate`

### For Linux/Mac:
Open a terminal.

Change the directory to the desired location for your project:

`cd /path/to/project`

Create a new virtual environment using the venv module:

`python3.10 -m venv venv`


Activate the virtual environment:
`source myenv/bin/activate`

Install the project requirements using pip:
`pip install -r requirements.txt`

These instructions assume you have Python 3.10.4 installed and added to your system's PATH variable.

### Execution Instructions if Multiple Python Versions Installed

If you have multiple Python versions installed on your system, you can use the Python Launcher to create a virtual environment with Python 3.10.4. Specify the version using the -p or --python flag. Follow the instructions below:

For donkey at hte farm Windows:
Open the Command Prompt by pressing Win + R, typing "cmd", and pressing Enter.

Change the directory to the desired location for your project:

`cd C:\path\to\project`

Create a new virtual environment using the Python Launcher:

`py -3.10 -m venv myenv`

Note: Replace myenv with your desired virtual environment name.

Activate the virtual environment:


`myenv\Scripts\activate`


Install the project requirements using pip:

`pip install -r requirements.txt`


### For Linux/Mac:
Open a terminal.

Change the directory to the desired location for your project:

`cd /path/to/project`

Create a new virtual environment using the Python Launcher:


`python3.10 -m venv myenv`


Note: Replace myenv with your desired virtual environment name.

Activate the virtual environment:

`source myenv/bin/activate`


Install the project requirements using pip:

`pip install -r requirements.txt`


By specifying the version using py -3.10 or python3.10, you can ensure that the virtual environment is created using Python 3.10.4 specifically, even if you have other Python versions installed.


To run the streamlit app

Add OpenAI API Key in Constants
`
streamlit run src/resume_suggestions.py
`

This will start a local web server and open the application in your default web browser.

Adding Paths for Poppler and Tesseract in Python
If you encounter issues with Tesseract or Poppler not being detected, you can manually specify the paths in your Python code:

For Tesseract

`import pytesseract`

`pytesseract.pytesseract.tesseract_cmd = r'C:\Program Files\Tesseract-OCR\tesseract.exe`  



# On Mac, this step is usually unnecessary if installed via Homebrew.
For Poppler

`from pdf2image import convert_from_path`

`images = convert_from_path('your_pdf_file.pdf', poppler_path=r'C:\path\to\poppler\bin') ` # Windows





