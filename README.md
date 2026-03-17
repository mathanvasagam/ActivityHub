# ActivityHub 🚀

A Django-powered application for managing LinkedIn activities, content organization, and team collaboration.

## Features

- 🔐 **Dual Authentication**: Firebase + Django fallback for flexible login
- 📊 **Organization Dashboard**: Manage posts, projects, blogs, and research papers
- 💾 **Export Data**: Download posts/projects as CSV or XLSX
- 🐳 **Docker Ready**: Production-ready Docker image included
- 👥 **Admin Management**: Easy user role management
- 📱 **Responsive Design**: Mobile-friendly interface

## Quick Start

### Local Development

**Prerequisites:**
- Python 3.10+
- pip / venv

**Setup:**

```bash
# Clone repository
git clone https://github.com/mathanvasagam/ActivityHub.git
cd ActivityHub

# Create virtual environment
python -m venv .venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Run migrations
python manage.py migrate

# Create superuser (admin account)
python manage.py createsuperuser

# Start development server
python manage.py runserver 127.0.0.1:8000
```

Open: `http://127.0.0.1:8000`

### Docker Deployment

**Build image:**
```bash
docker build -t activityhub:latest .
```

**Run container:**
```bash
# Create .env file first (see Configuration section below)
docker run --env-file .env -p 8000:8000 activityhub:latest
```

Access: `http://localhost:8000`

### Docker Hub (Easy Sharing)

**Pull and run:**
```bash
docker run --env-file .env -p 8000:8000 mathanvasagam/activityhub:latest
```

## Configuration

Create a `.env` file in the project root:

```
DEBUG=true
SECRET_KEY=your-secret-key-here
ALLOWED_HOSTS=localhost,127.0.0.1
DATABASE_URL=sqlite:///db.sqlite3

# Firebase (optional)
FIREBASE_API_KEY=your-firebase-key
FIREBASE_AUTH_DOMAIN=your-firebase-domain
FIREBASE_PROJECT_ID=your-firebase-project-id
FIREBASE_STORAGE_BUCKET=your-firebase-bucket
FIREBASE_MESSAGING_SENDER_ID=your-firebase-sender-id
FIREBASE_APP_ID=your-firebase-app-id
```

## Admin Management

See [RUN.md](RUN.md) for detailed admin operations:
- Create new admins
- Promote/demote existing users
- Delete admin accounts

## Project Structure

```
├── accounts/           # User authentication & profile
├── searcher/          # Main app (posts, projects, blogs, research)
├── social_hub/        # Django settings & configuration
├── static/            # CSS, JS, images
├── templates/         # HTML templates
├── Dockerfile         # Production image
├── requirements.txt   # Python dependencies
└── manage.py          # Django management
```

## Database Models

- **User**: Django auth with Firebase integration
- **UserProfile**: Social hub user details
- **LinkedinPost**: LinkedIn posts tracking
- **Project**: Project management
- **BlogPost**: Blog content
- **ResearchPaper**: Research documentation

## Export Endpoints

- `GET /search/organization/export/posts/csv` - Export posts as CSV
- `GET /search/organization/export/posts/xlsx` - Export posts as XLSX
- `GET /search/organization/export/projects/csv` - Export projects as CSV
- `GET /search/organization/export/projects/xlsx` - Export projects as XLSX

## Testing

```bash
python manage.py test
```

## Requirements

See [requirements.txt](requirements.txt):
- Django 5.0+
- Firebase Admin SDK
- BeautifulSoup4 (web scraping)
- Pillow (image handling)
- openpyxl (Excel export)
- Gunicorn (production server)

## Production Checklist

Before deploying to production:

- [ ] Set `DEBUG=false` in `.env`
- [ ] Generate strong `SECRET_KEY` (50+ random characters)
- [ ] Configure HTTPS/SSL (reverse proxy or load balancer)
- [ ] Use PostgreSQL instead of SQLite
- [ ] Store `.env` securely (use Docker secrets or CI/CD environment variables)
- [ ] Set up proper logging and monitoring
- [ ] Configure `ALLOWED_HOSTS` for your domain
- [ ] Enable `SECURE_SSL_REDIRECT`, `SESSION_COOKIE_SECURE`, `CSRF_COOKIE_SECURE`

## Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit changes (`git commit -m 'Add amazing feature'`)
4. Push to branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## License

This project is open source and available under the MIT License.

## Author

**Mathan** - [GitHub](https://github.com/mathanvasagam)

## Support

For issues, questions, or suggestions, please open an [Issue](https://github.com/mathanvasagam/ActivityHub/issues) on GitHub.

---

**Happy coding! 🎉**
