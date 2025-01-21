# NB: running the app with this file as opposed to "uvicorn app:app ..." since uvicorn obscures
# uncaught exceptions thrown before server starts up

from app import app

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
