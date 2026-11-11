import subprocess
import sys
import time

def run():
    cmd = [sys.executable, "-m", "uvicorn", "backend.app.main:app", "--host", "127.0.0.1", "--port", "8000", "--loop", "asyncio"]
    while True:
        try:
            print("Starting uvicorn server...")
            proc = subprocess.Popen(cmd)
            proc.wait()
            print(f"Uvicorn exited with code {proc.returncode}. Restarting in 1s...")
            time.sleep(1)
        except KeyboardInterrupt:
            break
        except Exception as e:
            print(f"Runner error: {e}. Retrying in 2s...")
            time.sleep(2)

if __name__ == "__main__":
    run()

