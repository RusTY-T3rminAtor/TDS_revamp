# Development and Testing Guide

## Quick Start

### 1. Initial Setup
```bash
# Install dependencies
python setup.py

# Or manually:
pip install -r requirements.txt
```

### 2. Configure Environment
Copy `.env.example` to `.env` and fill in your credentials:
```
STUDENT_EMAIL=your-email@example.com
SECRET_KEY=your-secret-string
OPENAI_API_KEY=sk-your-api-key
PORT=5000
DEBUG=True
```

### 3. Run the Server
```bash
python app.py
```

Server will start on `http://localhost:5000`

### 4. Test the Endpoint
In a new terminal:
```bash
python test_endpoint.py
```

## Manual Testing

### Test with curl (PowerShell)
```powershell
# Valid request
$body = @{
    email = "your-email@example.com"
    secret = "your-secret"
    url = "https://tds-llm-analysis.s-anand.net/demo"
} | ConvertTo-Json

Invoke-WebRequest -Uri http://localhost:5000/quiz -Method POST -Body $body -ContentType "application/json"

# Invalid secret
$badBody = @{
    email = "your-email@example.com"
    secret = "wrong-secret"
    url = "https://tds-llm-analysis.s-anand.net/demo"
} | ConvertTo-Json

Invoke-WebRequest -Uri http://localhost:5000/quiz -Method POST -Body $badBody -ContentType "application/json"
```

### Test with Python
```python
import requests

response = requests.post(
    "http://localhost:5000/quiz",
    json={
        "email": "your-email@example.com",
        "secret": "your-secret",
        "url": "https://tds-llm-analysis.s-anand.net/demo"
    }
)

print(response.status_code)
print(response.json())
```

## Debugging

### Enable Verbose Logging
Edit `app.py` and set:
```python
logging.basicConfig(level=logging.DEBUG)
```

### Common Issues

#### 1. Chrome Driver Not Found
**Solution:** The script auto-downloads ChromeDriver via webdriver-manager. Ensure you have Chrome browser installed.

#### 2. OpenAI API Key Invalid
**Error:** `openai.error.AuthenticationError`
**Solution:** Check your API key in `.env` file. Get a valid key from https://platform.openai.com/api-keys

#### 3. Port Already in Use
**Error:** `Address already in use`
**Solution:** Change PORT in `.env` or kill the process:
```powershell
# Find process using port 5000
Get-NetTCPConnection -LocalPort 5000 | Select-Object OwningProcess
# Kill it
Stop-Process -Id <ProcessId> -Force
```

#### 4. Module Import Errors
**Solution:** Reinstall dependencies:
```bash
pip install -r requirements.txt --force-reinstall
```

#### 5. Headless Browser Issues
**Solution:** If Chrome fails, try:
```python
# In browser_handler.py, temporarily disable headless mode:
chrome_options.add_argument('--headless')  # Comment this line
```

## Project Structure

```
TDS_revamp/
├── app.py                  # Flask API server
├── quiz_solver.py          # Main quiz solving logic
├── browser_handler.py      # Headless browser management
├── llm_handler.py          # OpenAI LLM integration
├── data_processor.py       # Data analysis utilities
├── prompts.py              # System/user prompts
├── config.py               # Configuration management
├── requirements.txt        # Dependencies
├── .gitignore              # Git ignore rules
├── LICENSE                 # MIT License
├── README.md               # Project documentation
├── Project_summary.md      # Project Summary
└── Development_guide.md    # This file
```

## Workflow

1. **Receive Quiz Request** → Flask endpoint validates and accepts
2. **Fetch Quiz Page** → Headless browser renders JavaScript
3. **Analyze Task** → LLM extracts requirements
4. **Process Data** → Download files, scrape, parse
5. **Solve Task** → LLM performs analysis
6. **Submit Answer** → POST to specified endpoint
7. **Continue Chain** → Repeat if new URL provided

## Testing Checklist

- [ ] Server starts without errors
- [ ] Health endpoint responds: `GET http://localhost:5000/health`
- [ ] Quiz endpoint accepts valid requests: `POST /quiz`
- [ ] Quiz endpoint rejects invalid JSON (400)
- [ ] Quiz endpoint rejects invalid secret (403)
- [ ] Quiz endpoint rejects missing fields (400)
- [ ] Browser handler can fetch pages
- [ ] LLM handler can analyze quiz content
- [ ] Data processor can download files
- [ ] Answer submission works

## Deployment

### Local Deployment
```bash
python app.py
```

### Using gunicorn (Production)
```bash
pip install gunicorn
gunicorn -w 4 -b 0.0.0.0:5000 app:app
```

### Using Docker
Create `Dockerfile`:
```dockerfile
FROM python:3.11-slim
WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt
RUN apt-get update && apt-get install -y chromium chromium-driver
COPY . .
CMD ["python", "app.py"]
```

Build and run:
```bash
docker build -t llm-quiz .
docker run -p 5000:5000 --env-file .env llm-quiz
```

## Performance Tips

1. **Use GPT-4o-mini** for cost efficiency (already configured)
2. **Cache common results** for repeated queries
3. **Parallel processing** for multiple files
4. **Connection pooling** for HTTP requests

## Security Notes

- Never commit `.env` file to Git
- Keep API keys secret
- Use HTTPS in production
- Validate all inputs
- Rate limit the endpoint

## Support

For issues:
1. Check logs in console
2. Review error messages
3. Verify environment variables
4. Test each component individually
