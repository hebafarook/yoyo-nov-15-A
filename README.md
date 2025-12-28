# ⚽ Yo-Yo Elite Soccer Player AI Coach

A comprehensive AI-powered soccer training and assessment platform designed to help elite youth soccer players reach their full potential through personalized training programs, performance tracking, and professional coaching insights.

## 🚀 Quick Start

### Prerequisites
- Python 3.9+
- Node.js 16+
- MongoDB
- Yarn package manager

### Installation

```bash
# Backend setup
cd backend
pip install -r requirements.txt

# Frontend setup
cd frontend
yarn install
```

### Running the Application

```bash
# Start backend (development)
cd backend
uvicorn server:app --reload --port 8001

# Start frontend (development)
cd frontend
yarn start
```

### Production Deployment
See [docs/deploy.md](docs/deploy.md) for deployment instructions.

## 📁 Project Structure

```
/app/
├── backend/           # FastAPI backend
│   ├── routes/       # API endpoints
│   ├── models.py     # Data models
│   ├── server.py     # Main application
│   └── exercise_database.py  # Training exercises
├── frontend/         # React frontend
│   ├── src/
│   │   ├── components/  # React components
│   │   ├── contexts/    # React contexts
│   │   └── i18n/        # Internationalization
│   └── public/
├── tests/            # Automated tests (pytest)
├── scripts/          # Manual test scripts & utilities
├── docs/             # Documentation
├── pytest.ini        # Test configuration
└── README.md         # This file
```

## 📚 Documentation

All documentation is in the [`docs/`](docs/) directory:

- **[docs/README.md](docs/README.md)** - Documentation index
- **[docs/CODE_DOCUMENTATION.md](docs/CODE_DOCUMENTATION.md)** - Technical architecture
- **[docs/TRAINING_DATABASE_DOCUMENTATION.md](docs/TRAINING_DATABASE_DOCUMENTATION.md)** - Exercise library
- **[docs/CLUB_PORTAL_SYSTEM.md](docs/CLUB_PORTAL_SYSTEM.md)** - Club management
- **[docs/deploy.md](docs/deploy.md)** - Deployment guide

## 🧪 Testing

### Automated Tests
```bash
# Run all tests
pytest

# Run with coverage
pytest --cov=backend --cov-report=html

# Run specific test categories
pytest -m unit          # Unit tests only
pytest -m integration   # Integration tests
pytest -m backend       # Backend tests
```

See [tests/README.md](tests/README.md) for more details.

### Manual Testing Scripts
Manual test scripts and debugging utilities are in [`scripts/`](scripts/). These are for exploration and debugging, not automated CI/CD.

```bash
cd scripts
python ai_coach_backend_test.py
```

See [scripts/README.md](scripts/README.md) for available scripts.

## 🌟 Key Features

### For Players
- **Personalized Assessments** - Comprehensive physical, technical, tactical, and psychological evaluation
- **AI-Generated Training Programs** - Customized training plans based on assessment data
- **Progress Tracking** - Monitor improvement over time with detailed analytics
- **Professional Reports** - Comprehensive performance reports with actionable insights

### For Coaches
- **Player Management** - Track multiple players and their progress
- **Training Plan Templates** - Access pre-built training programs
- **Performance Analytics** - Detailed insights into player development

### For Clubs
- **Team Management** - Manage multiple teams and rosters
- **Club-Wide Analytics** - Aggregate performance data across all players
- **Safety Monitoring** - Track training load and injury prevention

### For Parents
- **Progress Visibility** - Monitor child's development
- **Communication Hub** - Stay connected with coaches
- **Report Access** - View detailed performance reports

## 🛠️ Technology Stack

### Backend
- **FastAPI** - Modern Python web framework
- **MongoDB** - NoSQL database with Motor async driver
- **Pydantic** - Data validation
- **JWT** - Authentication
- **Emergent Integrations** - AI/LLM integration (GPT-4o-mini, Claude, Gemini)

### Frontend
- **React** - UI framework
- **Tailwind CSS** - Styling
- **Shadcn UI** - Component library
- **i18next** - Internationalization (English & Arabic with RTL support)
- **Axios** - HTTP client
- **React Router** - Navigation

### AI/ML
- **LLM Integration** - GPT-4o-mini for insights and program generation
- **Predictive Models** - Performance forecasting
- **Personalization Engine** - Adaptive training recommendations

## 🌍 Internationalization

The platform fully supports:
- 🇺🇸 English
- 🇸🇦 Arabic (with RTL layout support)

## 🔐 Authentication & Authorization

Role-based access control (RBAC):
- **Player** - Personal dashboard, assessments, training
- **Coach** - Player management, program creation
- **Parent** - View child's progress
- **Club Admin** - Club-wide management
- **System Admin** - User management

## 📊 API Documentation

API documentation is available at:
- Development: `http://localhost:8001/docs` (Swagger UI)
- Development: `http://localhost:8001/redoc` (ReDoc)

## 🤝 Contributing

### Development Workflow
1. Create feature branch
2. Make changes
3. Write tests
4. Run tests: `pytest`
5. Run linting: `ruff check .`
6. Submit pull request

### Code Style
- Python: Follow PEP 8, use `ruff` for linting
- JavaScript: Follow Airbnb style guide, use ESLint
- Commits: Use conventional commits format

## 📝 License

Proprietary - All rights reserved

## 📧 Support

For issues and questions:
- Create an issue in the repository
- Contact: support@yoyoelitesoccer.com

## 🙏 Acknowledgments

Built with emergent.ai development platform
