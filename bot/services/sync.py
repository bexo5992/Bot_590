# bot/services/sync.py
import json
import tempfile
import os
from datetime import datetime
from typing import List, Dict, Any
from bot.utils.logger import logger
from bot.config import Config
import aiohttp
import asyncio

class SyncService:
    """خدمة المزامنة مع بوت قاعدة البيانات"""
    
    def __init__(self):
        self.db_token = Config.DB_BOT_TOKEN
        self.admin_id = Config.ADMIN_ID
        self.group_id = Config.GROUP_CHAT_ID
    
    async def send_data(self, action: str, data_list: List[Dict], retries: int = 3) -> bool:
        """إرسال البيانات إلى بوت قاعدة البيانات"""
        if not data_list:
            return True
        
        # تقسيم إلى دفعات
        batch_size = Config.BATCH_SIZE
        for i in range(0, len(data_list), batch_size):
            batch = data_list[i:i+batch_size]
            
            for attempt in range(retries):
                try:
                    # إنشاء ملف مؤقت
                    with tempfile.NamedTemporaryFile(
                        mode='w', 
                        suffix='.json', 
                        delete=False
                    ) as f:
                        json.dump({
                            'action': action,
                            'data': batch,
                            'batch': i//batch_size + 1,
                            'total_batches': (len(data_list) + batch_size - 1) // batch_size
                        }, f, ensure_ascii=False, indent=2)
                        temp_path = f.name
                    
                    # إرسال عبر API
                    await self._send_file(temp_path, action)
                    
                    # حذف الملف المؤقت
                    os.unlink(temp_path)
                    
                    logger.info(f"✅ Synced {action}: {len(batch)} records")
                    return True
                    
                except Exception as e:
                    logger.error(f"Sync attempt {attempt+1} failed: {e}")
                    await asyncio.sleep(2 ** attempt)  # تأخير متزايد
            
            return False
        
        return True
    
    async def _send_file(self, file_path: str, action: str):
        """إرسال الملف إلى بوت قاعدة البيانات"""
        # هنا يمكن إرسال الملف عبر API أو عبر البوت نفسه
        # هذا يعتمد على تصميمك
        pass
