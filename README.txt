Веб сервис состоит из четырех элементов: микросервиса Website (отвечает за управление пользователями и комнатами), 
микросервиса Chat (отвечает за функционал Websocket чатов), базы данных и сервера.

Структура проекта: 
БД (две таблицы: users и chats)
Приложение:
WEBAPP/
├── .vscode/               
│   ├── launch.json        
│   └── tasks.json          
│
├── Chat/                   
│   ├── __pycache__/        
│   ├── Templates/                  
│   └── Chat.py  
│     	
├── nginx/                 
│   └── nginx.conf
│
├── Website/                
│   ├── __pycache__/        
│   ├── Templates/                
│   └── Website.py          
│     
├── README.txt              
└── README.md   
Зависимости:

Для Chat:
fastapi
uvicorn
pydantic
pyjwt
jinja2
websockets

Для Website:
fastapi
uvicorn
pydantic
sqlalchemy
psycopg2-binary
pyjwt
jinja2
python-multipart

Запуск: запустить оба микросервиса. Доступ по порту 5000.
Для запуска требуется PostgreSQL.
При первом запуске приложения происходит автоматическая инициализация базы данных.

## Running with Docker

This project provides Dockerfiles for both the Chat and Website services, using Python 3.13-slim and virtual environments for dependency isolation. The services are orchestrated via Docker Compose.

### Requirements
- Python 3.13-slim (as specified in Dockerfiles)
- `requirements.txt` for Python dependencies (automatically installed in each service's container)

### Services and Ports
- **python-chat**: Exposes port `8000` (mapped to host `8000`)
- **python-website**: Exposes port `5000` (mapped to host `5000`)

### Build and Run
1. Ensure Docker and Docker Compose are installed.
2. From the project root, run:
   ```sh
   docker compose up --build
   ```
   This will build and start both services.

### Configuration
- No environment variables are required by default. If you need to set any, uncomment the `env_file` lines in the `docker-compose.yaml` and provide `.env` files in the respective service directories.
- The services are connected via a custom `backend` bridge network.
- The Website service depends on the Chat service (see `depends_on` in compose file).

### Notes
- If you change dependencies, update `requirements.txt` and rebuild the containers.
- Adjust exposed ports in the compose file if you need to avoid conflicts.

           