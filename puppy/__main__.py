import os
import platform
import sys
import subprocess

from puppy import main


if platform.system() == "Darwin" and not sys.stdout.isatty():
    # packaged mac app doesn't launch with a terminal
    subprocess.run(
        [
            "open",
            "-a",
            "Terminal",
            os.path.dirname(os.path.realpath(sys.argv[0]))
            + "/puppy.app/Contents/MacOS/puppy",
        ]
    )
else:
    main()
