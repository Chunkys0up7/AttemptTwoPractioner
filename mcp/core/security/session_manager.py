import logging
from datetime import datetime
from mcp.core.security.jwt_manager import JWTManager

logger = logging.getLogger("audit")
handler = logging.FileHandler("audit.log")
formatter = logging.Formatter('%(asctime)s %(levelname)s %(message)s')
handler.setFormatter(formatter)
logger.addHandler(handler)
logger.setLevel(logging.INFO)

class SessionManager:
    @staticmethod
    def create_session(user_id: int) -> str:
        token = JWTManager.create_access_token({"sub": str(user_id)})
        logger.info(f"LOGIN user_id={user_id}")
        return token

    @staticmethod
    def revoke_session(user_id: int):
        # In a real system, implement token blacklist or revocation
        logger.info(f"LOGOUT user_id={user_id}")

    @staticmethod
    def audit_action(user_id: int, action: str, details: str = ""):
        logger.info(f"AUDIT user_id={user_id} action={action} details={details}")

session_manager = SessionManager() 