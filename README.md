Step 1: Clone and Setup

Clone the repository
git clone repository-url
cd JobRec

Create virtual environment
python -m venv venv

Activate virtual environment
Windows:
venv\Scripts\activate
macOS/Linux:
source venv/bin/activate

Install dependencies
pip install -r requirements.txt

Navigate to Django project
cd jobox

Step 2: Run the Application

Run database migrations
python manage.py migrate

Create admin user (optional)
python manage.py createsuperuser

Start the server
python manage.py runserver

Database Setup

For MySQL (production):
1. Install MySQL Server
2. Create database: CREATE DATABASE jobox;
3. Update settings in jobox/jobox/settings.py

Step 3: Access the Application

Main Site: http://localhost:8000
