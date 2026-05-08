import time
from quick_ini import QuickIni

from EllaBotLib import bot
from events import Events_Handler, Run, RunChild, Event
import EllaBotLib as Ella
from EllaBotLib import defaultActions, functions
from .tut_actions import get_breakout_actions, food_locations, get_eat_food_at_location_actions
from shared.account import OholAccount

QuickIni.load_file("config.ini")
DATA_PATH = QuickIni.get_value("data7_path", "C:/OneLifeData7")

def get_valid_object_at(bot: Ella.Bot_Object, x: int, y: int) -> Ella.Live_Item_Object:
    tile = bot.world.get_tile(x, y)
    if(not tile): return None
    obj = tile.live_item
    if(not obj or not tile.has_item): return None
    item = obj.item
    if(not item): return None
    return obj

class BreakoutRun(RunChild):
    def start(self):
        print("Starting Breakout Run")

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

    def handle_bot_tick(self, account: OholAccount):
        bot = account.bot
        p = bot.handle_next_packet()

        if((not bot.logged_in or not bot.sock_alive) and account.status == "TUT"):
            # We are not logged in, try to log in every 30 seconds
            if(time.time() - account.last_login_time > 30):
                print(f"Logging in account {account.email}...")
                bot.reset_bot(preserve_login_info=True)
                bot.reset_flags()
                bot.login(tutorial_num=1)
                account.last_login_time = time.time()
                account.tut_food_list = food_locations.copy()

        if(bot.logged_in and not bot.login_proccess):
            bot.action_manager.tick()

            if(bot.ensure_single_run("add_actions")):
                print("Adding actions...")
                ac = get_breakout_actions()
                for action in ac: bot.action_manager.add_action(action, chain_id="actions_tut")
            
            if(account.status != "TUT"):
                print(f"Account {account.email} has status {account.status}, logging out...")
                bot.unlogin()
                return
            
            # once breakout steps are complete we go into survivle mode, while we wait to get a ghost
            if(bot.action_manager.is_complete()):

                # Find and eat the closest food
                closest_food_pos = None
                closest_food_dist = float("inf")
                bot_pos = bot.live_player.xy
                for food_pos in account.tut_food_list:
                    print(f"Checking food at {food_pos}, bot at {bot_pos}")
                    dist = functions.get_chebyshev_distance(bot_pos, food_pos)
                    if(dist < closest_food_dist):
                        closest_food_pos = food_pos
                        closest_food_dist = dist
                if(closest_food_pos):
                    print(f"Closest food is at {closest_food_pos}, distance {closest_food_dist}")
                    bot.action_manager.add_actions(*get_eat_food_at_location_actions(closest_food_pos), chain_id="eat_food")
                    account.tut_food_list.remove(closest_food_pos)

    def tick(self):

        for e in self.events_handler.get_events():
            if(e.matches("add_account")): self.handle_add_account(e)
            elif(e.matches("remove_account")): self.handle_remove_account(e)
            elif(e.matches("update_account_status")): self.handle_update_account_status(e)

        for account in self.oholAccounts: self.handle_bot_tick(account)
