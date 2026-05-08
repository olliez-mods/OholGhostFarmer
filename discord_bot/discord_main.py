from events import Events_Handler, Run, RunChild, Event
import discord
from quick_ini import QuickIni
from discord.ext import commands
import threading
import asyncio
import json

QuickIni.load_file("config.ini")
TOKEN = QuickIni.get_value("discord_token")

intents = discord.Intents.default()
intents.message_content = True

_run_instance: 'DiscordRun' = None

bot = commands.Bot(command_prefix="!", intents=intents, help_command=None)
last_used_channel = None

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
        self.accounts:list[dict] = []

        found_housekeeper = False
        for acc in self.config["accounts"]:
            account = {"email": acc["email"], "key": acc["key"], "status": acc["status"], "notes": acc["notes"]}
            # Consistenly put the housekeeper account first
            if not found_housekeeper and "housekeeper" in acc["notes"].lower().replace(" ", ""):
                self.accounts.insert(0, account)
                found_housekeeper = True
            else: self.accounts.append(account)

    def _find(self, email:str) -> dict | None:
        return next((a for a in self.accounts if a["email"] == email), None)

    def add_account(self, email:str, key:str, status:str = "DIS") -> dict:
        account = {"email": email, "key": key, "status": status, "notes": ""}
        self.accounts.append(account)
        self._save_config()
        return account
    def set_account_status(self, email:str, status:str) -> bool:
        account = self._find(email)
        if not account: return False
        account["status"] = status
        self._save_config()
        return True
    def set_account_notes(self, email:str, notes:str) -> bool:
        account = self._find(email)
        if not account: return False
        account["notes"] = notes
        self._save_config()
        return True
    def remove_account(self, email:str) -> bool:
        account = self._find(email)
        if account:
            self.accounts.remove(account)
            self._save_config()
            return True
        return False
    def get_account(self, email:str) -> dict:
        return self._find(email)

    def _save_config(self):
        with open(self.config_path, "w") as f:
            json.dump({"accounts": self.accounts}, f, indent=2)

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
        for account in self.account_manager.accounts:
            self.events_handler.emit("update_account_status", {
                "email": account["email"],
                "status": account["status"]
            })

    # ========== Event Handlers ==========
    def handle_get_accounts(self, event: Event):
        self.events_handler.consume(event)
        for account in self.account_manager.accounts:
            self.events_handler.emit("add_account", {
                "email": account["email"],
                "key": account["key"],
                "twin": None
            })
            self._send_all_account_statuses()
    
    def handle_ghost_created(self, event: Event):
        self.events_handler.consume(event)
        email = event.data.get("email")
        if not email: raise Exception("on_ghost_created event missing email", event)
        asyncio.run_coroutine_threadsafe(_send_message(f"Ghost created for account {email}"), bot.loop)
    # ====================================

    def tick(self):
        for e in self.events_handler.get_events():
            if(e.matches("get_accounts")): self.handle_get_accounts(e)
            if(e.matches("ghost_created")): self.handle_ghost_created(e)

def update_last_used_channel(ctx):
    global last_used_channel
    last_used_channel = ctx.channel

async def _send_message(message:str):
    if last_used_channel:
        await last_used_channel.send(message)

@bot.event
async def on_ready():
    print(f'{bot.user} has connected to Discord!')

@bot.command()
async def ping(ctx):
    update_last_used_channel(ctx)
    await ctx.send('Pong!')

@bot.command()
async def help(ctx):
    update_last_used_channel(ctx)
    help_message = (
        "Available commands:\n"
        "!ping - Check if the bot is responsive.\n"
        "!help - Show this help message.\n"
        "!status - Show the status of all accounts.\n"
        "!setstatus <index> <status> - Set the status of an account. Status can be TUT, BASE, OUT, DIS.\n"
        "!setnotes <index> <notes> - Set the notes for an account.\n"
        "!addaccount <email> <key> - Add a new account.\n"
        "!removeaccount <index> - Remove an account."
    )
    await ctx.send(help_message)

@bot.command()
async def status(ctx):
    update_last_used_channel(ctx)
    status_message = "Account Statuses:\n"
    index = 1
    for account in _run_instance.account_manager.accounts:
        status_message += f"{index}. [{account['notes']}]: {account['status']}"

        if(account["status"] == "TUT"):
            e = _run_instance.events_handler.request("get_tut_status", {"email": account["email"]})
            if(e):
                if(e.data.get("in_game")):
                    status_message += f" {round(e.data.get("age"), 1)}yo"
                    if(e.data.get("is_ghost")): status_message += " (GHOST)"
                else: status_message += " (Not in game)"
        status_message += "\n"
        index += 1
    await ctx.send(status_message)

@bot.command()
async def setstatus(ctx, index: int, status: str):
    update_last_used_channel(ctx)
    index = int(index) - 1
    if(index < 0 or index >= len(_run_instance.account_manager.accounts)):
        await ctx.send("Invalid account index.")
        return
    account = _run_instance.account_manager.accounts[index]
    status = status.upper()
    if(status not in ("TUT", "BASE", "OUT", "DIS")):
        await ctx.send("Invalid status. Valid statuses are: TUT, BASE, OUT, DIS.")
        return
    _run_instance.account_manager.set_account_status(account["email"], status)
    _run_instance.events_handler.emit("update_account_status", {
        "email": account["email"],
        "status": status
    })
    await ctx.send(f"Set status of [{account['notes']}] to {status}.")

@bot.command()
async def setnotes(ctx, index: int, *, notes: str):
    update_last_used_channel(ctx)
    index = int(index) - 1
    if(index < 0 or index >= len(_run_instance.account_manager.accounts)):
        await ctx.send("Invalid account index.")
        return
    account = _run_instance.account_manager.accounts[index]
    _run_instance.account_manager.set_account_notes(account["email"], notes)
    await ctx.send(f"Set notes of [{account['email']}] to {notes}.")

@bot.command()
async def addaccount(ctx, email: str, key: str):
    update_last_used_channel(ctx)
    account = _run_instance.account_manager.add_account(email, key)
    _run_instance.events_handler.emit("add_account", {
        "email": account["email"],
        "key": account["key"],
        "twin": None
    })
    await ctx.send(f"Added account {email}.")

@bot.command()
async def removeaccount(ctx, index: int):
    update_last_used_channel(ctx)
    index = int(index) - 1
    if(index < 0 or index >= len(_run_instance.account_manager.accounts)):
        await ctx.send("Invalid account index.")
        return
    account = _run_instance.account_manager.accounts[index]
    _run_instance.account_manager.remove_account(account["email"])
    _run_instance.events_handler.emit("remove_account", {
        "email": account["email"]
    })
    await ctx.send(f"Removed account {account['email']}.")

