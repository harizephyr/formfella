from fastapi import FastAPI
from api.v1.endpoints import auth 
from starlette.middleware.sessions import SessionMiddleware
import os
from fastapi.middleware.cors import CORSMiddleware
# from services.llm_form_filler import router as llm_form_filler_router
from api.v1.endpoints import payment
from api.v1.endpoints import process

app = FastAPI()

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000","*"],  # Frontend URL
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
    expose_headers=["*"],
    max_age=600,  # Cache preflight requests for 10 minutes
)


app.include_router(auth.router, prefix="/api/v1", tags=["auth"])
app.include_router(process.router, prefix="", tags=["process"])
app.include_router(payment.router, prefix="/api/v1", tags=["payment"])

app.add_middleware(SessionMiddleware, secret_key=os.urandom(24))

@app.get("/")
def health_check():
    return {"status": "ok"}
    


if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)