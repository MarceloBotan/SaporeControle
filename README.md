# SaporeControle

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


Copy code
git clone https://github.com/your-username/SaporeControle.git
Navigate to the project directory:

Copy code
cd SaporeControle
Create a virtual environment to isolate dependencies:

Copy code
python -m venv env
Activate the virtual environment:

On Linux/macOS:
Copy code
source env/bin/activate

On Windows (PowerShell):
Copy code
.\env\Scripts\Activate.ps1

Install the project dependencies:
Copy code
pip install -r requirements.txt

Run the database migrations:
Copy code
python manage.py migrate

