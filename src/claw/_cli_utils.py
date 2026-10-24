import argparse
import os
import sys
from typing import Iterable, NoReturn

from .errors import Error, display_error


def stop_after(stage: str, state: object, args: argparse.Namespace) -> None:
    if args.stop_after != stage:
        return

    if args.show_state:
        print(state)

    sys.exit(0)


def cli_err(err: str) -> NoReturn:
    print(f"{os.path.basename(sys.argv[0])}: error: {err}", file=sys.stderr)
    sys.exit(1)


def compile_err(errs: Iterable[Error], src: str) -> NoReturn:
    for err in errs:
        display_error(err, src)
    sys.exit(2)
