# train-station-api
API for train station service
With our service you can manage trains and their types, stations and routes, 
crew and journeys, tickets and orders.
For you available detailed information about crew members, journeys and routes.
You could easily find needed journey searching by station or train.
Modern authentication via JWT.
Creation of orders and tickets available for all registered users.
API has convenient documentation provided by drf_spectacular and Swagger.
Optimised database queries.

Setup
Create and activate a virtual environment (Python3) using your preferred method. 
This functionality is built into Python, if you do not have a preference.

From the command line, type:

git clone https://github.com/N1khto/train-station-api.git
pip install -r requirements.txt
python manage.py migrate
python manage.py createsuperuser 
python manage.py runserver
