# Shadow

Runes, summoner spells, items, and ability order helper

## Overview

* Automatic creates rune pages, edits summoner spells, and builds item sets. Open your shop to see your ability upgrade orders.
* Supports changing champion (e.g., trades, ARAM bench)
* Supports different roles (for when there are different runes, summoner spells, items, or ability orders depending on the role your champion is played in)
* Detects your assigned role and switches your runes and items to match that role by default
* Support Summoner's Rift and ARAM
* Uses caching for optimal performance
* Detects whether to use previous patch's data if there is not enough data on this patch to give accurate information

## Before using

* Install Python 3.7+
* Clone this repository, or download it as a zip file and extract it
* Run `python3 -m pip install -r requirements.txt --user` to install dependencies

## Usage

* Open League of Legends
* Run `python3 -m shadow` from the command line, or run `shadow.bat`
* Go through champ select and lock in a champion
* Select the rune page whose name is your role (e.g., if you are playing mid, select the rune page called "Middle"). Your summoner spells, item sets, and ability upgrade order data will update automatically when you select a rune page.

Your summoner spells and items should be updated automatically whenever you choose a new role using rune pages. Your ability upgrade orders can be found in the item set title in the in-game shop.

## Config File

The first time you run Shadow, a configuration file will be created named `config.json`. Edit this file to customize how shadow runs. See below for available options.

#### flash_on_f

`"flash_on_f": bool`

When enabled, puts flash in the secondary summoner spell spot (usually on the F key) if your champion uses flash. Use this flag to be like Faker.

#### revert_patch

`"revert_patch": bool`

When enabled, will revert to previous patch's data if it is very early in the current patch in order to give more accurate suggestions. Disabling this option early in the patch may result in strange runes/builds.

#### preferred_item_slots

`"preferred_item_slots": {str: int}`

Maps item ids to preferred item slots in game (0 to 5). When you buy an item on this list, the game will attempt to place it in your preferred slot specified here.

For example,

```
{
    ...
    "preferred_item_slots": {
        "2055": 0
    }
}
```

will place control wards into the first item slot (bound to the 1 key by default).