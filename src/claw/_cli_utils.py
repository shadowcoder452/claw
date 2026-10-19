from .errors import display_error
import sys
import os

def stop_after(stage: str, state, args):
    if args.stop_after != stage:
        return

    if args.show_state:
        print(state)

    sys.exit(0)

def cli_err(err):
    print(f"{os.path.basename(sys.argv[0])}: error: {err}", file=sys.stderr)
    sys.exit(1)

def compile_err(errs, src):
    for err in errs:
        display_error(err, src)
    sys.exit(2)