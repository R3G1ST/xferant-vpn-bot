import aiohttp
import logging
from bot.config import SUI_API_URL, SUI_API_KEY

logger = logging.getLogger(__name__)

class SUIAPI:
    def __init__(self):
        self.base_url = SUI_API_URL
        self.api_key = SUI_API_KEY
        self.headers = {
            "Authorization": f"Bearer {self.api_key}", 
            "Content-Type": "application/json"
        } if self.api_key else {}
    
    async def create_user(self, username: str, days: int, traffic_limit_gb: int = 500):
        """Создать пользователя в S-UI"""
        if not self.api_key:
            logger.warning("S-UI API key not configured, using mock user creation")
            return {"username": username, "status": "mock_created"}
        
        payload = {
            "username": username,
            "expire_date": days,
            "traffic_limit": traffic_limit_gb * 1024 * 1024 * 1024,
            "enable": True
        }
        
        try:
            async with aiohttp.ClientSession() as session:
                async with session.post(
                    f"{self.base_url}/users", 
                    json=payload, 
                    headers=self.headers
                ) as resp:
                    if resp.status == 201:
                        data = await resp.json()
                        logger.info(f"Created S-UI user: {username}")
                        return data
                    else:
                        error_text = await resp.text()
                        logger.error(f"S-UI API error: {resp.status} - {error_text}")
                        return None
        except Exception as e:
            logger.error(f"S-UI connection error: {e}")
            return None
    
    async def get_user_stats(self, username: str):
        """Получить статистику пользователя"""
        if not self.api_key:
            return {"username": username, "used_traffic": 0, "status": "mock"}
        
        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(
                    f"{self.base_url}/users/{username}", 
                    headers=self.headers
                ) as resp:
                    if resp.status == 200:
                        return await resp.json()
                    return None
        except Exception as e:
            logger.error(f"S-UI stats error: {e}")
            return None
    
    async def delete_user(self, username: str):
        """Удалить пользователя"""
        if not self.api_key:
            return True
        
        try:
            async with aiohttp.ClientSession() as session:
                async with session.delete(
                    f"{self.base_url}/users/{username}", 
                    headers=self.headers
                ) as resp:
                    return resp.status == 200
        except Exception as e:
            logger.error(f"S-UI delete error: {e}")
            return False

sui_client = SUIAPI()
