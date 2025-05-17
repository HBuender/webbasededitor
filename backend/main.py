from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import docker
import time

app = FastAPI()

class CodeRequest(BaseModel):
    code: str

@app.post("/api/run-code")
async def run_code(request: CodeRequest):
    if not request.code or len(request.code) > 5000:
        raise HTTPException(status_code=400, detail="Invalid or too large code input.")

    client = docker.from_env()
    image = "python:3.9"
    timeout = 5  # seconds
    memory_limit = "50m"  # 50 MB

    try:
        client.images.pull(image)
        container = client.containers.run(
            image,
            command=["python3", "-c", request.code],
            detach=True,
            mem_limit=memory_limit,
            network_disabled=True,
            stdout=True,
            stderr=True,
            remove=False,
        )

        start_time = time.time()
        while container.status != "exited":
            container.reload()
            if time.time() - start_time > timeout:
                container.kill()
                raise HTTPException(status_code=408, detail="Execution timed out")

        logs = container.logs(stdout=True, stderr=True)
        logs_decoded = logs.decode("utf-8")
        container.remove()

        return {
            "output": logs_decoded,
            "errors": None,
            "execution_time": round(time.time() - start_time, 3)
        }

    except docker.errors.ContainerError as e:
        return {
            "output": None,
            "errors": e.stderr.decode("utf-8") if e.stderr else str(e),
            "execution_time": None
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
