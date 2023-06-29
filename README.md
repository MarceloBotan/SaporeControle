# SaporeControle

[![Django CI](https://github.com/MarceloBotan/SaporeControle/actions/workflows/django.yml/badge.svg)](https://github.com/MarceloBotan/SaporeControle/actions/workflows/django.yml)

![image](https://github.com/MarceloBotan/SaporeControle/assets/128054032/410ef42f-94a1-4bbc-98fa-e44882f1f8c9)

SaporeControle is a Python application built with the Django framework to manage the inventory of assets in a company. It provides a web interface for asset management and includes features to add, edit, and delete SQL charts.

#Features

![image](https://github.com/MarceloBotan/SaporeControle/assets/128054032/df1a2615-65b8-4037-93a2-5f3614bd77de)

Add a new asset to the system, including information such as name, status and more information.
Update the information of an existing asset.
Remove an asset from the system.
View a list of all assets, including their detailed information.

#Installation

Clone this repository to your local machine:
```bash
git clone https://github.com/your-username/SaporeControle.git
```

Navigate to the project directory:
```bash
cd SaporeControle
```

Create a virtual environment to isolate dependencies:
```bash
python -m venv env
```

Activate the virtual environment:

On Linux/macOS:
```bash
source env/bin/activate
```

On Windows (PowerShell):
```bash
.\env\Scripts\Activate.ps1
```

Install the project dependencies:
```bash
pip install -r requirements.txt
```

Run the database migrations:
```bash
python manage.py migrate
```
