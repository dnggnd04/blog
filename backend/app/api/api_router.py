from fastapi import APIRouter

from app.api import register_router, user_router, login_router, post_router, like_router, comment_router, refresh_router

router = APIRouter()

router.include_router(register_router.router, tags=["register"], prefix="/register")
router.include_router(user_router.router, tags=["user"], prefix="/users")
router.include_router(login_router.router, tags=["login"], prefix="/login")
router.include_router(post_router.router, tags=["post"], prefix="/posts")
router.include_router(like_router.router, tags=["like"], prefix="/likes")
router.include_router(comment_router.router, tags=["comment"], prefix="/comments")
router.include_router(refresh_router.router, tags=["refresh"], prefix="/refresh")