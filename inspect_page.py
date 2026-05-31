import paramiko

MAIN_PY = """
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from scrapling import Fetcher
import uvicorn

app = FastAPI()

class ScrapeRequest(BaseModel):
    url: str

@app.post("/scrape")
def scrape_url(request: ScrapeRequest):
    fetcher = Fetcher(stealth=True, headless=True)
    page = fetcher.get(request.url)
    return {"dir": dir(page)}

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
"""

host = '10.147.18.204'
ssh = paramiko.SSHClient()
ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
ssh.connect(host, 22, 'root', 'Twinc3pt.2')
sftp = ssh.open_sftp()
with sftp.file('/opt/scrapling-mcp/main.py', 'w') as f:
    f.write(MAIN_PY)

print("Rebuilding...")
ssh.exec_command('cd /opt/scrapling-mcp && docker compose build && docker compose up -d')
ssh.close()
