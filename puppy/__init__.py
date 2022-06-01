from time import sleep

from puppy.apis import Champions
from puppy.apis.data import DataSource
from puppy.config import config
from puppy.static import ALL_ROLES, SLEEP_TIME, GAMEFLOW_PHASE
from puppy.lcu_interface import LcuInterface


def main():
    """
    Main
    """

    print(f"Puppy")
    print("-------")
    print("Options:")
    print(f"Patch reversion {'enabled' if config.revert_patch else 'disabled'}")
    if config.backend == "ugg":
        print(f"Backend is U.GG")
    elif config.backend == "mobalytics":
        print(f"Backend is Mobalytics")
    print(f"Flash on {'F' if config.flash_on_f else 'D'}", end="\n\n")

    lcu_interface = LcuInterface()

    while True:
        # exit if in game
        if lcu_interface.get_gameflow_phase() == GAMEFLOW_PHASE.IN_PROGRESS:
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
        data_source = None
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

                # request data
                print("-" * 20, end="\n\n")
                print("Locked in", champion_name)
                # get champ data
                print("Fetching data...")
                data_source = DataSource(
                    champion_id=champion_id,
                    current_queue=current_queue,
                    assigned_role=assigned_role,
                )
                print("Retrieved data")

                print("Building rune pages...")
                # delete old pages
                rune_pages = lcu_interface.get_rune_pages()
                editable_rune_pages = [
                    page for page in rune_pages if page["isEditable"]  # type: ignore
                ]
                for rune_page in editable_rune_pages:
                    for role in ALL_ROLES:
                        if role.display_role_name in rune_page["name"]:  # type: ignore
                            lcu_interface.delete_rune_page(str(rune_page["id"]))  # type: ignore
                            break

                # build rune pages for correct map and post them
                rune_pages_to_add = []
                for i, role in enumerate(data_source.get_roles()):
                    # make the page for assigned role active
                    active = role == assigned_role
                    # most popular role is active if there is no assigned role
                    if assigned_role is None and i == 0:
                        active = True
                    new_rune_page = data_source.get_runes(role, active=active).build()
                    rune_pages_to_add.append(new_rune_page)

                # search through rune pages for the one marked as active
                assigned_role_rune_page_id = None
                for rune_page in rune_pages_to_add:
                    lcu_interface.post_rune_page(rune_page)
                    # remember id of assigned rune page to set it as active later
                    if rune_page["isActive"]:
                        assigned_role_rune_page_id = (
                            lcu_interface.get_current_rune_page()["id"]
                        )
                # set current rune page to assigned role
                if assigned_role_rune_page_id:
                    lcu_interface.set_current_rune_page(str(assigned_role_rune_page_id))
                print("Done", end="\n\n")

            # get role of current rune page
            current_rune_page = lcu_interface.get_current_rune_page()
            if current_rune_page["name"] in [
                role.display_role_name for role in ALL_ROLES
            ]:
                current_rune_page_role = ALL_ROLES.get_role_by_display_role_name(
                    current_rune_page["name"]
                )
            # check if champion changed or if we have a different rune page than last time we checked
            if champion_changed or current_rune_page_role != prev_rune_page_role:
                assert current_rune_page_role is not None
                assert data_source is not None

                print("Rune page changed to", current_rune_page_role.display_role_name)
                print("Building item set...")
                # change items
                item_sets_data = lcu_interface.get_item_sets_data()
                all_item_sets = item_sets_data["itemSets"]

                # delete old item sets
                new_all_item_sets = []
                for item_set in all_item_sets:
                    for role in ALL_ROLES:
                        if item_set["title"].endswith(role.display_short_role_name):
                            break
                    else:  # only keep ones that do not have the name of a role in their title
                        new_all_item_sets.append(item_set)
                all_item_sets = new_all_item_sets

                # first abilities order
                first_abilities_string = "".join(
                    data_source.get_first_abilities(
                        current_rune_page_role
                    ).to_str_list()
                )
                # ability max order
                ability_max_order_string = "".join(
                    data_source.get_max_order(current_rune_page_role).to_str_list()
                )

                # build new item set
                new_item_set = data_source.get_items(
                    role=current_rune_page_role,
                    item_set_name=f"{champion_name} {current_rune_page_role.display_short_role_name}",
                    first_abilities_string=first_abilities_string,
                    ability_max_order_string=ability_max_order_string,
                ).build()
                # put item set
                all_item_sets.insert(0, new_item_set)
                item_sets_data["itemSets"] = all_item_sets
                lcu_interface.put_item_sets_data(item_sets_data)

                # change summoners
                print("Editing summoners...")
                lcu_interface.edit_summoners(
                    data_source.get_summoners(current_rune_page_role)
                )

                print("Done", end="\n\n")

            # update variables to check if they have changed in the next poll
            prev_champion_name = champion_name
            prev_rune_page_role = current_rune_page_role
            champion_changed = False

            # pause between polls
            sleep(SLEEP_TIME)
