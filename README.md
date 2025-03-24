# ECM2434 Project - Bingo Sustainability Game

## Project Overview

This project is the **Sprint Two Final Submission of the Bingo Sustainability Game** developed by the **Caffeinated Divas Team** at **Exeter University**. It is a gamified experience aimed at promoting sustainability where players complete tasks to earn points and rewards. The application consists of a **Django backend** and a **React frontend**. Tasks are verified via **QR codes**, and there is a bonus points system for completing tasks within a set timeframe.

---

## Features

- **9 Task-Based Games:** Players complete challenges to earn stamps.
- **QR Code Verification:** Users scan QR codes to confirm task completion.
- **Bonus Points System:** Rewards for completing tasks in patterns.
- **Leaderboard:** Tracks top-scoring players.
- **User Authentication:** Secure login using JWT.

---

## Prerequisites

Ensure you have the following installed:
- Python (>= 3.8)
- pip (Python package manager)
- Node.js & npm
- Git
- Virtual Environment (Recommended for Python dependencies)

---

## Backend Setup (Django)

1. **Clone the Repository**
```bash
   git clone <your-repo-url>
   cd <your-project-folder>
```

2. **Set up a virtual environment:**
```bash
   python -m venv venv
   source venv/bin/activate  # Mac/Linux
   venv\Scripts\activate    # Windows
```

3. **Install dependencies:**
```bash
   pip install -r requirements.txt
```

4. **Apply migrations:**
```bash
   python manage.py makemigrations
   python manage.py migrate
```

5. **Run the server:**
```bash
   python manage.py runserver
```
   The backend will be running at: `http://localhost:8000/`

---

## Frontend Setup (React)

1. **Navigate to the frontend folder:**
```bash
   cd path/to/ECM2434_v2/bingo-frontend
```

2. **Install dependencies:**
```bash
   npm install
   npm install jsqr  # If required
```

3. **Run the React frontend:**
```bash
   npm start
```
   The frontend will be running at: `http://localhost:3000/`

---

## Stopping the Application

To stop both frontend and backend servers, run:
```bash
   pkill -f node
   pkill -f python
```

---

## Running Tests

### Backend Tests (Django)
```bash
   python manage.py test
```

### Frontend Tests (React)
```bash
   npm test
```

---

## Environment Variables (Optional)

Create a `.env` file in the project root and add:
```env
   SECRET_KEY=your_secret_key
   DEBUG=True
   DATABASE_URL=your_database_url
```

---

## Deployment Guide (Optional)
For production deployment on Heroku, AWS, or DigitalOcean:
- Use **Gunicorn** instead of the Django development server.
- Set up a **PostgreSQL database** for production.
- Configure **whitenoise** for static file handling.

---

## Common Issues & Troubleshooting

- **Virtual Environment Issues:**
   ```bash
   python -m pip install --upgrade pip
   ```

- **Database Issues:**
   ```bash
   python manage.py flush
   ```

---

## Contributing

1. Fork the repository.
2. Create a feature branch (`git checkout -b feature-xyz`).
3. Commit your changes (`git commit -m "Added feature XYZ"`).
4. Push the branch (`git push origin feature-xyz`).
5. Create a pull request for review.

---

## License

This project is part of an academic submission for **Sprint Two Final Submission of the Bingo Sustainability Game** by the **Caffeinated Divas Team at Exeter University**. It is licensed under the **MIT License**, but certain restrictions may apply based on academic guidelines. Contact the team for further details.

---

## Contact

For questions or contributions, contact the Caffeinated Divas Team at:
**lyt202@exeter.ac.uk, wllt201@exeter.ac.uk, mk811@exeter.ac.uk, ncm206@exeter.ac.uk, stl214@exeter.ac.uk, sc1332@exeter.ac.uk, lc1025@exeter.ac.uk**.

