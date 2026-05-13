from EllaBotLib.defaultActions import *
from shared.customActions import *

food_locations = [
    (16, 0), (17, 0), (17, 1), (18, -1), (40, 1), (63, 1), (91, 0), (92, 1), (106, 0), (110, 1), (117, 1), (123, -1), (132, -1), (133, -1), (133, 0), (134, 1), (135, 1),
    (161, -1), (162, 1), (182, 1), (183, -1), (204, -1), (205, 1), (213, -1), (217, 1), (229, -1), (235, 1), (231, -3), (232, -4), (236, -6), (239, -9), (243, -8), (245, -8),
    (249, -8), (264, -9), (269, -8), (270, -9), (273, -10), (273, -11), (273, -12)
]

def get_eat_food_at_location_actions(location: tuple[int, int]):
    return [
        Fail_On_Not_Holding("Sharp Stone"),
        Walk_To_Action(location),
        Use_Held_On_Tile_Action(location),
        Empty_Hands_action(return_to_tile=True, keep_tile_clear=True),
        Send_Interaction_Action("use", location),
        Ignore_Fail(
            Fail_On_Empty_Hands(),
            Wait_For_Hunger(num_empty_pips=7),
            Send_Interaction_Action("self"),
        ),
        Get_Item_Action("Sharp Stone"),
    ]



def get_empty_charcoal_kiln_actions():
    return [
        Empty_Hands_action(),
        Wait_For_Item("Sealed Adobe Kiln"),
        Use_Held_On_Object_Action("Sealed Adobe Kiln"),
        Get_Item_Action("Basket"),
        Use_Held_On_Object_Action("Kiln"),
        Empty_Hands_action(),
        Use_Held_On_Object_Action("Basket of Charcoal"),
        Empty_Hands_action(),
    ]

def get_fire_charcoal_actions():
    return [
        Fail_On_Not_Found(r"^Adobe Kiln$"),
        Get_Item_Action("Kindling"),
        Use_Held_On_Object_Action("Kiln"),
        Fallback_Action([
            Get_Item_Action("Firebrand"),
        ], [
            Get_Item_Action("Long Straight Shaft"),
            Use_Held_On_Object_Action("Large Slow Fire", r"^Fire$"),
        ]),
        Use_Held_On_Object_Action("Kiln"),
        Get_Item_Action(r"^Adobe$"),
        Fail_On_Not_Found("Firing adobe kiln"),
        Use_Held_On_Object_Action("Kiln"),
        Empty_Hands_action(),
    ]

def get_fire_kiln_actions():
    return [
        Fallback_Action([
            Fail_On_Not_Found("Forge with Charcoal"),
        ], [
            Wait_For_Item(r"^Forge$"),
            Get_Item_Action(r"^Basket$"),
            Use_Held_On_Object_Action("Big Charcoal Pile"),
            Use_Held_On_Object_Action(r"^Forge$"),
            Fail_On_Not_Found("Forge with Charcoal"),
        ]),
        Empty_Hands_action(),
        Fallback_Action([
            Get_Item_Action(r"^Firebrand$"),
            Use_Held_On_Object_Action("Forge with Charcoal"),
        ], [
            Empty_Hands_action(),
            Get_Item_Action("Long Straight Shaft"),
            Use_Held_On_Object_Action("Large Slow Fire", r"^Fire$"),
            Use_Held_On_Object_Action("Forge with Charcoal"),
        ]),
        Fail_On_Not_Found("Firing Forge"),
        Empty_Hands_action(),
    ]

def get_breakout_actions() -> list[Action]:
    return [

    # GET CLOTHES AND WALK TO BREAKOUT SPOT
    Wait_Seconds_Action(5), # Wait a few seconds
    Walk_To_Action((13, -1)),
    Use_Held_On_Object_Action("Wooden Door"),
    Walk_To_Action((17, 0)),
    Use_Held_On_Object_Action("Wild Onion"),
    Wait_For_Hunger(),
    Send_Interaction_Action("self"),
    Walk_To_Action((27, 0)),
    Walk_To_Action((37, 0)),
    Walk_To_Action((47, 0)),
    Walk_To_Action((57, 0)),
    Walk_To_Action((67, 0)),
    Walk_To_Action((77, 0)),
    Walk_To_Action((87, 0)),
    Walk_To_Action((97, 0)),
    Walk_To_Action((107, 0)),
    Use_Held_On_Object_Action("Wild Garlic"),
    Wait_For_Hunger(),
    Send_Interaction_Action("self"),
    Walk_To_Action((117, 0)),
    Walk_To_Action((126, 0)),
    Use_Held_On_Object_Action("Wooden Door"),
    Walk_To_Action((136, -10)),
    Send_Interaction_Action("use", (135, -10)),
    Send_Interaction_Action("use", (137, -10)),
    Wait_For_World_Update_Action(),
    Get_Item_Action("Firewood"),
    Walk_To_Action((140, -7)),
    Use_Held_On_Object_Action("Wooden Door"),
    Walk_To_Action((140, -3)),
    Use_Held_On_Object_Action("Wooden Door"),
    Walk_To_Action((142, -1)),
    Get_Item_Action("Burdock Root"),
    Wait_For_Hunger(),
    Send_Interaction_Action("self"),
    Get_Item_Action("Firewood"),
    Walk_To_Action((148, -1)),
    Walk_To_Action((152, -1)),
    Walk_To_Action((162, -1)),
    Get_Item_Action("Rabbit Fur Shoe"),
    Send_Interaction_Action("self"),
    Get_Item_Action("Rabbit Fur Shoe"),
    Send_Interaction_Action("self"),
    Get_Item_Action("Rabbit Fur Hat"),
    Send_Interaction_Action("self"),
    Get_Item_Action("Rabbit Fur Loincloth"),
    Send_Interaction_Action("self"),
    Get_Item_Action("Sealskin Coat"),
    Send_Interaction_Action("self"),
    Get_Item_Action("Firewood"),
    Walk_To_Action((173, 0)),
    Walk_To_Action((183, 0)),
    Walk_To_Action((193, 0)),
    Walk_To_Action((203, 0)),
    Walk_To_Action((213, 0)),
    Walk_To_Action((223, 0)),
    Walk_To_Action((233, 0)),
    Walk_To_Action((234, -6)),
    Use_Held_On_Object_Action("Wooden Door"),
    Walk_To_Action((244, -9)),
    Walk_To_Action((254, -9)),
    Walk_To_Action((263, -9)),
    Empty_Hands_action(),
    Walk_To_Action((269, -10)),


    # SETUP TUT ESCAPE ITEMS

    # Sharp stones
    Repeat_Action(2,
        lambda: Get_Item_Action(r"^Stone$"),
        lambda: Use_Held_On_Object_Action("Big Hard Rock")
    ),

    # Cut items
    Use_Held_On_Object_Action("Flint"),
    Use_Held_On_Object_Action("Sapling"),
    Use_Held_On_Object_Action("Burdock"),
    Repeat_Action(6, lambda: Use_Held_On_Object_Action("Straight Branch")),
    Repeat_Action(3, lambda: Use_Held_On_Object_Action("Long Straight Shaft")),
    Use_Held_On_Object_Action("Short Shaft"),
    Repeat_Action(6, lambda: Use_Held_On_Object_Action("Tule Reeds")),
    Empty_Hands_action(),

    # Create oven
    Repeat_Action(4,
        lambda: Get_Item_Action("Harvested Tule", ignore_result=True),
        lambda: Get_Item_Action("Clay Deposit", "Clay Pit#partial", ignore_result=True),
        lambda: Use_Held_On_Object_Action("Reed Bundle")
    ),
    Get_Item_Action(r"^Adobe$"),
    Walk_To_Action((269, -10)),
    Get_Item_Action(r"^Stone$"),
    Walk_To_Action((268, -10)),
    Use_Held_On_Object_Action(r"^Adobe$"),
    Empty_Hands_action(),
    Repeat_Action(2,
        lambda: Get_Item_Action(r"^Adobe$"),
        lambda: Use_Held_On_Object_Action("Adobe Oven"),
    ),
    
    # Make basket
    Get_Item_Action("Harvested Tule", ignore_result=True),
    Get_Item_Action("Harvested Tule", ignore_result=True),
    Use_Held_On_Object_Action("Reed Bundle"),

    # Craft string rope items
    Repeat_Action(5, # 5 Thread
        lambda: Get_Item_Action(r"^(?:Flowering |Fruiting )?Milkweed$", ignore_result=True),
        lambda: Get_Item_Action(r"^(?:Flowering |Fruiting )?Milkweed$", ignore_result=True),
        lambda: Use_Held_On_Object_Action("Milkweed Stalk")
    ),
    Repeat_Action(2, # 2 Rope
        lambda: Get_Item_Action("Thread"),
        lambda: Use_Held_On_Object_Action("Thread")
    ),
    Get_Item_Action("Rope"),
    Use_Held_On_Object_Action("Stakes"),
    Get_Item_Action("Rope"),
    Use_Held_On_Object_Action("Short Shaft"),
    Get_Item_Action("Sharp Stone"),
    Use_Held_On_Object_Action("Tied Short Shaft"),

    # Catch rabbit
    Get_Item_Action("Snare"),
    Use_Held_On_Object_Action("Rabbit Family Hole"),
    Get_Item_Action("Dug Burdock", ignore_result=True),
    Use_Held_On_Object_Action("Flat Rock"),
    Get_Item_Action("Sharp Stone"),
    Use_Held_On_Object_Action("Flat Rock with Burdock Root"),
    Get_Item_Action("Rabbit Bait"),
    Use_Held_On_Object_Action("Snared Rabbit"),
    Empty_Hands_action(),

    # Make clay items
    Repeat_Action(5, 
        lambda: Get_Item_Action(r"^Clay Deposit", r"^Clay Pit", ignore_result=True),
        lambda: Empty_Hands_action(),
    ),
    Get_Item_Action(r"^Stone$"),
    Repeat_Action(4, lambda: Use_Held_On_Object_Action(r"^Clay$")),
    Repeat_Action(2, lambda: Use_Held_On_Object_Action("Wet Clay Bowl")),
    Get_Item_Action("Cut Sapling Skewer", ignore_result=True),
    Use_Held_On_Object_Action(r"^Clay$"),
    Get_Item_Action("Clay with Nozzle", ignore_result=True),
    Empty_Hands_action(),

    # Tongs
    Get_Item_Action("Flint", ignore_result=True),
    Repeat_Action(2, lambda: Use_Held_On_Object_Action("Long Straight Shaft")),
    Empty_Hands_action(),

    # Cut rabbit
    Wait_For_Item("Snared Rabbit"),
    Get_Item_Action("Snared Rabbit"),
    Get_Item_Action("Flint Chip"),
    Use_Held_On_Object_Action("Dead Rabbit"),
    Get_Item_Action("Skinned Rabbit", ignore_result=True),
    Get_Item_Action("Flint Chip"),
    Use_Held_On_Object_Action("Rabbit Fur"),
    Empty_Hands_action(),

    # Start Fire
    Get_Item_Action("Hatchet"),
    Repeat_Action(8, lambda: Use_Held_On_Object_Action("Branch")),
    Get_Item_Action("Kindling"),
    Walk_To_Action((260, -9)),
    Walk_To_Action((250, -9)),
    Walk_To_Action((240, -9)),
    Walk_To_Action((236, -1)),
    Use_Held_On_Object_Action("Hot Coals"),
    Get_Item_Action("Long Straight Shaft"),
    Use_Held_On_Object_Action("Fire"),
    Walk_To_Action((234, -9)),
    Walk_To_Action((244, -9)),
    Walk_To_Action((254, -9)),
    Walk_To_Action((264, -9)),
    Use_Held_On_Object_Action("Kindling"),
    Use_Held_On_Object_Action("Kindling"),
    # Don't use the firewood yet, since we need more time, do it after second charcoal

    # Start making charcoal and cooking plates
    Get_Item_Action("Kindling"),
    Use_Held_On_Object_Action("Kiln"),
    Get_Item_Action("Long Straight Shaft"),
    Use_Held_On_Object_Action(r"^Fire$"),
    Use_Held_On_Object_Action("Kiln"),
    Get_Item_Action("Tongs"),
    Repeat_Action(5,
        lambda: Use_Held_On_Object_Action(r"^Wet Clay (?:Bowl|Plate|Nozzle)$"),
        lambda: Use_Held_On_Object_Action("Kiln"),
        lambda: Empty_Hands_action(force_action_type="use", ignore_result=True), # We expect to still be holding tongs
    ),
    Get_Item_Action(r"^Adobe$"),
    Fail_On_Not_Found("Firing adobe kiln"),
    Use_Held_On_Object_Action("Kiln"),

    # Cook rabbit
    Get_Item_Action("Skewer"),
    Use_Held_On_Object_Action("Skinned Rabbit"),
    Wait_For_Item(r"Hot Coals# \+tool"),
    Use_Held_On_Object_Action(r"Hot Coals# \+tool"),
    Empty_Hands_action(force_action_type="use", ignore_result=True), # We expect to still be holding skewer
    Empty_Hands_action(),
    Get_Item_Action("Cooked Rabbit"),
    Wait_For_Hunger(),
    Send_Interaction_Action("self"),
    Empty_Hands_action(),

    # Stoke fire
    Get_Item_Action("Kindling"),
    Use_Held_On_Object_Action(r"Hot Coals# \+tool"),
    Get_Item_Action("Firewood"),
    Use_Held_On_Object_Action(r"^Fire$"),

    # Next charcoal
    *get_empty_charcoal_kiln_actions(),
    *get_fire_charcoal_actions(),

    # Next charcoal
    *get_empty_charcoal_kiln_actions(),
    *get_fire_charcoal_actions(),

    # Make bellows
    Get_Item_Action("Rabbit Bones", ignore_result=True),
    Get_Item_Action("Flint Chip"),
    Use_Held_On_Object_Action(r"^Rabbit Bone$"),
    Get_Item_Action("Needle"),
    Use_Held_On_Object_Action("Thread"),
    Use_Held_On_Object_Action("Cut Rabbit Fur"),
    Get_Item_Action("Water Pouch"),
    Use_Held_On_Object_Action("Tongs"),
    Get_Item_Action("Clay Nozzle"),
    Use_Held_On_Object_Action("Bellows"),
    Empty_Hands_action(),

    # Final charcoal
    *get_empty_charcoal_kiln_actions(),
    *get_fire_charcoal_actions(),
    Wait_For_Item("Sealed Adobe Kiln"),
    Use_Held_On_Object_Action("Kiln"),
    Empty_Hands_action(),

    # Start smithing
    Get_Item_Action("Bellows"),
    Use_Held_On_Object_Action("Kiln"),

    # Create Wrought Iron
    *get_fire_kiln_actions(),
    Repeat_Action(2,
        lambda: Get_Item_Action("Wooden Tongs"),
        lambda: Use_Held_On_Object_Action("Iron Ore"),
        lambda: Use_Held_On_Object_Action("Firing Forge"),
        lambda: Use_Held_On_Object_Action("Flat Rock# empty"),
        lambda: Get_Item_Action(r"^Stone$"),
        lambda: Use_Held_On_Object_Action("Hot Iron Bloom on Flat Rock"),
    ),
    Repeat_Action(2,
        lambda: Get_Item_Action("Wrought Iron on Flat Rock", ignore_result=True),
        lambda: Use_Held_On_Object_Action("Clay Bowl"),
        lambda: Fallback_Action([
            Get_Item_Action("Small Charcoal Pile", ignore_result=True),
        ],[
            Get_Item_Action("Big Charcoal Pile", ignore_result=True),
        ]),
        lambda: Use_Held_On_Object_Action(r"^Crucible with Iron$"),
        lambda: Get_Item_Action("Clay Plate"),
        lambda: Use_Held_On_Object_Action("Crucible with Iron and Charcoal"),
    ),

    # Create steel
    *get_fire_kiln_actions(),
    Repeat_Action(2,
        lambda: Get_Item_Action("Wooden Tongs"),
        lambda: Use_Held_On_Object_Action("Unforged Sealed Steel Crucible"),
        lambda: Use_Held_On_Object_Action("Firing Forge"),
        lambda: Empty_Hands_action(force_action_type="use", ignore_result=True), # We expect to still be holding the tongs
    ),
    Empty_Hands_action(),
    Repeat_Action(2,
        lambda: Wait_For_Item(r"^Forged Steel Crucible$"),
        lambda: Get_Item_Action(r"^Forged Steel Crucible$", ignore_result=True),
        lambda: Empty_Hands_action(),
        lambda: Get_Item_Action("Crucible with Steel", ignore_result=True),
        lambda: Empty_Hands_action(),
    ),

    # Create tools
    *get_fire_kiln_actions(),
    # Smithing hammer
    Get_Item_Action("Wooden Tongs"),
    Use_Held_On_Object_Action("Steel Ingot"),
    Use_Held_On_Object_Action("Firing Forge"),
    Use_Held_On_Object_Action("Flat Rock# empty"),
    Empty_Hands_action(),
    Get_Item_Action(r"^Stone$"),
    Use_Held_On_Object_Action("Hot Steel Ingot on Flat Rock"),
    Empty_Hands_action(),
    Wait_For_Item(r"^Steel Hammer Head on Flat Rock$"),
    Get_Item_Action(r"^Steel Hammer Head on Flat Rock$", ignore_result=True),
    Use_Held_On_Object_Action("Short Shaft"),
    # Pickaxe
    Get_Item_Action("Wooden Tongs"),
    Use_Held_On_Object_Action("Steel Ingot"),
    Use_Held_On_Object_Action("Firing Forge"),
    Use_Held_On_Object_Action("Flat Rock# empty"),
    Get_Item_Action("Smithing Hammer"),
    Repeat_Action(9, lambda: Use_Held_On_Object_Action(r"^Hot Steel")),
    Wait_For_Item(r"^Steel Mining Pick#flat rock"),
    Get_Item_Action("Steel Mining Pick#flat rock", ignore_result=True),
    Use_Held_On_Object_Action("Long Straight Shaft"),
    Get_Item_Action("Sharp Stone"),
]
