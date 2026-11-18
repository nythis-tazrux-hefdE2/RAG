"""用户环境生命周期的持久锁键。"""


def user_environment_lock_key(uid: str) -> str:
    """用户环境生命周期与执行领取共同使用的锁键。"""
    return f"user-environment:{uid}"
