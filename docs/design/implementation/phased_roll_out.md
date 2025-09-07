
### PHASED ROLL-OUT PLAN
1. Local-dev
  - Create local nginx (http only) that serves frontend assets, backend (1 hour)
    - Create backend [DONE]
    - Create frotnend [DONE]
    - Create transfromation algorithm:
      - Handle collisions [DONE]
      - Upload to redis 
        - .env [DONE]
        - Docker compose [DONE]
      - Create redirect functionality [DONE]
      - Test redirect from frontend [DONE]
    - Nginx for backend  [DONE]
    - Create frontend + backend through nginx [DONE]
  - Create local db, provide schema (1 hour)
    - Create endpoint [DONE]
    - Test connection [DONE]
  - Integrate redis, transformation algorithm (with collision handling) (30 mins) [DONE]
  - Integrate firebase basic auth (1 1/4 hour)
    - Allow to log-in (subcomponent inside subcomponet?) [DONE]
    - Frontend auth-hidden pages 
      - Force email verification [DONE]
      - Force auth [DONE]
      - Redirect to links page after logged in [DONE]
    - Databas health status [DONE]
    - Require in backend tokens [DONE]
  - Integrate registering operations to db (30 min)
    - User info 
      - Firebase (profile pic, email, isVerified, displayableName) [DONE]
      - Store user info even when they sign up via federated providers 
      - URL specific protection [DONE]
    - Link history [DONE]
  - Allow firebase editing (1 1/2 hour --frontend is bottleneck for me) [DONE]
  - Allow shortened url links  (1 1/2 hour) [DONE]
  - Integrate linter, test and stuff for backend
  - Lifespan not working!!!
  - Add tests (benchmarking, locust) (1 hour)
  - Shadcn Profile component [DONE]
  - 404 page [DONE]
  - Alembic, precommits
  - Gitignore
  - Fastapi config 
  - General test
  - Prod
  - CI/CD
2. Prod
  - Create terraform (1)
  - Create makefiles for CI/CD  (2 hours)

### RESOURCE ESTIMATION
- Less than 5$ on AWS 1-year free plan
