Step 1: Clone and Setup

Clone the repository
git clone repository-url
cd mlmp-applicanttracking

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


Start the server
python manage.py runserver


Step 3 - Access the Application

Main Site: http://localhost:8000
