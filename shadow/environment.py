from shadow.config import Config
from shadow.static import CONFIG_FILENAME

__version__ = "1.3.5"

config = Config()

def print_info():
    print(f"Shadow v{__version__}")
    print("-------")
    print("Options:")
    if config.is_new:
        print(f"Created a config file ({CONFIG_FILENAME})")
    print(f"Patch reversion {'enabled' if config.revert_patch else 'disabled'}")
    print(f"Flash on {'F' if config.flash_on_f else 'D'}", end="\n\n")
