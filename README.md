# NMT Engineering & Services Dashboard

A full-stack dashboard application for managing company data, built with Django (backend) and Next.js (frontend).

## Features

- 📊 Real-time data visualization with charts and graphs
- � Advanced filtering (Country-State-City hierarchy, Industry Type, Products)
- 📝 Remark management system with 8 stages
- 🔐 JWT-based authentication
- ☁️ Google Sheets integration for live data
- 🗄️ PostgreSQL database
- 📱 Responsive design

## Tech Stack

### Backend
- Django 6.0.2
- Django REST Framework
- PostgreSQL
- Google Sheets API
- JWT Authentication

### Frontend
- Next.js 15
- React 19
- TypeScript
- Tailwind CSS
- Recharts for data visualization

## Setup Instructions

### Prerequisites
- Python 3.11+
- Node.js 18+
- PostgreSQL 18
- Google Cloud Service Account (for Google Sheets)

### Backend Setup

1. Navigate to backend directory:
```bash
cd backend
```

2. Create virtual environment:
```bash
python -m venv venv
venv\Scripts\activate  # Windows
```

3. Install dependencies:
```bash
pip install -r requirements.txt
```

4. Configure environment variables in `backend/.env`:
```env
DEBUG=True
SECRET_KEY=your-secret-key

# PostgreSQL
DB_NAME=nmt_dashboard
DB_USER=postgres
DB_PASSWORD=your-password
DB_HOST=localhost
DB_PORT=5432

# Google Sheets
USE_GOOGLE_SHEETS=True
GOOGLE_SHEET_URL=your-google-sheet-url

# Google Service Account Credentials
GOOGLE_TYPE=service_account
GOOGLE_PROJECT_ID=your-project-id
GOOGLE_PRIVATE_KEY_ID=your-private-key-id
GOOGLE_PRIVATE_KEY="-----BEGIN PRIVATE KEY-----\nYOUR_KEY\n-----END PRIVATE KEY-----\n"
GOOGLE_CLIENT_EMAIL=your-service-account@project.iam.gserviceaccount.com
GOOGLE_CLIENT_ID=your-client-id
```

**Note:** Copy `backend/.env.example` to `backend/.env` and fill in your credentials.

5. Share your Google Sheet with the service account email (GOOGLE_CLIENT_EMAIL)

6. Run migrations:
```bash
python manage.py migrate
python manage.py createsuperuser
```

7. Start server:
```bash
python manage.py runserver 8000
```

### Frontend Setup

1. Navigate to frontend directory:
```bash
cd frontend
```

2. Install dependencies:
```bash
npm install
```

3. Configure environment in `frontend/.env.local`:
```env
NEXT_PUBLIC_API_URL=http://localhost:8000
```

4. Start development server:
```bash
npm run dev
```

5. Open browser: http://localhost:3000

## Default Credentials

- Username: `admin`
- Password: `admin@5213`

## Project Structure

```
├── backend/
│   ├── config/          # Django settings
│   ├── dashboard/       # Main app
│   ├── core/           # Middleware & permissions
│   └── requirements.txt
├── frontend/
│   ├── src/
│   │   ├── app/        # Next.js pages
│   │   ├── components/ # React components
│   │   └── lib/        # Utilities
│   └── package.json
└── README.md
```

## API Endpoints

- `POST /api/auth/login/` - User login
- `POST /api/auth/logout/` - User logout
- `GET /api/dashboard/data/` - Get dashboard data
- `GET /api/dashboard/stats/` - Get statistics
- `POST /api/dashboard/update_remark/` - Update remark

## License

Proprietary - NMT Engineering & Services Pvt. Ltd.
