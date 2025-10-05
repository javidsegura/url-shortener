![Tests](https://img.shields.io/badge/tests-passing-brightgreen.svg)
![Coverage](https://img.shields.io/badge/coverage-92%25-brightgreen.svg)
![Build](https://img.shields.io/github/actions/workflow/status/javidsegura/url-shortener/ci.yml?branch=main&label=build)
![License](https://img.shields.io/github/license/javidsegura/url-shortener)
![Python](https://img.shields.io/badge/python-3.8%2B-blue.svg)
![React](https://img.shields.io/badge/frontend-react%4019.1.1-blue)
![AWS](https://img.shields.io/badge/deploy-aws-orange)

# URL Shortener  
  
A production-ready URL shortening service built with FastAPI, React, and deployed on AWS infrastructure.  
  
## Overview  
  
This URL shortener provides a scalable solution for creating and managing shortened URLs. The system features a FastAPI backend with multiple shortening strategies, a React + TypeScript frontend, and automated infrastructure provisioning using Terraform and Ansible. It supports local development with hot-reloading and production deployment to AWS with containerized services.  

## See extended documentation here
[Extended documentation](https://deepwiki.com/javidsegura/url-shortener/2.2-local-development-setup)


## Step-by-Step Installation

### 1. Environment Variable Setup
Before installing, set the **ENVIRONMENT** variable:
```bash
export ENVIRONMENT=dev # or 'staging' or 'prod'
````

This is validated by `Makefile:86-91` which exits with an error if **ENVIRONMENT** is undefined.

-----

### 2\. Install All Dependencies

From the repository root:

```bash
make install
```

This command:

  * Validates the **ENVIRONMENT** variable
  * Installs backend dependencies: `make -C backend install`
  * Installs frontend dependencies: `make -C frontend install`
  * Installs infrastructure tools: `make -C infra install`
  * Installs **jq** via Homebrew for JSON processing

-----

### 3\. Package-Only Installation (Alternative)

To install only application packages without infrastructure tooling:

```bash
make install-packages
```

This skips infrastructure tools and only installs backend and frontend packages.

-----

## Backend-Specific Installation

The backend uses Python's `pyproject.toml` with setuptools. Installation modes:

| Command | Installs | Use Case |
| :--- | :--- | :--- |
| `pip install -e .` | Runtime dependencies only | Production deployment |
| `pip install -e .[dev]` | Runtime + dev tools | Local development |
| `pip install -e .[tests]` | Runtime + test tools | CI/CD pipelines |
| `pip install -e .[dev,tests]` | All dependencies | Complete local setup |

The `-e` flag installs in editable mode, allowing code changes without reinstallation. The package source is located in `src/` as specified by `backend/pyproject.toml:52-53`.



## Local dev set-up
### 0. Generate remote infra state 
#### 1. Create infra/terraform/set-up/terraform.tfvars and write
project_name = "url-shortener"
#### 2. Generate remote state 
```bash
make -C infra start-remote-state
```
### 1. Set up environmental variables
Before installing, set the **ENVIRONMENT** variable:
```bash
      export ENVIRONMENT=dev 
```
### 2. Generate `.env` Templates
You'll need to create and populate `.env` files for both the backend and frontend services.

### Backend

1. Navigate to the directory `backend/env/env_config/base`.

2. Create a new file named `.env.dev`.

3. Add the following variables to the file. You must set these to actual values before running the application, but for now, they are set to **empty strings** as placeholders.
      ```
      REDIS
      REDIS_URL=""

      DB
      MYSQL_USER=""
      MYSQL_PASSWORD=""
      MYSQL_HOST=""
      MYSQL_PORT=""
      MYSQL_DATABASE=""
      MYSQL_SYNC_DRIVER=""
      MYSQL_ASYNC_DRIVER=""

      AWS
      AWS_ACCESS_KEY_ID=""
      AWS_SECRET_ACCESS_KEY=""
      AWS_MAIN_REGION=""
      ```
### Frontend

1. Go to the frontend directory: `frontend/app/env_config/base`.

2. Create a new file named `.env.dev`.

3. **Note:** The file must exist at this path, but for the initial setup, you **do not need to fill in any environmental variables** inside it.

### 3. Start app locally
```bash
make dev-start # Starts the entire local dev environment
dev-stop # Kills the entire local dev environment
dev-restart-docker-compose # Useful for debugging backend/frontend with hot reloading
```

### 4. Run tests with:
```bash
make -C backend pytest-run
```

# ENTIRE TECH STACK
Based on the codebase analysis, here is the tech stack used in the URL shortener project:

## Backend
- **Python** (>=3.8) [1](#1-0) 
- **FastAPI** (web framework) [2](#1-1) 
- **Uvicorn** (ASGI server) [3](#1-2) 
- **Gunicorn** (production server) [4](#1-3) 
- **Pydantic** (data validation) [5](#1-4) 
- **SQLAlchemy** (ORM with async support) [6](#1-5) 
- **MySQL** (database) [7](#1-6) 
- **Redis** (caching) [8](#1-7) 
- **Alembic** (database migrations) [9](#1-8) 
- **Firebase Admin** (authentication) [10](#1-9) 
- **Boto3** (AWS SDK) [11](#1-10) 

## Frontend
- **React** (19.1.1) [12](#1-11) 
- **TypeScript** [13](#1-12) 
- **Vite** (build tool) [14](#1-13) 
- **React Router DOM** (routing) [15](#1-14) 
- **Tailwind CSS** (styling) [16](#1-15) 
- **Firebase** (client SDK) [17](#1-16) 
- **Radix UI** (component library) [18](#1-17) 
- **Lucide React** (icons) [19](#1-18) 

## Infrastructure & DevOps
- **Docker** & **Docker Compose** [20](#1-19) 
- **Nginx** (reverse proxy) [21](#1-20) 
- **Terraform** (infrastructure as code) [22](#1-21) 
- **Ansible** (configuration management) [23](#1-22) 
- **AWS** (cloud provider - RDS for database)

## Testing & Development Tools
- **Pytest** (backend testing) [24](#1-23) 
- **ESLint** (frontend linting) [25](#1-24) 
- **Ruff** (Python linting/formatting) [26](#1-25) 
- **Pre-commit** (git hooks) [27](#1-26) 

## Notes
The project follows a microservices architecture with separate backend (Python/FastAPI) and frontend (React/TypeScript) applications. The infrastructure is containerized using Docker and can be orchestrated with Docker Compose. For production deployments, the project uses Terraform for AWS infrastructure provisioning (including RDS for the MySQL database) and Ansible for configuration management.

### Citations

**File:** backend/pyproject.toml (L4-4)
```text
requires-python = ">=3.8"
```

**File:** backend/pyproject.toml (L6-6)
```text
      "fastapi",
```

**File:** backend/pyproject.toml (L7-7)
```text
      "uvicorn",
```

**File:** backend/pyproject.toml (L8-8)
```text
      "gunicorn",
```

**File:** backend/pyproject.toml (L9-9)
```text
      "pydantic",
```

**File:** backend/pyproject.toml (L10-10)
```text
      "redis",
```

**File:** backend/pyproject.toml (L13-13)
```text
      "sqlalchemy[asyncio]",
```

**File:** backend/pyproject.toml (L17-17)
```text
      "firebase-admin",
```

**File:** backend/pyproject.toml (L18-18)
```text
      "boto3",
```

**File:** backend/pyproject.toml (L19-19)
```text
      "alembic"
```

**File:** backend/pyproject.toml (L24-24)
```text
      "ruff",
```

**File:** backend/pyproject.toml (L26-26)
```text
      "pre-commit",
```

**File:** backend/pyproject.toml (L29-29)
```text
      "ansible-core",
```

**File:** backend/pyproject.toml (L37-37)
```text
      "pytest",
```

**File:** docker-compose.dev.yml (L39-39)
```yaml
    image: mysql:8.0
```

**File:** frontend/app/package.json (L14-14)
```json
    "@radix-ui/react-avatar": "^1.1.10",
```

**File:** frontend/app/package.json (L17-17)
```json
    "firebase": "^12.2.0",
```

**File:** frontend/app/package.json (L18-18)
```json
    "lucide-react": "^0.542.0",
```

**File:** frontend/app/package.json (L19-19)
```json
    "react": "^19.1.1",
```

**File:** frontend/app/package.json (L21-21)
```json
    "react-router-dom": "^7.8.2",
```

**File:** frontend/app/package.json (L32-32)
```json
    "eslint": "^9.33.0",
```

**File:** frontend/app/package.json (L37-37)
```json
    "tailwindcss": "^4.1.12",
```

**File:** frontend/app/package.json (L39-39)
```json
    "typescript": "~5.8.3",
```

**File:** frontend/app/package.json (L41-41)
```json
    "vite": "^7.1.2"
```

**File:** docker-compose.yml (L1-2)
```yaml
# Nginx server (added later), redis, db (added later)
services:
```

**File:** docker-compose.yml (L35-36)
```yaml
  nginx:
    image: nginx:alpine
```

**File:** infra/terraform/modules/rds (L1-1)
```text
[{"name":"main.tf","path":"infra/terraform/modules/rds/main.tf","sha":"5391855792610e98dbc30196c23b4163a3a2936f","size":1156,"url":"https://api.github.com/repos/javidsegura/url-shortener/contents/infra/terraform/modules/rds/main.tf?ref=main","html_url":"https://github.com/javidsegura/url-shortener/blob/main/infra/terraform/modules/rds/main.tf","git_url":"https://api.github.com/repos/javidsegura/url-shortener/git/blobs/5391855792610e98dbc30196c23b4163a3a2936f","download_url":"https://raw.githubusercontent.com/javidsegura/url-shortener/main/infra/terraform/modules/rds/main.tf","type":"file","_links":{"self":"https://api.github.com/repos/javidsegura/url-shortener/contents/infra/terraform/modules/rds/main.tf?ref=main","git":"https://api.github.com/repos/javidsegura/url-shortener/git/blobs/5391855792610e98dbc30196c23b4163a3a2936f","html":"https://github.com/javidsegura/url-shortener/blob/main/infra/terraform/modules/rds/main.tf"}},{"name":"outputs.tf","path":"infra/terraform/modules/rds/outputs.tf","sha":"335187c8f2bb2972083c43a4f925245aba6a2e88","size":279,"url":"https://api.github.com/repos/javidsegura/url-shortener/contents/infra/terraform/modules/rds/outputs.tf?ref=main","html_url":"https://github.com/javidsegura/url-shortener/blob/main/infra/terraform/modules/rds/outputs.tf","git_url":"https://api.github.com/repos/javidsegura/url-shortener/git/blobs/335187c8f2bb2972083c43a4f925245aba6a2e88","download_url":"https://raw.githubusercontent.com/javidsegura/url-shortener/main/infra/terraform/modules/rds/outputs.tf","type":"file","_links":{"self":"https://api.github.com/repos/javidsegura/url-shortener/contents/infra/terraform/modules/rds/outputs.tf?ref=main","git":"https://api.github.com/repos/javidsegura/url-shortener/git/blobs/335187c8f2bb2972083c43a4f925245aba6a2e88","html":"https://github.com/javidsegura/url-shortener/blob/main/infra/terraform/modules/rds/outputs.tf"}},{"name":"variables.tf","path":"infra/terraform/modules/rds/variables.tf","sha":"d8bbae5797386c6616e2093b2abc23cddb93d6bd","size":192,"url":"https://api.github.com/repos/javidsegura/url-shortener/contents/infra/terraform/modules/rds/variables.tf?ref=main","html_url":"https://github.com/javidsegura/url-shortener/blob/main/infra/terraform/modules/rds/variables.tf","git_url":"https://api.github.com/repos/javidsegura/url-shortener/git/blobs/d8bbae5797386c6616e2093b2abc23cddb93d6bd","download_url":"https://raw.githubusercontent.com/javidsegura/url-shortener/main/infra/terraform/modules/rds/variables.tf","type":"file","_links":{"self":"https://api.github.com/repos/javidsegura/url-shortener/contents/infra/terraform/modules/rds/variables.tf?ref=main","git":"https://api.github.com/repos/javidsegura/url-shortener/git/blobs/d8bbae5797386c6616e2093b2abc23cddb93d6bd","html":"https://github.com/javidsegura/url-shortener/blob/main/infra/terraform/modules/rds/variables.tf"}}]
```
