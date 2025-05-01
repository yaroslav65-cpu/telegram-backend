from fastapi import FastAPI, WebSocket, HTTPException, Depends
from fastapi.security import OAuth2PasswordBearer
from pydantic import BaseModel
from jose import JWTError, jwt
from passlib.context import CryptContext
from datetime import datetime, timedelta
import json
from database import init_db

app = FastAPI()
db_conn = init_db()

# Налаштування JWT
SECRET_KEY = "your-secret-key-123"
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE = 30  # хвилин

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")

active_connections = {}

# Моделі
class UserRegister(BaseModel):  # Використовуємо Pydantic для валідації
    username: str
    password: str
    phone: str

class Message(BaseModel):
    sender: str
    text: str
    receiver: str


# Функції для роботи з JWT
def create_access_token(data: dict):
    expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE)
    data.update({"exp": expire})
    return jwt.encode(data, SECRET_KEY, algorithm=ALGORITHM)


def verify_password(plain_password, hashed_password):
    return pwd_context.verify(plain_password, hashed_password)


def get_password_hash(password):
    return pwd_context.hash(password)


# WebSocket для чату
@app.websocket("/ws/{token}")
async def websocket_endpoint(websocket: WebSocket, token: str):
    try:
        # Перевіряємо токен
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username = payload.get("sub")
    except JWTError:
        await websocket.close()
        return

    # Приймаємо підключення
    await websocket.accept()
    active_connections[username] = websocket

    try:
        while True:
            data = await websocket.receive_text()
            message = json.loads(data)

            # Зберігаємо повідомлення в БД
            cur = db_conn.cursor()
            cur.execute(
                "INSERT INTO messages (sender_id, receiver_id, text) VALUES (%s, %s, %s)",
                (message['sender'], message['receiver'], message['text'])
            )
            db_conn.commit()

            # Відправляємо повідомлення отримувачу
            if message['receiver'] in active_connections:
                await active_connections[message['receiver']].send_json(message)

    except Exception as e:
        print(f"Error: {e}")
    finally:
        del active_connections[username]


# API для реєстрації
@app.post("/register")
async def register(user: UserRegister):
    cur = db_conn.cursor()
    try:
        hashed_password = get_password_hash(user.password)
        cur.execute(
            "INSERT INTO users (username, password_hash, phone) VALUES (%s, %s, %s)",
            (user.username, hashed_password, user.phone)
        )
        db_conn.commit()
        return {"status": "success"}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=8000)
