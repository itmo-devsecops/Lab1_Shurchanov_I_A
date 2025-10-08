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
           