from fastapi import APIRouter, Request
from fastapi.responses import JSONResponse
from fastapi.templating import Jinja2Templates

router = APIRouter()
templates = Jinja2Templates(directory="web/templates")


@router.get("/login")
def login(request: Request):
    """Login endpoint - placeholder for Google OAuth"""
    return JSONResponse(
        content={"message": "Login endpoint - to be implemented with Google OAuth"}
    )


@router.get("/auth/callback")
def auth_callback(request: Request):
    """OAuth callback endpoint - placeholder"""
    return JSONResponse(
        content={"message": "Auth callback endpoint - to be implemented"}
    )


@router.get("/logout")
def logout(request: Request):
    """Logout endpoint - placeholder"""
    return JSONResponse(
        content={"message": "Logout endpoint - to be implemented"}
    )
