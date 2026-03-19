"""
用户认证 API
注册、登录、用户管理
"""

from datetime import datetime, timedelta
from typing import Optional
from fastapi import APIRouter, HTTPException, Depends, status
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from pydantic import BaseModel, EmailStr
from passlib.context import CryptContext
from jose import JWTError, jwt

from server.database import get_db_context, User, DashboardConfig, UserPreference

router = APIRouter(prefix="/api/auth", tags=["用户认证"])

# JWT 配置
SECRET_KEY = "your-secret-key-change-in-production"  # TODO: 使用环境变量
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30

# 密码加密
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# OAuth2
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="api/auth/login")


# ============ Pydantic 模型 ============

class UserRegister(BaseModel):
    """用户注册请求"""
    username: str
    email: EmailStr
    password: str
    nickname: Optional[str] = None


class UserLogin(BaseModel):
    """用户登录请求"""
    username: str
    password: str


class Token(BaseModel):
    """访问令牌"""
    access_token: str
    token_type: str = "bearer"
    expires_in: int


class UserResponse(BaseModel):
    """用户信息响应"""
    id: int
    username: str
    email: str
    nickname: Optional[str] = None
    avatar_url: Optional[str] = None
    created_at: datetime
    
    class Config:
        from_attributes = True


# ============ 工具函数 ============

def verify_password(plain_password: str, hashed_password: str) -> bool:
    """验证密码"""
    return pwd_context.verify(plain_password, hashed_password)


def get_password_hash(password: str) -> str:
    """生成密码哈希"""
    return pwd_context.hash(password)


def create_access_token(data: dict, expires_delta: Optional[timedelta] = None) -> str:
    """创建访问令牌"""
    to_encode = data.copy()
    expire = datetime.utcnow() + (expires_delta or timedelta(minutes=15))
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)


async def get_current_user(token: str = Depends(oauth2_scheme)) -> User:
    """获取当前用户"""
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="无法验证凭据",
        headers={"WWW-Authenticate": "Bearer"},
    )
    
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username: str = payload.get("sub")
        if username is None:
            raise credentials_exception
    except JWTError:
        raise credentials_exception
    
    with get_db_context() as db:
        user = db.query(User).filter(User.username == username).first()
        if user is None:
            raise credentials_exception
        return user


# ============ API 端点 ============

@router.post("/register", response_model=UserResponse)
async def register(user_data: UserRegister):
    """用户注册"""
    with get_db_context() as db:
        # 检查用户名是否已存在
        existing_user = db.query(User).filter(
            User.username == user_data.username
        ).first()
        if existing_user:
            raise HTTPException(
                status_code=400,
                detail="用户名已存在"
            )
        
        # 检查邮箱是否已存在
        existing_email = db.query(User).filter(
            User.email == user_data.email
        ).first()
        if existing_email:
            raise HTTPException(
                status_code=400,
                detail="邮箱已被注册"
            )
        
        # 创建用户
        user = User(
            username=user_data.username,
            email=user_data.email,
            password_hash=get_password_hash(user_data.password),
            nickname=user_data.nickname or user_data.username,
        )
        db.add(user)
        db.commit()
        db.refresh(user)
        
        # 创建默认仪表盘配置
        default_config = DashboardConfig(
            user_id=user.id,
            name="默认配置",
            is_default=True,
            enabled_widgets=["market_indices", "news", "ai_advice"],
            refresh_interval=30,
        )
        db.add(default_config)
        
        # 创建默认偏好设置
        preferences = UserPreference(
            user_id=user.id,
            preferences={
                "language": "zh-CN",
                "timezone": "Asia/Shanghai",
                "default_market": "A",
                "show_help_tips": True,
                "auto_refresh": True,
            }
        )
        db.add(preferences)
        
        db.commit()
        
        return user


@router.post("/login", response_model=Token)
async def login(form_data: OAuth2PasswordRequestForm = Depends()):
    """用户登录"""
    with get_db_context() as db:
        # 查找用户
        user = db.query(User).filter(User.username == form_data.username).first()
        if not user or not verify_password(form_data.password, user.password_hash):
            raise HTTPException(
                status_code=401,
                detail="用户名或密码错误",
                headers={"WWW-Authenticate": "Bearer"},
            )
        
        # 检查账户状态
        if not user.is_active:
            raise HTTPException(
                status_code=403,
                detail="账户已被禁用"
            )
        
        # 更新最后登录时间
        user.last_login_at = datetime.utcnow()
        db.commit()
        
        # 创建访问令牌
        access_token = create_access_token(
            data={"sub": user.username},
            expires_delta=timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
        )
        
        return {
            "access_token": access_token,
            "token_type": "bearer",
            "expires_in": ACCESS_TOKEN_EXPIRE_MINUTES * 60
        }


@router.get("/me", response_model=UserResponse)
async def get_me(current_user: User = Depends(get_current_user)):
    """获取当前用户信息"""
    return current_user


@router.put("/me")
async def update_profile(
    nickname: Optional[str] = None,
    avatar_url: Optional[str] = None,
    current_user: User = Depends(get_current_user)
):
    """更新用户资料"""
    with get_db_context() as db:
        if nickname is not None:
            current_user.nickname = nickname
        if avatar_url is not None:
            current_user.avatar_url = avatar_url
        
        db.commit()
        db.refresh(current_user)
        
        return {"message": "更新成功", "user": current_user}
