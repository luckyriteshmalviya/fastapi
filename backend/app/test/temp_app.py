from fastapi import FastAPI;
from fastapi.staticfiles import StaticFiles
from app.routes.routes import router as appRoutes;
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI(docs_url=None, redoc_url=None)
app.mount("/static", StaticFiles(directory="static"), name="static")



origins = [
    "http://localhost"
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

#order of api matters

@app.get('/') #decorative function also called hof in javascript
def root():
    return "Welcome to mopid backend"

app.include_router(appRoutes,prefix='/api')
