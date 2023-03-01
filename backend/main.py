from fastapi import FastAPI, Request, Response
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from app.routes.routes import router as appRoutes
from fastapi.middleware.cors import CORSMiddleware
import time
# from app.utils.classes import Logger, timing_format, timing_file

# logger = Logger('API', timing_file, timing_format)

# app = FastAPI(docs_url=None, redoc_url=None)
app = FastAPI()
app.mount("/static", StaticFiles(directory="static"), name="static")

# cors dependecies

origins = [
    "http://localhost",
    "http://localhost:3000",
    "http://localhost:4200",
    "http://localhost:4400",
    "http://localhost:45678",
    "http://3.136.56.93:3000",
    "http://3.136.56.93:4200",
    "http://3.136.56.93:4400",
    "http://3.132.202.223:4200",
    "https://examarly.com",
    "https://www.examarly.com",
    "https://test.examarly.com",
    "https://www.test.examarly.com",
    "https://www.staging1-community.examarly.com",
    "https://community.examarly.com",
    "https://stage.mopid.me",
    "https://mopid.me"
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
    allow_origin_regex="https://.*\.mopid\.me"
)

#order of api matters

# @app.middleware("http")
# async def add_process_time_header(request: Request, call_next):
#     startTime = time.time()
#     response : Response = await call_next(request)
#     elapsed_time = time.time()-startTime
#     logger.logger.info(f'{request.url} Elapsed time: {elapsed_time:0.4f} seconds')
#     return response


@app.get('/') #decorative function also called hof in javascript
def root():
    return "Welcome to Mopid-Backend"      

app.include_router(appRoutes,prefix='/api')