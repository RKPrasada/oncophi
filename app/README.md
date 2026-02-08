# CervixAI

AI-Powered Cervical Cancer Screening Platform

## Features

- 🔬 **AI-Driven Triage**: Automated analysis of Pap smear and colposcopy images
- 🎯 **Explainable AI**: Heatmap overlays showing areas of concern
- 👨‍⚕️ **Human Oversight**: Mandatory clinician review before final diagnosis
- 📋 **Episode-Based Monitoring**: Longitudinal patient tracking
- 🔒 **Compliance**: HIPAA/GDPR audit logging

## Quick Start

### Prerequisites

- Python 3.9+
- pip

### Installation

```bash
cd app

# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt
```

### Running the Application

**1. Start the Backend API:**

```bash
cd app
uvicorn app.main:app --reload --port 8000
```

**2. Start the Frontend (in a new terminal):**

```bash
cd app
streamlit run ui/main.py
```

**3. Access the application:**

- API Docs: http://localhost:8000/docs
- Frontend: http://localhost:8501

## Workflow

1. **Register** a user account (physician, pathologist, etc.)
2. **Add patients** and obtain consent
3. **Create screening** episodes
4. **Upload images** (Pap smear, colposcopy)
5. **Run AI analysis** - get initial triage
6. **Clinician review** - finalize diagnosis

## API Endpoints

| Endpoint | Description |
|----------|-------------|
| `POST /api/v1/auth/register` | Register new user |
| `POST /api/v1/auth/login` | Login |
| `GET /api/v1/patients` | List patients |
| `POST /api/v1/patients` | Create patient |
| `POST /api/v1/screenings` | Create screening |
| `POST /api/v1/images/upload/{screening_id}` | Upload image |
| `POST /api/v1/diagnoses/analyze` | Run AI analysis |
| `POST /api/v1/diagnoses/review` | Submit clinician review |

## Docker Deployment

```bash
cd app
docker-compose up --build
```

## Tech Stack

- **Backend**: FastAPI, SQLAlchemy, Pydantic
- **Frontend**: Streamlit
- **Database**: SQLite (dev) / PostgreSQL (prod)
- **Auth**: JWT with OAuth2
