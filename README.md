Our Draft Game overview
We decided to play BINGO, a gamified challenge where players complete tasks to earn points and rewards.

Game Structure 
-There are 9 games (details attached below).
-When a user completes a task, it turns into a stamp, and they earn points.
-Each game is worth a set number of points and requires either visiting a location or uploading a picture.
-For location-based tasks, players must scan a QR code to verify they have been there.
-Players can earn bonus points for completing tasks in a specific pattern (explanation attached below).
-The game has a time limit of one month.

Bonouspoints for early completion 
Players who complete all 9 games within:
⁠Week 1 earn an extra 40 points
⁠Week 2 earn an extra 30 points
⁠Week 3 earn an extra 20 points
⁠Week 4 earn an extra 10 points\

Rewards
The top three players with the highest scores will receive rewards like gift cards

Prototype Overview 
This prototype is a Djangopbased web application designed to provide an interactive and engaing through a combination of user authentication, gameificationa dn location based features. Players can sign up and log in securely to access their personalized dashboard, where they can participate in nine challenges or tasks and track their progress on a leaderboard.  The application also incorporates scanner functionality, allowing users to interact with specific challenges tied to four places. Additionally, a QR code generation feature can be utilized for enhanced user interactions. The backend is built using the Django REST Framework (DRF) to create a scalable and efficient API, enabling seamless communication between the front end and back end.

Current Features that sprint 1 has 
User regirstration and login
user profile
bingo board and leaderbaord(not fully function)
admin pannel at the backend 

Tech Stack
Backend: Django, Django REST Framework (DRF)
Database: SQLite/PostgreSQL
Authentication: Django Authentication
Other Tools: QR Code Generation, Django Admin

Instructions for installation and setup 
✅ Python 3.x – Download and install from Python.org
✅ Git – Download and install from Git website
✅ Virtual Environment – A Python environment manager for dependency isolation

Clone the Repository 
Install Dependencies 
- pip install -r requirements.txt
how to run the  web server 
- Start frontend/ backend 
  Go to your Django project folder
  To activate virtual environment
  source venv/bin/activate (Mac/Linux)
  venv/Scripts/activate  (Windows)
  run

- Start Django backend
  run
  pip install -r requirements.txt
  npm install jsqr
  python manage.py makemigrations
  python manage.py migrate
  python manage.py runserver

- Start Django frontend
  run
  cd bingo-frontend
  npm install
  npm start


  
  

  


