from EllaBotLib.defaultActions import *
import EllaBotLib as Ella
import copy
import time

class Wait_For_Hunger(Action):
    """
    Does nothing until the player is hungry, then it succeeds.
    """
    def __init__(self, num_empty_pips: int = 1, time_out: int = None):
        super().__init__()
        self.num_empty_pips = num_empty_pips
        self.time_out = time_out
    
    def start(self):
        if(self.bot.live_player == None): return self.fail("No live player object found.")

        self.logger.debug(f"Waiting for hunger: {self.bot.food_left} food left, {self.bot.max_food} max food, need at least {self.num_empty_pips} empty pips")

        self.time_start = time.time()
        self.run_timeout = (self.time_out != None)

    def on_packet(self, packet):
        if(self.bot.max_food - self.bot.food_left >= self.num_empty_pips):
            self.complete = True; return
        if(self.run_timeout and time.time() - self.time_start >= self.time_out):
            self.fail(f"Wait_For_Hunger timed out after {self.time_out} seconds.")
    
    def __repr__(self):
        return f"<CustomActions.Wait_For_Hunger, num_empty_pips={self.num_empty_pips}>"

class Wait_For_Item(Action):
    """
    Waits until a specific item is available in the world, then it succeeds.
    """
    def __init__(self, regex:str, *regs:str):
        super().__init__()
        self.item_regexs = []
        self.item_regexs.append(regex)
        self.item_regexs.extend(regs)

        self.seconds_between_checks = 0.2
        self.last_check_time = 0

        self.ready = False
    
    def start(self):
        if(self.bot.live_player == None): return self.fail("No live player object found.")
        self.bot.logger.debug(f"Waiting for item with regex: {self.item_regexs}")
    
    def on_packet(self, packet):
        if(self.ready): return
        if(time.time() - self.last_check_time < self.seconds_between_checks): return
        items = self.bot.world.find_tiles_with_descriptions(*self.item_regexs)
        if(len(items) > 0): self.ready = True; return
        self.last_check_time = time.time()
    
    def tick(self):
        # We wait for tick so World can update correctly so next actions can find the item
        if(self.ready): self.complete = True
    
    def __repr__(self):
        return f"<CustomActions.Wait_For_Item, item_regexs={self.item_regexs}>"


class Repeat_Action(Action):
    """
    Repeats a list of actions a specific number of times or until a fail
    -1 for num_repeats means infinite repeats

    Actions may be passed as instances or as zero-argument factories.
    """
    def __init__(self, num_repeats:int, action, *actions):
        super().__init__()
        self.num_repeats = num_repeats
        if(num_repeats < 0): self.num_repeats = -1
        self.current_repeat = 0

        self.action_factories:list[callable] = []
        self.action_factories.append(self._make_factory(action))
        for a in actions:
            self.action_factories.append(self._make_factory(a))
    
    def _make_factory(self, action_or_factory):
        if callable(action_or_factory):
            return action_or_factory
        return lambda action=action_or_factory: copy.deepcopy(action)

    def add_group(self):
        for factory in self.action_factories:
            self.action_queue.add_action(factory())
    
    def start(self):
        if(self.bot.live_player == None): return self.fail("No live player object found.")
        if(self.num_repeats == 0): return self.succeed()

        self.add_group()
    
    def tick(self):
        if(self.action_queue.last_action_failed): return self.fail(f"An action in the Repeat_Action failed ({str(self.action_queue.current_action)}): {self.action_queue.last_action_failed_reason}")
        if(self.action_queue.is_complete()):
            self.current_repeat += 1
            if(self.num_repeats > 0 and self.current_repeat >= self.num_repeats): self.complete = True; return
            self.add_group()
    
    def __repr__(self):
        return f"<CustomActions.Repeat_Action, num_repeats={self.num_repeats}, current_repeat={self.current_repeat}, num_actions={len(self.action_factories)}>"

class Ignore_Fail(Action):
    """
    Runs a list of actions, ignoring any fails. Succeeds when all actions have completed.
    """
    def __init__(self, action:Action, *actions:Action):
        super().__init__()
        self.set_auto_fail(False, False)

        self.actions:list[Action] = []
        self.actions.append(action)
        self.actions.extend(actions)
    
    def start(self):
        for action in self.actions:
            self.action_queue.add_action(action)
    
    def tick(self):
        if(self.action_queue.is_complete()): self.complete = True; return
        if(self.action_queue.last_action_failed): self.complete = True; return

class Print_World(Action):
    """
    Prints the world object to the logger, for debugging purposes.
    """
    def __init__(self, radius:int = None):
        super().__init__()
        self.radius = radius if radius != None else 5
    def start(self):
        if(self.bot.world == None): return self.fail("No world object found.")

        self.logger.info(f"World Debug ({(self.radius * 2 + 1) ** 2} tiles):")
        for x in range(self.bot.live_player.x - self.radius, self.bot.live_player.x + self.radius + 1):
            for y in range(self.bot.live_player.y - self.radius, self.bot.live_player.y + self.radius + 1):
                tile = self.bot.world.get_tile(x, y)
                if(tile == None): self.logger.info(f"({x}, {y}): None"); continue
                if(not tile.has_item): self.logger.info(f"({x}, {y}): Empty"); continue
                live_item = tile.live_item
                if(live_item == None): self.logger.info(f"({x}, {y}): None (No live item)"); continue
                item = live_item.item
                if(item == None): self.logger.info(f"({x}, {y}): None (Could not find item - ID: {live_item.id})"); continue
                self.logger.info(f"({x}, {y}): {item.description} (ID: {live_item.id})")
        self.complete = True

class Fail_On_Not_Holding(Action):
    """
    Fails if the player is not currently holding an item that matches the given regexes.
    """
    def __init__(self, regex:str, *regs:str):
        super().__init__()
        self.item_regexs = []
        self.item_regexs.append(regex)
        self.item_regexs.extend(regs)

    def start(self):
        if(self.bot.live_player == None): return self.fail("No live player object found.")
        if(self.bot.live_player.item_held == None): return self.fail("Player is not holding anything.")
        item = self.bot.live_player.item_held.item
        if(item == None): return self.fail("Could not find item object for held item.")
        for regex in self.item_regexs:
            if(re.match(regex, item.description)): self.complete = True; return
        return self.fail(f"Held item '{item.description}' does not match any of the regexes: {self.item_regexs}")

class Fail_On_Empty_Hands(Action):
    """
    Fails if the player is not currently holding anything.
    """
    def start(self):
        if(self.bot.live_player == None): return self.fail("No live player object found.")
        if(self.bot.live_player.item_held == None): return self.fail("Player is not holding anything.")
        self.complete = True
