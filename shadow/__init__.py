from time import sleep

from shadow.environment import __version__, print_info
from shadow.apis import Champions
from shadow.ugg import UGG
from shadow.static import ALL_ROLES, SLEEP_TIME, GAMEFLOW_PHASE
from shadow.lcu_interface import LcuInterface


def main():
    """
    Main
    """

    print_info()

    lcu_interface = LcuInterface()

    while True:
        # exit if in game
        if lcu_interface.get_gameflow_phase()  == GAMEFLOW_PHASE.IN_PROGRESS:
            print("In game, exiting...")
            raise SystemExit

        # wait until in champ select
        print("#" * 40, end="\n\n")
        print("Waiting for champ select...")
        lcu_interface.wait_for_champ_select(SLEEP_TIME)

        # check what queue we are in
        current_queue = lcu_interface.get_current_queue()
        print("Current queue is", current_queue.lcu_queue_name)

        # check assigned role
        assigned_role = lcu_interface.get_assigned_role()
        if assigned_role:
            print("Assigned role is", assigned_role.display_role_name)

        # wait until champ is locked in
        print("Waiting for champion lock in...", end="\n\n")
        lcu_interface.wait_for_champion_lock(SLEEP_TIME)

        # init vars
        champion_changed = False
        prev_champion_name = ""
        prev_rune_page_role = None
        current_rune_page_role = None
        # main loop
        while True:
            # if we leave champ select, quit
            if lcu_interface.get_gameflow_phase() != GAMEFLOW_PHASE.CHAMP_SELECT:   
                print("No longer in champ select", end="\n\n")
                break

            champion_id = lcu_interface.get_current_champion()
            champion_name = Champions.name_for_id(champion_id)
            # check if we have the same champion as last time
            if prev_champion_name != champion_name:
                champion_changed = True

                # request data from ugg
                print("-" * 20, end="\n\n")
                print("Locked in", champion_name)
                # get champ data
                print("Fetching data...")
                ugg = UGG(champion_name=champion_name, current_queue=current_queue, assigned_role=assigned_role)
                print("Retrieved data for", ", ".join([role.display_role_name for role in ugg.get_roles()]))

                print("Building rune pages...")
                # delete old pages
                rune_pages = lcu_interface.get_rune_pages()
                editable_rune_pages = [page for page in rune_pages if page["isEditable"]]
                for rune_page in editable_rune_pages:
                    for role in ALL_ROLES:
                        if role.display_role_name in rune_page["name"]:
                            lcu_interface.delete_rune_page(str(rune_page["id"]))
                            break

                # build rune pages for correct map and post them
                rune_pages_to_add = []
                for role in ugg.get_roles():
                    active = role == assigned_role # make the page for assigned role active
                    new_rune_page = ugg.get_runes(role, active=active)
                    rune_pages_to_add.append(new_rune_page)

                assigned_role_rune_page_id = None
                for rune_page in rune_pages_to_add:
                    lcu_interface.post_rune_page(rune_page)
                    # remember id of assigned rune page to set it as active later
                    if rune_page["isActive"]:
                        assigned_role_rune_page_id = lcu_interface.get_current_rune_page()["id"]
                # set current rune page to assigned role
                if assigned_role_rune_page_id:
                    lcu_interface.set_current_rune_page(str(assigned_role_rune_page_id))
                print("Done", end="\n\n")

            # get role of current rune page
            current_rune_page = lcu_interface.get_current_rune_page()
            if current_rune_page["name"] in [role.display_role_name for role in ALL_ROLES]:
                current_rune_page_role = ALL_ROLES.get_role_by_display_role_name(current_rune_page["name"])
            # check if champion changed or if we have the same rune page as last time
            if champion_changed or current_rune_page_role != prev_rune_page_role:
                print("Rune page changed to", current_rune_page_role.display_role_name)
                print("Building item set...")
                # change items
                item_sets_data = lcu_interface.get_item_sets_data()
                all_item_sets = item_sets_data["itemSets"]

                # delete old item sets
                new_all_item_sets = []
                for item_set in all_item_sets:
                    for role in ALL_ROLES:
                        if role.display_role_name in item_set["title"]:
                            break
                    else: # only keep ones that do not have the name of a role in their title
                        new_all_item_sets.append(item_set)
                all_item_sets = new_all_item_sets

                # first abilities order
                first_abilities_string = "".join(ugg.get_first_abilities(current_rune_page_role).to_str_list())
                # ability max order
                ability_max_order_string = "".join(ugg.get_max_order(current_rune_page_role).to_str_list())

                # build new item set
                new_item_set = ugg.get_items(
                    role=current_rune_page_role, 
                    champion_id=champion_id, 
                    item_set_name=f"{current_rune_page_role.display_short_role_name} (Start {first_abilities_string}, Max {ability_max_order_string})", 
                    first_abilities=first_abilities_string
                )
                # put item set
                all_item_sets.append(new_item_set)
                item_sets_data["itemSets"] = all_item_sets
                lcu_interface.put_item_sets_data(item_sets_data)

                # change summoners
                print("Editing summoners...")
                lcu_interface.edit_summoners(ugg.get_summoners(current_rune_page_role))
                
                print("Done", end="\n\n")

            # update variables to check if they have changed in the next poll
            prev_champion_name = champion_name
            prev_rune_page_role = current_rune_page_role
            champion_changed = False
            
            # pause between polls
            sleep(SLEEP_TIME)