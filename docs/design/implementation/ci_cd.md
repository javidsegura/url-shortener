
#### Dev environment
- Python version: 3.10
- IDE: Cursos
- Extensions: python linter, terraform linter, docker compose linter, docker image linter 
- Pre-commits: tests, linting, formatting, bandit, lstort

#### CI/CD pipeline
##### CI
- Formatting => Black, Makefile for infra, TS in frontend
- Linting => Ruff, Makefile for infra, TS in frontend
- Tests => pytest (benchmarked transformation, coverage, async test)
- Lsort 
- Doccs extraction 
#### CD
##### LOCAL DEV
- Docker compose the bind mount to backend and frontend, s3 in cloud (special for dev), db in container 
  - Prod to dev data:
    - Set up bastion host 
    - Create SSH tunnel
    - Connect locally 
##### PROD
- Environmental variables needed
  - APP_ENV=PROD
- Build frontend artifacts
- Get SSL certified (with certbot) -- only once, tho
- Run infra changes
- Run playbook for ansible (pull docker images, start docker compose)
- Build docker images

