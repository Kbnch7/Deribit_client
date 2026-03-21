import json
import uuid
from redis import Redis

def add_notification_to_redis(r: Redis, user_id: int, ticker: str, target_price: float, current_price: float):
    notification_id = str(uuid.uuid4())
    
    payload = {
        "id": notification_id,
        "user_id": user_id,
        "ticker": ticker,
        "target_price": target_price
    }
    
    json_payload = json.dumps(payload)
    
    if float(target_price) > float(current_price):
        key = f"notifs:up:{ticker}"
        direction = "up"
    else:
        key = f"notifs:down:{ticker}"
        direction = "down"
    
    r.zadd(key, {json_payload: target_price})
    
    return json_payload, direction

def get_notifications_from_redis(r: Redis, ticker: str, current_price: float):
    lua_get_delete = """
    local result = redis.call('ZRANGEBYSCORE', KEYS[1], ARGV[1], ARGV[2])
    if #result > 0 then
        redis.call('ZREMRANGEBYSCORE', KEYS[1], ARGV[1], ARGV[2])
    end
    return result
    """
    
    script = r.register_script(lua_get_delete)
    
    up = script(keys=[f"notifs:up:{ticker}"], args=["-inf", current_price])
    down = script(keys=[f"notifs:down:{ticker}"], args=[current_price, "inf"])
    
    return up + down