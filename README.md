# Puppy

League of Legends runes, summoner spells, items, and ability order fetcher

## Overview

* Automatically creates rune pages, edits summoner spells, and builds item sets. Open your shop to see your ability upgrade orders.
* Supports changing champion (e.g., trades, ARAM bench)
* Supports different roles (for when there are different runes, summoner spells, items, or ability orders depending on the role your champion is played in)
* Detects your assigned role and switches your runes and items to match that role by default
* Supports Summoner's Rift, ARAM, and Nexus Blitz
* Uses caching for optimal performance
* Detects whether to use previous patch's data if there is not enough data on this patch to give accurate information
* Can use data from both U.GG and Mobalytics

## Setup

### Pre-compiled Binaries

1. Navigate to the [releases page](https://github.com/imranmaj/puppy/releases)
2. Download the binary for your platform from the latest release and open it

On Windows, if you get a blue window which says "Window protected your PC," press "More info" then "Run anyway."

On Mac, open the DMG file and drag the puppy.app to another location on your computer. If you get a window which says "puppy.app is an app downloaded from the internet" or "\_\_main\_\_ is a Unix app downloaded from the internet," press "Open." If you see "puppy.app cannot be opened because the developer cannot be verified," right-click on puppy.app and press "Open," then on the screen which asks "Are you sure you want to open it?" press "Open."

### Running from source

1. Install Python 3.7+
2. `pip install -r requirements.txt`
3. `python -m puppy`

## Usage

1. Open League of Legends
2. Run puppy
3. Go through champ select and lock in a champion
4. Select the rune page whose name is your role (e.g., if you are playing mid, select the rune page called "Middle")

Your summoner spells and items should be updated automatically whenever you choose a new role using rune pages. Your ability upgrade orders can be found in the names of the item blocks in the in-game shop.

## Config File

The first time you run puppy, a configuration file will be created named `config.json`. Edit this file to customize how puppy runs. See below for available options.

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

#### small_items

`"small_items": [int] `

List of any additional items you want to be listed as part of your small/starting items.

For example,

```
{
    ...
    "small_items": [
        1001,
        2055
    ]
}
```

will include boots and control wards at the end of your small items block in the item set.

#### backend

`"backend": "ugg" OR "mobalytics"`

Determines the backend to be used to fetch data. `"ugg"` will cause the data to be fetched from [U.GG](https://u.gg/), while `"mobalytics"` will cause data to be fetched from [Mobalytics](https://app.mobalytics.gg/lol).

## Todo

- [X] Mobalytics backend
- [ ] Config `"preferred_item_slots"` and `"small_items"` by name instead of ID
- [ ] Use WebSocket LCU API (not polling)
    - [ ] Persistent background process
- [ ] Matchup-specific builds (Mobalytics)
