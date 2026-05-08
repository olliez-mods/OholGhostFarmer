# Used just for breakout and ghost base
import EllaBotLib as Ella
from quick_ini import QuickIni

QuickIni.load_file("config.ini")
TWIN = QuickIni.get_value("run_as_twins", False)
TWIN_CODE = QuickIni.get_value("twin_code", "TWIN")
IP = QuickIni.get_value("ohol_ip", "bigserver2.onehouronelife.com")
PORT = QuickIni.get_value("ohol_port", 8005)


class OholAccount:
    def __init__(self, email, key, twin:bool = False):
        self.email = email
        self.key = key
        self.status = "DIS" # TUT, BASE, OUT, DIS

        if(twin == None): twin = TWIN # DEFAULT to global twin setting if not provided

        self.bot = Ella.Bot_Object()
        self.bot.set_login_creds(email, key, IP, PORT)
        if(twin): self.bot.set_twin_info(TWIN_CODE, 2, enable_twinning=True)

        self.last_login_time = 0
        self.tut_food_list:list[tuple[int, int]] = []

        self.estimated_time_of_hunger = None # We have food for about how much longer?
        self.last_craving_item_desc:str = ""

    def set_status(self, status:str):
        status = status.upper()
        if(status not in ("TUT", "BASE", "OUT", "DIS")): raise Exception(f"Invalid status {status} for account {self.email}")
        self.status = status
