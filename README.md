# Recipe API

A small but well-structured **Recipe API** built with **FastAPI**, **Strawberry GraphQL**, and **SQLAlchemy 2.0**, including an **AI-powered recipe recommendation** feature.

The scope is intentionally small, with a focus on **clean architecture, testability, and thoughtful design decisions**.

---

## Tech Stack

- **Python 3.13**
- **FastAPI** (REST API)
- **Strawberry GraphQL**
- **SQLAlchemy 2.0 (async)**
- **SQLite** (local / tests)
- **pytest**
- **AI integration** (LLM-based)

---

## Features

### Recipes
- Create recipes
- List recipes
- Delete recipes
- Shared service layer for REST and GraphQL

### AI Recommendation
- Recommends one recipe based on existing data
- AI client is **fully decoupled and mockable**
- Graceful fallback behavior
- External credentials configurable via environment variables

---

## API Overview

### REST Endpoints

| Method | Endpoint | Description |
|------|--------|-------------|
| POST | `/recipes` | Create a recipe |
| GET | `/recipes` | List recipes |
| DELETE | `/recipes/{id}` | Delete a recipe |
| GET | `/recipes/recommendation` | AI-based recommendation |

---

### GraphQL

#### Queries
- `recipes`
- `recommendRecipe`

#### Mutations
- `createRecipe`
- `deleteRecipe`

REST and GraphQL both rely on the **same service layer**, ensuring consistent business logic.

---

## Project Structure

```text
app/
├── api/
│   ├── rest.py
│   └── graphql.py
├── core/
│   └── config.py
├── services/
│   ├── recipes.py
│   └── ai.py
├── db/
│   ├── models.py
│   ├── repo.py
│   └── session.py
├── domain/
│   └── schemas.py
├── main.py
tests/
├── test_rest_recipes.py
├── test_graphql_recipes.py
├── test_ai_recommendation.py
└── conftest.py
```

---

## AI Integration

The AI recommendation is implemented as a **thin integration layer**:

- Receives existing recipes as context
- Returns a recommended recipe or suggestion
- Designed for easy replacement (OpenAI, Anthropic, local model)
- Fully mockable for deterministic tests

This approach focuses on **integration quality**, not model complexity.

---

## Running the Project Locally

### 1. Prerequisites

Make sure you have installed:

- **Python 3.13**
- **pip**
- **Git**

Optional but recommended:
- `make`
- `curl` or `httpie`

---

### 2. Clone the Repository

```bash
git clone https://github.com/alevarriola/recipe-api.git
cd recipe-api
```

---

### 3. Create and Activate Virtual Environment

#### Windows (PowerShell)

```powershell
python -m venv .venv
.venv\Scripts\Activate.ps1
```

If you get a policy error:

```powershell
Set-ExecutionPolicy -Scope CurrentUser -ExecutionPolicy RemoteSigned
```

---

#### macOS / Linux

```bash
python3.13 -m venv .venv
source .venv/bin/activate
```

---

### 4. Install Dependencies

```bash
pip install -e .[dev] 
```

---

### 5. Environment Variables

Create a `.env` file in the project root:

```env
DATABASE_URL=sqlite+aiosqlite:///./recipes.db
ANTHROPIC_API_KEY=
ANTHROPIC_MODEL=claude-3-5-sonnet-latest
```

If no API key is provided, the application will fall back to a safe default recommendation behavior.

---

### 6. Initialize the Database

For local development and tests, tables are created automatically at startup.

If you want to manually ensure tables exist:

```bash
python -m app.db.init_db
```

---

### 7. Run the Application

```bash
uvicorn app.main:app --reload
```

The API will be available at:

- REST API: http://localhost:8000
- Swagger UI: http://localhost:8000/docs
- GraphQL Playground: http://localhost:8000/graphql

---


---

## Testing

Run all tests:

```bash
pytest -q
```

Test coverage includes:
- REST endpoints
- GraphQL API
- Database interactions
- AI recommendation (mocked)

---


## Author Notes

This project emphasizes:
- Clean separation of concerns
- Shared business logic across APIs
- Async-first SQLAlchemy 2.0 usage
- Pragmatic AI integration
- Strong test isolation and mocking

