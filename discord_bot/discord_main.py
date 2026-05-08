from events import Events_Handler, Run, RunChild, Event
import discord
from quick_ini import QuickIni
from discord.ext import commands
import threading
import json

QuickIni.load_file("config.ini")
TOKEN = QuickIni.get_value("discord_token")

intents = discord.Intents.default()
intents.message_content = True

_run_instance: 'DiscordRun' = None

bot = commands.Bot(command_prefix="!", intents=intents, help_command=None)

# account: {
# "email": str,
# "key": str,
# "notes": str,
# "status": str, # TUT, BASE, OUT, DIS
# "twin": bool (optional)
# }
__DEFAULT_JSON_CONFIG = {
    "accounts": []
}
def config_get_create(path:str) -> dict:
    try:
        with open(path, "r") as f: return json.load(f)
    except FileNotFoundError:
        with open(path, "w") as f: json.dump(__DEFAULT_JSON_CONFIG, f)
        return __DEFAULT_JSON_CONFIG.copy()

class Account_Manager():
    def __init__(self, config_path:str):
        self.config_path = config_path
        self.config = config_get_create(config_path)
        self.accounts:dict[str, dict] = {}

        for acc in self.config["accounts"]:
            account = {"email": acc["email"], "key": acc["key"], "status": acc["status"]}
            self.accounts[account["email"]] = account

    def add_account(self, email:str, key:str, status:str = "DIS") -> dict:
        account = {"email": email, "key": key, "status": status, "notes": ""}
        self.accounts[account["email"]] = account
        self._save_config()
        return account
    def set_account_status(self, email:str, status:str) -> bool:
        account = self.accounts.get(email)
        if not account: return False
        account["status"] = status
        self._save_config()
        return True
    def set_account_notes(self, email:str, notes:str) -> bool:
        account = self.accounts.get(email)
        if not account: return False
        account["notes"] = notes
        self._save_config()
        return True
    def remove_account(self, email:str) -> bool:
        if email in self.accounts:
            del self.accounts[email]
            self._save_config()
            return True
        return False
    def get_account(self, email:str) -> dict:
        return self.accounts.get(email)

    def _save_config(self):
        with open(self.config_path, "w") as f:
            json.dump({
                "accounts": [acc for acc in self.accounts.values()]
            }, f, indent=2)

class DiscordRun(RunChild):
    def start(self):
        print("Starting Discord Run")
        global _run_instance
        _run_instance = self

        self.account_manager = Account_Manager(self.get_self_path() + "/accounts.json")

        self.bot_thread = threading.Thread(target=bot.run, daemon=True, args=(TOKEN,))
        self.bot_thread.start()

        self._send_all_account_statuses()
    
    def stop(self): pass # STOP BOT

    def _send_all_account_statuses(self):
        for account in self.account_manager.accounts.values():
            self.events_handler.emit("update_account_status", {
                "email": account["email"],
                "status": account["status"]
            })

    # ========== Event Handlers ==========
    def handle_get_accounts(self, event: Event):
        self.events_handler.consume(event)
        for account in self.account_manager.accounts.values():
            self.events_handler.emit("add_account", {
                "email": account["email"],
                "key": account["key"],
                "twin": None
            })
            self._send_all_account_statuses()
    # ====================================

    def tick(self):
        for e in self.events_handler.get_events():
            if(e.matches("get_accounts")): self.handle_get_accounts(e)

@bot.event
async def on_ready():
    print(f'{bot.user} has connected to Discord!')

@bot.command()
async def ping(ctx):
    await ctx.send('Pong!')

@bot.command()
async def help(ctx):
    help_message = (
        "Available commands:\n"
        "!ping - Check if the bot is responsive.\n"
        "!help - Show this help message.\n"
        "!status - Show the status of all accounts.\n"
    )
    await ctx.send(help_message)
