from fastapi import FastAPI
from movies_api import app

# Inicializar la aplicación FastAPI desde movies_api
if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="127.0.0.1", port=8000)