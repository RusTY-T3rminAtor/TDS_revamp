# LLM Analysis Quiz Project

Automated quiz-solving system for TDS Project 2 that handles data sourcing, preparation, analysis, and visualization using LLMs.

## 🚀 Quick Start

### Prerequisites
- Python 3.8+
- Google Chrome browser (for headless browsing)
- OpenAI API key

### Installation

1. **Clone the repository** (or you're already here!)

2. **Install dependencies:**
```bash
pip install -r requirements.txt
```
Or use the setup script:
```bash
python setup.py
```

3. **Configure environment variables:**

Edit the `.env` file with your credentials:
```env
STUDENT_EMAIL=your-email@example.com
SECRET_KEY=your-secret-string
OPENAI_API_KEY=sk-your-openai-api-key
PORT=5000
DEBUG=True
```

4. **Run the server:**
```bash
python app.py
```
Or on Windows:
```bash
run.bat
```

Server starts at: `http://localhost:5000`

### Testing

In a new terminal, test your endpoint:
```bash
python test_endpoint.py
```

## 📋 Features

- ✅ Flask REST API with authentication
- ✅ Headless Chrome browser for JavaScript-rendered pages
- ✅ OpenAI GPT-4o-mini integration for intelligent quiz solving
- ✅ Comprehensive data processing (CSV, Excel, PDF, web scraping)
- ✅ Automated answer submission with retry logic
- ✅ Quiz chain handling (multiple sequential quizzes)
- ✅ Time-limit enforcement (3 minutes per quiz chain)
- ✅ Detailed logging for debugging

## 🏗️ Architecture

```
Quiz Request → Flask API → Browser Fetch → LLM Analysis
                                ↓
                    Data Processing ← Download Files
                                ↓
                    LLM Solution → Extract Answer
                                ↓
                    Submit Answer → Handle Response
                                ↓
                    Next Quiz URL? → Repeat or End
```

## 📁 Project Structure

```
TDS_1/
├── app.py                  # Flask API server
├── quiz_solver.py          # Main quiz solving logic
├── browser_handler.py      # Headless Chrome management
├── llm_handler.py          # OpenAI GPT integration
├── data_processor.py       # Data processing & analysis
├── prompts.py              # System/user prompts for form
├── config.py               # Configuration management
├── render.yaml             # Settings for render
├── requirements.txt        # Python dependencies
├── LICENSE                 # MIT License
├── README.md               # This file
└── DEVELOPMENT.md          # Development & debugging guide
```

## 🔧 Configuration

### Environment Variables

| Variable | Description | Example |
|----------|-------------|---------|
| `STUDENT_EMAIL` | Your student email | `student@example.com` |
| `SECRET_KEY` | Secret for authentication | `my-secret-key-123` |
| `OPENAI_API_KEY` | OpenAI API key | `sk-...` |
| `PORT` | Server port | `5000` |
| `DEBUG` | Debug mode | `True` / `False` |

### System and User Prompts

Located in `prompts.py`:
- **System Prompt** (88 chars): Protects the code word
- **User Prompt** (93 chars): Extracts the code word

Both are within the 100-character limit required by the Google Form.

## 🧪 API Endpoints

### `POST /quiz`
Receives quiz tasks and solves them.

**Request:**
```json
{
  "email": "your-email@example.com",
  "secret": "your-secret",
  "url": "https://example.com/quiz-123"
}
```

**Responses:**
- `200`: Quiz accepted and solving started
- `400`: Invalid JSON or missing fields
- `403`: Invalid secret

### `GET /health`
Health check endpoint.

**Response:**
```json
{
  "status": "healthy"
}
```

## 📊 How It Works

1. **Receive Request**: Flask endpoint validates email and secret
2. **Fetch Quiz**: Headless Chrome renders JavaScript and extracts content
3. **Analyze Task**: LLM parses quiz and identifies requirements
4. **Process Data**: Downloads files, scrapes web pages, parses PDFs
5. **Solve Task**: LLM performs calculations/analysis
6. **Extract Answer**: Formats answer in required format
7. **Submit**: Posts answer to specified endpoint
8. **Chain Handling**: If new URL provided, repeats process

## 🎯 Supported Quiz Types

- ✅ Data scraping (with JavaScript support)
- ✅ API calls with custom headers
- ✅ PDF processing and table extraction
- ✅ CSV/Excel data analysis
- ✅ Statistical calculations
- ✅ Data transformation
- ✅ Visualization generation (charts as base64)
- ✅ Text processing and NLP

## 🚀 Deployment

### Local (for testing)
```bash
python app.py
```

### Using ngrok (temporary public URL)
```bash
# Terminal 1
python app.py

# Terminal 2
ngrok http 5000
```
Use the ngrok HTTPS URL for the Google Form.

### Production (Heroku example)
```bash
# Create Procfile
echo "web: gunicorn app:app" > Procfile

# Deploy
git init
git add .
git commit -m "Initial commit"
heroku create your-app-name
git push heroku main
```

## 🐛 Troubleshooting

### Common Issues

**Chrome driver not found:**
- Install Google Chrome browser
- Driver auto-downloads via webdriver-manager

**OpenAI API errors:**
- Check API key in `.env`
- Verify you have credits: https://platform.openai.com/usage

**Port already in use:**
```powershell
# Find and kill process
Get-NetTCPConnection -LocalPort 5000 | Select-Object OwningProcess
Stop-Process -Id <ProcessId> -Force
```

**Module import errors:**
```bash
pip install -r requirements.txt --force-reinstall
```

See `DEVELOPMENT.md` for detailed debugging guide.

## 📚 Documentation

- **DEVELOPMENT.md**: Development guide and debugging
- **Code comments**: Inline documentation in all modules

## 📝 Testing

### Manual Test
```bash
python test_endpoint.py
```

### With curl (PowerShell)
```powershell
$body = @{
    email = "your-email@example.com"
    secret = "your-secret"
    url = "https://tds-llm-analysis.s-anand.net/demo"
} | ConvertTo-Json

Invoke-WebRequest -Uri http://localhost:5000/quiz `
    -Method POST `
    -Body $body `
    -ContentType "application/json"
```

## 🔒 Security

- Never commit `.env` to Git (already in `.gitignore`)
- Use HTTPS in production
- Keep your secret key secure
- Rotate API keys periodically
- Validate all inputs

## 📄 License

MIT License - See [LICENSE](LICENSE) file for details.

## 🤝 Contributing

This is a student project for TDS.

---

**Good luck with your submission! 🎉**
