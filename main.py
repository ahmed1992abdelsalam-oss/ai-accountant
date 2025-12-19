from fastapi import FastAPI
from fastapi.responses import HTMLResponse
import os

app = FastAPI(title="AI Accountant")

@app.get("/", response_class=HTMLResponse)
@app.head("/")
def home():
    return """
    <html>
        <head>
            <title>AI Accountant</title>
        </head>
        <body style="font-family:Arial;text-align:center;margin-top:50px">
            <h1>✅ AI Accountant is running</h1>
            <p>FastAPI + Render</p>
        </body>
    </html>
    """

if __name__ == "__main__":
    import uvicorn
    port = int(os.environ.get("PORT", 10000))
    uvicorn.run(app, host="0.0.0.0", port=port)
