# Contributing

Thank you for your interest in contributing to the Personal Finance Multi-Agent Analyzer.

## How to contribute

### Report a bug

Open an [issue](https://github.com/yjumatov/personal-finance-agent/issues) and include:
- What you did
- What you expected to happen
- What actually happened
- Your OS and Python version

### Suggest a feature

Open an issue with the `enhancement` label and describe the use case.

### Submit a pull request

1. Fork the repository
2. Create a feature branch:
   ```bash
   git checkout -b feature/your-feature-name
   ```
3. Make your changes
4. Test both interfaces (Streamlit app and API server)
5. Commit with a clear message:
   ```bash
   git commit -m "Add: short description of what you added"
   ```
6. Push and open a pull request against `main`

## Development setup

```bash
git clone https://github.com/yjumatov/personal-finance-agent.git
cd personal-finance-agent
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
cp .env.example .env
# add your ANTHROPIC_API_KEY to .env
```

Run the Streamlit app:
```bash
streamlit run app.py
```

Run the API server:
```bash
uvicorn api_server:app --reload
```

## Code style

- Follow PEP 8
- Keep functions small and focused
- Do not commit `.env` or any file containing API keys
- Remove debug `print()` statements before submitting

## Areas open for contribution

- Add unit tests
- Support more CSV column name variations
- Add expense visualization charts to the Streamlit UI
- Support additional AI models or providers
- Improve error messages for common API errors
