import time
import traceback
import subprocess
from quick_ini import QuickIni

import events

event_handler = events.Events_Handler()

ITEMS:list[events.Run] = [
    events.Run(event_handler, "discord_bot.discord_main", "DiscordRun"),
    events.Run(event_handler, "ghost_base.ghost_base_main", "GhostBaseRun"),
    events.Run(event_handler, "tutorial_breakout.breakout_main", "BreakoutRun")
]

QuickIni.load_file("config.ini")

GIT_PULL = QuickIni.get_value('do_git_pull', False)
GIT_PULL_INTERVAL = QuickIni.get_value('git_pull_interval', 120)
HOT_RELOAD = QuickIni.get_value('do_file_checks', False)
HOT_RELOAD_CHECK_TIME = QuickIni.get_value('file_checks_interval', 1)

initial_tick_done = False
stop_flag = False

def git_pull() -> bool:
    result = subprocess.run(["git", "pull"], capture_output=True, text=True)
    if result.returncode != 0:
        print(f"git pull failed:\n{result.stderr}")
        return False
    if "Already up to date." not in result.stdout:
        print(f"git pull:\n{result.stdout}")
    return True


def safe_call(func, *args, **kwargs) -> bool:
    try: func(*args, **kwargs)
    except Exception:
        print(f"Error in {func}:")
        traceback.print_exc()
        return False
    return True

def hot_reload_check():
    for run in ITEMS:
        if run.check_file_changed():
            print(f"File change detected for {run.class_name}, restarting it")
            if not safe_call(run.restart): run.stop()

def tick_all():
    for run in ITEMS:
        if not run.run_me: continue
        if not safe_call(run.tick): run.stop()


# =======================================================
# Methods called by main loop at certain times
def pre_start(): pass
def post_start(): pass
def post_initial_tick(): pass
def pre_stop(): pass
def post_stop(): pass
# =======================================================


if __name__ == "__main__":
    pre_start()
    for run in ITEMS: safe_call(run.start)
    post_start()

    last_hot_reload_check = time.time()
    last_git_pull = time.time()
    while True:

        if(stop_flag):
            pre_stop()
            for run in ITEMS: safe_call(run.stop)
            post_stop()
            break

        time.sleep(0.01)
        event_handler.tick()

        if GIT_PULL and time.time() - last_git_pull > GIT_PULL_INTERVAL:
            last_git_pull = time.time()
            git_pull()

        if HOT_RELOAD and time.time() - last_hot_reload_check > HOT_RELOAD_CHECK_TIME:
            last_hot_reload_check = time.time()
            hot_reload_check()

        tick_all()
        if(not initial_tick_done): post_initial_tick(); initial_tick_done = True
