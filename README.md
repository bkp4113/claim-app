# Claim-app
Claim processing app built on FastAPI and Postgres using the CDM(common data-model)

## Pre Requirements
Please install python3 and docker
- `brew install python3`
- `brew install docker`

## Local Development Requirements
- Clone repo locally
   ```bash
   git clone https://github.com/bkp4113/claim-app.git
   cd repo claim-app
   ```

- Install python dependency
   ```bash
   python3 -m venv .venv
   source .venv/bin/activate
   pip3 install requirements.txt
   ```

- VS Code configuration for local development
  ```json
  {
      // Use IntelliSense to learn about possible attributes.
      // Hover to view descriptions of existing attributes.
      // For more information, visit: https://go.microsoft.com/fwlink/?linkid=830387
      "version": "0.2.0",
      "configurations": [
         {
               "name": "Python Debugger: FastAPI",
               "type": "debugpy",
               "request": "launch",
               "module": "uvicorn",
               "cwd": "${workspaceFolder}/app",
               "args": [
                  "asgi:app",
                  "--reload",
                  "--port",
                  "8080"
               ],
               "env": {
                  "ENVIRONMENT": "dev",
                  "DISABLE_SWAGGER": "false",
                  "DATABASE_URL": "postgresql://test:test123!@localhost:5432/test",
               },
               "jinja": true
         }
      ]
   }
   ```

## Validation steps
- Docker compose up both claim process and postgres container service

   `docker compose build`

   `docker compose up`
- Run the tests 
   - Opt1: from tests/test_api.py dir
      - Assuming you've setup the local development venv or at minimum installed requests module
         `python3 tests/test_api.py`
   - Opt2: Alternatively can be done via POSTMAN
      - Swagger UI is deployed at "http://localhost:8080/docs", Please get the openapi.json and use that to create POSTMAN collection for testing.
   - Opt3: Directly from swagger UI
      - Swagger UI is deployed at "http://localhost:8080/docs"
      - Here after selecting local server from left and authenticating with "test" bearer token you can invoke or test any API.