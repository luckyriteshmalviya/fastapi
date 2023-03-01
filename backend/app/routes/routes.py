from fastapi import Depends, APIRouter

from app.utils.jwtHandler import hasAccess, isAdminAccess, isFacultyAccess
from app.mopid.user.controller import userRouter
from app.mopid.testData.controller import testRouter
from app.mopid.questionModule.controller import questionRouter

router = APIRouter()

router.include_router(
    testRouter,
    prefix='/test',
    tags=['Test'],
)

router.include_router(
    userRouter,
    prefix='/user',
    tags=['user']
)

router.include_router(
    questionRouter,
    prefix='/question',
    tags=['question']
)