import datetime
import logging

logger = logging.getLogger(__name__)

# Простая in-memory база данных
class SimpleDB:
    def __init__(self):
        self.orders = {}
        self.referrals = {}
        self.order_counter = 1
    
    async def create_order(self, user_id: int, username: str, tariff: str, webapp_query_id: str = None):
        order_id = self.order_counter
        self.order_counter += 1
        
        order = {
            'id': order_id,
            'user_id': user_id,
            'username': username,
            'tariff': tariff,
            'status': 'wait',
            'created_at': datetime.datetime.utcnow(),
            'webapp_query_id': webapp_query_id,
            'sui_username': None,
            'expiry_date': None,
            'server_location': 'Xferant Sweden'
        }
        
        self.orders[order_id] = order
        return order
    
    async def get_order(self, order_id: int):
        return self.orders.get(order_id)
    
    async def update_order_status(self, order_id: int, status: str, sui_username: str = None, days: int = None):
        if order_id in self.orders:
            self.orders[order_id]['status'] = status
            if sui_username:
                self.orders[order_id]['sui_username'] = sui_username
            if days:
                self.orders[order_id]['expiry_date'] = datetime.datetime.utcnow() + datetime.timedelta(days=days)
            return True
        return False
    
    async def get_orders_by_status(self, status: str = None):
        if status:
            return [order for order in self.orders.values() if order['status'] == status]
        return list(self.orders.values())
    
    async def create_referral(self, referrer_id: int, referred_id: int):
        referral_id = len(self.referrals) + 1
        referral = {
            'id': referral_id,
            'referrer_id': referrer_id,
            'referred_id': referred_id,
            'bonus_activated': False,
            'created_at': datetime.datetime.utcnow()
        }
        self.referrals[referral_id] = referral
        return referral
    
    async def get_referrals_by_referrer(self, referrer_id: int):
        return [ref for ref in self.referrals.values() if ref['referrer_id'] == referrer_id]
    
    async def get_referral_count(self, referrer_id: int):
        return len([ref for ref in self.referrals.values() if ref['referrer_id'] == referrer_id])

# Глобальная база данных
db = SimpleDB()

async def create_vpn_user(order_id: int, days: int) -> str:
    """Создать пользователя и сгенерировать ссылку для Xferant VPN"""
    username = f"xferant_{order_id}"
    
    try:
        from bot.config import VPN_SERVER, VPN_OBFS_PASSWORD, VPN_SNI, VPN_PORT, VPN_SERVER_NAME
        
        # Обновляем заказ
        await db.update_order_status(order_id, 'done', username, days)
        
        return f"hysteria2://{username}@{VPN_SERVER}:{VPN_PORT}?sni={VPN_SNI}&obfs=salamander&obfs-password={VPN_OBFS_PASSWORD}&fastopen=0&downmbps=270&upmbps=270&security=tls&insecure=1#{VPN_SERVER_NAME}_{username.upper()}"
    
    except Exception as e:
        logger.error(f"Error creating VPN user for Xferant: {e}")
    
    return None

async def init_db():
    logger.info("Xferant VPN database initialized successfully")
