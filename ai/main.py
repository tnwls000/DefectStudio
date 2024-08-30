import io

import uvicorn
from PIL import Image
from fastapi import FastAPI

from util import upload_files

app = FastAPI()


@app.get('/upload')
def upload():
    im = Image.open("./dog.png")
    stream = io.BytesIO()
    im.save(stream, format="jpeg", quality=90)
    stream.seek(0)
    stream_list = [stream]

    list = upload_files(stream_list)
    return {'url_list': list}


if __name__ == "__main__":
    uvicorn.run(app, host="localhost", port=8000)
