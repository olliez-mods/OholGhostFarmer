from events import Events_Handler, Run, RunChild, Event
from quick_ini import QuickIni

from EllaBotLib import bot, defaultActions, functions
import EllaBotLib as Ella
from shared.customActions import *
from shared.account import OholAccount

QuickIni.load_file("config.ini")
DATA_PATH = QuickIni.get_value("data7_path", "C:/OneLifeData7")

HUNGER_SECONDS_BUFFER = 120 # Login this many seconds before we expect the account to run out of hunger
SECONDS_PER_PIP = 39

class GhostBaseRun(RunChild):
    def start(self):
        print("Starting Ghost Base Run sorry")

        num_items = Ella.load_items_from_raw(DATA_PATH)
        if(not num_items): raise Exception("Failed to load items from data7.")
        print(f"Loaded {num_items} items.")

        Ella.set_action_manager_logging(failures=True, starts=True, completions=True)

        self.oholAccounts:list[OholAccount] = []
        self.events_handler.emit("get_accounts")

    # ========== Event Handlers ==========
    def handle_add_account(self, event: Event):
        email = event.data.get("email")
        key = event.data.get("key")
        do_twin = event.data.get("twin", None)
        if(not email or not key): raise Exception("add_account event missing email or key", event)
        for acc in self.oholAccounts:
            if(acc.email == email): return
        account = OholAccount(email, key, twin=do_twin)
        self.oholAccounts.append(account)
        print(f"Added account {email}")
    def handle_remove_account(self, event: Event):
        email = event.data.get("email")
        if(not email): raise Exception("remove_account event missing email", event)
        for i, account in enumerate(self.oholAccounts):
            if(account.email == email):
                del self.oholAccounts[i]
                print(f"Removed account {email}")
                return
    def handle_update_account_status(self, event: Event):
        email = event.data.get("email")
        status = event.data.get("status")
        if(not email or not status): raise Exception("update_account_status event missing email or status", event)
        for account in self.oholAccounts:
            if(account.email == email):
                account.set_status(status)
                print(f"Updated account {email} status to {status}")
                return
    # ====================================

    def _should_account_login(self, account: OholAccount) -> bool:
        if(account.status != "BASE"): return False
        if(account.bot.logged_in and account.bot.sock_alive): return False
        if(not account.estimated_time_of_hunger or not account.last_login_time): return True # Login instantly
        if(time.time() - account.last_login_time > 7200): return True # Every 2 hours so we can re-calculate hunger time
        if(time.time() >= account.estimated_time_of_hunger - HUNGER_SECONDS_BUFFER): return True
        return False

    def _should_account_logout(self, account: OholAccount) -> bool:
        if(not account.bot.logged_in): return False
        if(account.status != "BASE"): return True
        if(time.time() - account.last_login_time > 600): return True # Logout if logged in for more than 8 minutes
        return False

    def _should_bot_get_food(self, account: OholAccount) -> bool:
        pips_left = account.bot.food_left + account.bot.yum_bonus
        if(not account.bot.action_manager.is_complete()): return False # Maybe we are already getting food
        if(pips_left < account.bot.max_food - 2): return True
        return False

    def handle_bot_tick(self, account: OholAccount):
        bot = account.bot
        p = bot.handle_next_packet()

        if(self._should_account_login(account)):
            print(f"Logging in account {account.email}...")
            bot.reset_bot(preserve_login_info=True)
            bot.reset_flags()
            bot.login(tutorial_num=1)
            account.last_login_time = time.time()

        if(self._should_account_logout(account)):
            print(f"Logging out account {account.email}...")
            bot.unlogin()
            return

        if(bot.logged_in and not bot.login_proccess):
            bot.action_manager.tick()

            # Food left, is initially set to 9999 before we are told how much food we have
            if(bot.food_left < 999 and bot.ensure_single_run("update_hunger_estimate")):
                pips = bot.food_left + bot.yum_bonus
                estimate_seconds_before_hunger = SECONDS_PER_PIP * (pips - bot.max_food + 2) # We will have max_food - 2 pips (no yum bonus)
                account.estimated_time_of_hunger = time.time() + estimate_seconds_before_hunger

            if(bot.current_craving_id > 0 and bot.ensure_single_run("update_craving_info")):
                item = ObjectMap.get_item_given_id(bot.current_craving_id)
                if(not item): raise Exception(f"Failed to find item for craving id {bot.current_craving_id}")
                account.last_craving_item_desc = item.description

            if(self._should_bot_get_food(account)): # We have 2 hunger pips open, EAT! :)
                home_tile = bot.live_player.xy
                yum_id = bot.current_craving_id
                yum_item = ObjectMap.get_item_given_id(yum_id)
                if(not yum_item): raise Exception(f"Failed to find item for craving id {yum_id}")
                yum_desc = yum_item.description
                print(f"Account {account.email} is hungry! Getting food with yum {yum_desc}...")

                # Grab the food (presumablely it's in one of our yum boxes) and eat it
                bot.action_manager.add_actions(
                    Get_Item_Action(yum_desc),
                    Wait_For_Hunger(),
                    Send_Interaction_Action("self"),
                    Walk_To_Action(home_tile),
                    chain_id="get_food"
                )

    def tick(self):
        for e in self.events_handler.get_events():
            if(e.matches("add_account")): self.handle_add_account(e)
            elif(e.matches("remove_account")): self.handle_remove_account(e)
            elif(e.matches("update_account_status")): self.handle_update_account_status(e)

        for account in self.oholAccounts: self.handle_bot_tick(account)