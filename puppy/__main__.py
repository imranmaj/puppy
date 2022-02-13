import os
from pathlib import Path
import platform
import sys
import subprocess


if platform.system() == "Darwin" and not sys.stdout.isatty():
    # packaged mac app doesn't launch with a terminal
    # https://github.com/pyinstaller/pyinstaller/issues/5154
    subprocess.run(
        [
            "open",
            "-a",
            "Terminal",
            Path(os.path.realpath(sys.argv[0])).parent / "__main__",
        ]
    )
else:
    loc = Path(os.path.realpath(sys.argv[0])).parent
    os.chdir(loc)
    # get outside .app on mac
    for i, part in enumerate(loc.parts):
        if part.endswith(".app"):
            os.chdir(Path(*loc.parts[:i]))

    from puppy import main

    main()
