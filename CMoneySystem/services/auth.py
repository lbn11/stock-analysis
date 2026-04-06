"""用户认证和授权模块

提供用户注册、登录、权限管理等功能
"""
from typing import Dict, List, Any, Optional
from datetime import datetime, timedelta
import logging
import hashlib
import secrets
import json

try:
    import jwt
    JWT_AVAILABLE = True
except ImportError:
    JWT_AVAILABLE = False
    logging.warning("PyJWT not installed. Install with: pip install pyjwt")


class User:
    """用户模型"""

    def __init__(self, user_id: str, username: str, email: str,
                 password_hash: str, role: str = 'user'):
        """
        初始化用户

        Args:
            user_id: 用户ID
            username: 用户名
            email: 邮箱
            password_hash: 密码哈希
            role: 角色 (user, admin, premium)
        """
        self.user_id = user_id
        self.username = username
        self.email = email
        self.password_hash = password_hash
        self.role = role
        self.created_at = datetime.now()
        self.is_active = True
        self.last_login = None

    def to_dict(self) -> Dict[str, Any]:
        """转换为字典（不包含敏感信息）"""
        return {
            'user_id': self.user_id,
            'username': self.username,
            'email': self.email,
            'role': self.role,
            'created_at': self.created_at.isoformat(),
            'is_active': self.is_active,
            'last_login': self.last_login.isoformat() if self.last_login else None
        }


class UserService:
    """用户服务"""

    def __init__(self):
        self.logger = logging.getLogger("UserService")
        self.users: Dict[str, User] = {}  # user_id -> User
        self.username_index: Dict[str, str] = {}  # username -> user_id
        self.email_index: Dict[str, str] = {}  # email -> user_id

    def hash_password(self, password: str) -> str:
        """哈希密码"""
        return hashlib.sha256(password.encode()).hexdigest()

    def verify_password(self, password: str, password_hash: str) -> bool:
        """验证密码"""
        return self.hash_password(password) == password_hash

    def create_user(self, username: str, email: str, password: str,
                   role: str = 'user') -> Optional[User]:
        """
        创建新用户

        Args:
            username: 用户名
            email: 邮箱
            password: 密码
            role: 角色

        Returns:
            用户对象，失败返回None
        """
        # 检查用户名是否已存在
        if username in self.username_index:
            self.logger.warning(f"Username {username} already exists")
            return None

        # 检查邮箱是否已存在
        if email in self.email_index:
            self.logger.warning(f"Email {email} already exists")
            return None

        # 创建用户
        user_id = secrets.token_hex(16)
        password_hash = self.hash_password(password)

        user = User(user_id, username, email, password_hash, role)

        # 保存用户
        self.users[user_id] = user
        self.username_index[username] = user_id
        self.email_index[email] = user_id

        self.logger.info(f"User created: {username} ({user_id})")
        return user

    def get_user(self, user_id: str) -> Optional[User]:
        """获取用户"""
        return self.users.get(user_id)

    def get_user_by_username(self, username: str) -> Optional[User]:
        """通过用户名获取用户"""
        user_id = self.username_index.get(username)
        return self.users.get(user_id) if user_id else None

    def get_user_by_email(self, email: str) -> Optional[User]:
        """通过邮箱获取用户"""
        user_id = self.email_index.get(email)
        return self.users.get(user_id) if user_id else None

    def authenticate(self, username: str, password: str) -> Optional[User]:
        """
        认证用户

        Args:
            username: 用户名
            password: 密码

        Returns:
            认证成功返回用户对象，失败返回None
        """
        user = self.get_user_by_username(username)

        if not user:
            self.logger.warning(f"Authentication failed: user {username} not found")
            return None

        if not user.is_active:
            self.logger.warning(f"Authentication failed: user {username} is inactive")
            return None

        if not self.verify_password(password, user.password_hash):
            self.logger.warning(f"Authentication failed: invalid password for {username}")
            return None

        # 更新最后登录时间
        user.last_login = datetime.now()

        self.logger.info(f"User {username} authenticated successfully")
        return user


class TokenManager:
    """Token管理器"""

    def __init__(self, secret_key: str = None):
        """
        初始化Token管理器

        Args:
            secret_key: JWT密钥（自动生成如果未提供）
        """
        self.logger = logging.getLogger("TokenManager")
        self.secret_key = secret_key or secrets.token_hex(32)
        self.algorithm = 'HS256'
        self.token_expiry = timedelta(hours=24)

    def generate_token(self, user: User, expiry_hours: int = 24) -> Optional[str]:
        """
        生成JWT Token

        Args:
            user: 用户对象
            expiry_hours: 过期时间（小时）

        Returns:
            JWT Token字符串
        """
        if not JWT_AVAILABLE:
            self.logger.error("PyJWT not installed")
            return None

        try:
            payload = {
                'user_id': user.user_id,
                'username': user.username,
                'role': user.role,
                'iat': datetime.utcnow(),
                'exp': datetime.utcnow() + timedelta(hours=expiry_hours)
            }

            token = jwt.encode(payload, self.secret_key, algorithm=self.algorithm)

            self.logger.info(f"Token generated for user {user.username}")
            return token

        except Exception as e:
            self.logger.error(f"Error generating token: {e}")
            return None

    def verify_token(self, token: str) -> Optional[Dict[str, Any]]:
        """
        验证JWT Token

        Args:
            token: JWT Token字符串

        Returns:
            解码后的payload，验证失败返回None
        """
        if not JWT_AVAILABLE:
            self.logger.error("PyJWT not installed")
            return None

        try:
            payload = jwt.decode(token, self.secret_key, algorithms=[self.algorithm])
            self.logger.info("Token verified successfully")
            return payload

        except jwt.ExpiredSignatureError:
            self.logger.warning("Token expired")
            return None

        except jwt.InvalidTokenError as e:
            self.logger.warning(f"Invalid token: {e}")
            return None


class PermissionManager:
    """权限管理器"""

    def __init__(self):
        self.logger = logging.getLogger("PermissionManager")

        # 角色权限定义
        self.role_permissions = {
            'user': [
                'api:analyze',
                'api:predict',
                'api:factors',
                'task:submit',
                'task:get_status'
            ],
            'premium': [
                'api:analyze',
                'api:predict',
                'api:factors',
                'task:submit',
                'task:get_status',
                'api:batch_analysis',
                'api:advanced_models'
            ],
            'admin': [
                'api:analyze',
                'api:predict',
                'api:factors',
                'task:submit',
                'task:get_status',
                'api:batch_analysis',
                'api:advanced_models',
                'admin:users',
                'admin:tasks',
                'admin:stats'
            ]
        }

    def has_permission(self, role: str, permission: str) -> bool:
        """
        检查角色是否有权限

        Args:
            role: 用户角色
            permission: 权限名称

        Returns:
            是否有权限
        """
        permissions = self.role_permissions.get(role, [])
        return permission in permissions

    def check_permissions(self, role: str, required_permissions: List[str]) -> bool:
        """
        检查角色是否拥有所有必需权限

        Args:
            role: 用户角色
            required_permissions: 需要的权限列表

        Returns:
            是否拥有所有权限
        """
        user_permissions = self.role_permissions.get(role, [])

        for perm in required_permissions:
            if perm not in user_permissions:
                return False

        return True


class AuthService:
    """认证服务

    整合用户服务、Token管理和权限管理
    """

    def __init__(self, secret_key: str = None):
        """
        初始化认证服务

        Args:
            secret_key: JWT密钥
        """
        self.logger = logging.getLogger("AuthService")
        self.user_service = UserService()
        self.token_manager = TokenManager(secret_key)
        self.permission_manager = PermissionManager()

    def register(self, username: str, email: str, password: str,
                role: str = 'user') -> Dict[str, Any]:
        """
        用户注册

        Args:
            username: 用户名
            email: 邮箱
            password: 密码
            role: 角色

        Returns:
            注册结果
        """
        try:
            # 创建用户
            user = self.user_service.create_user(username, email, password, role)

            if not user:
                return {
                    'success': False,
                    'message': '用户名或邮箱已存在'
                }

            # 生成token
            token = self.token_manager.generate_token(user)

            return {
                'success': True,
                'message': '注册成功',
                'user': user.to_dict(),
                'token': token
            }

        except Exception as e:
            self.logger.error(f"Registration error: {e}")
            return {
                'success': False,
                'message': f'注册失败: {str(e)}'
            }

    def login(self, username: str, password: str) -> Dict[str, Any]:
        """
        用户登录

        Args:
            username: 用户名
            password: 密码

        Returns:
            登录结果
        """
        try:
            # 认证用户
            user = self.user_service.authenticate(username, password)

            if not user:
                return {
                    'success': False,
                    'message': '用户名或密码错误'
                }

            # 生成token
            token = self.token_manager.generate_token(user)

            return {
                'success': True,
                'message': '登录成功',
                'user': user.to_dict(),
                'token': token
            }

        except Exception as e:
            self.logger.error(f"Login error: {e}")
            return {
                'success': False,
                'message': f'登录失败: {str(e)}'
            }

    def verify_token(self, token: str) -> Dict[str, Any]:
        """
        验证Token

        Args:
            token: JWT Token

        Returns:
            验证结果
        """
        payload = self.token_manager.verify_token(token)

        if not payload:
            return {
                'valid': False,
                'message': 'Token无效或已过期'
            }

        # 获取用户信息
        user = self.user_service.get_user(payload['user_id'])

        if not user or not user.is_active:
            return {
                'valid': False,
                'message': '用户不存在或已被禁用'
            }

        return {
            'valid': True,
            'user': user.to_dict(),
            'role': payload['role']
        }

    def check_permission(self, token: str, permission: str) -> bool:
        """
        检查权限

        Args:
            token: JWT Token
            permission: 权限名称

        Returns:
            是否有权限
        """
        result = self.verify_token(token)

        if not result['valid']:
            return False

        role = result['role']
        return self.permission_manager.has_permission(role, permission)


# 全局认证服务实例
global_auth_service = AuthService()


def require_auth(permission: str = None):
    """
    装饰器：要求认证

    Args:
        permission: 需要的权限（可选）
    """
    def decorator(func):
        def wrapper(*args, **kwargs):
            # 从kwargs获取token
            token = kwargs.get('token')

            if not token:
                return {
                    'success': False,
                    'message': '缺少认证token'
                }

            # 验证token
            result = global_auth_service.verify_token(token)

            if not result['valid']:
                return {
                    'success': False,
                    'message': '认证失败'
                }

            # 检查权限
            if permission:
                role = result['role']
                if not global_auth_service.permission_manager.has_permission(role, permission):
                    return {
                        'success': False,
                        'message': '权限不足'
                    }

            # 将用户信息添加到kwargs
            kwargs['current_user'] = result['user']

            # 执行原函数
            return func(*args, **kwargs)

        return wrapper
    return decorator
