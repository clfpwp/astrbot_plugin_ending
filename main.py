import os
import json
import random
import time
import asyncio
from astrbot.api.event import filter, AstrMessageEvent
from astrbot.api.star import Context, Star, register

@register("astrbot_plugin_ending", "Cl_Fu", "每日随机doro结局插件", "1.0.0")
class DailyEndingPlugin(Star):
    def __init__(self, context: Context):
        super().__init__(context)
        self.ending_dir = os.path.join(os.path.dirname(__file__), "ending")
        self.data_file = os.path.join(os.path.dirname(__file__), "ending_data.json")
        
        self.load_data()
        asyncio.create_task(self.reset_data_daily())

    def load_data(self):
        if os.path.exists(self.data_file):
            try:
                with open(self.data_file, "r", encoding="utf-8") as f:
                    self.ending_data = json.load(f)
            except json.JSONDecodeError:
                self.ending_data = {}
        else:
            self.ending_data = {}

    def save_data(self):
        with open(self.data_file, "w", encoding="utf-8") as f:
            json.dump(self.ending_data, f, indent=4, ensure_ascii=False)

    async def reset_data_daily(self):
        while True:
            now = time.localtime()
            seconds_until_midnight = (24 - now.tm_hour) * 3600 - now.tm_min * 60 - now.tm_sec
            await asyncio.sleep(seconds_until_midnight)  
            self.ending_data = {}  
            self.save_data()
            print("每日结局数据已清空")  

    @filter.command("今日结局")
    async def daily_ending(self, event: AstrMessageEvent):
        user_id = str(event.get_sender_id())  

        if user_id in self.ending_data:
            image_path = self.ending_data[user_id]
        else:
            images = [f for f in os.listdir(self.ending_dir) if f.lower().endswith(('.png', '.jpg', '.jpeg', '.gif'))]
            if not images:
                yield event.plain_result("没有找到结局图片！")
                return
            image_path = os.path.join(self.ending_dir, random.choice(images))
            
            self.ending_data[user_id] = image_path
            self.save_data()

        yield event.image_result(image_path)

