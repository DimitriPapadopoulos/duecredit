# emacs: -*- mode: python; py-indent-offset: 4; tab-width: 4; indent-tabs-mode: nil -*-
# ex: set sts=4 ts=4 sw=4 noet:
# ## ### ### ### ### ### ### ### ### ### ### ### ### ### ### ### ### ### ### ##
#
#   See COPYING file distributed along with the duecredit package for the
#   copyright and license terms.
#
# ## ### ### ### ### ### ### ### ### ### ### ### ### ### ### ### ### ### ### ##
"""Helper to use duecredit as a "runnable" module with  -m duecredit"""
from __future__ import annotations

import sys

from . import __version__, due
from .log import lgr


def usage(outfile, executable=sys.argv[0]):
    if "__main__.py" in executable:
        # That was -m duecredit way to launch
        executable = f"{sys.executable} -m duecredit"
    outfile.write(
        f"""Usage: {executable} [OPTIONS] <file> [ARGS]

Meta-options:
--help                Display this help then exit.
--version             Output version information then exit.
"""
    )


def runctx(cmd, global_ctx=None, local_ctx=None):
    if global_ctx is None:
        global_ctx = {}
    if local_ctx is None:
        local_ctx = {}

    try:
        exec(cmd, global_ctx, local_ctx)
    finally:
        # good opportunity to avoid atexit I guess. pass for now
        pass


def main(argv=None):
    import getopt
    import os

    if argv is None:
        argv = sys.argv

    try:
        opts, prog_argv = getopt.getopt(argv[1:], "", ["help", "version"])
        # TODO: support options for whatever we would support ;)
        # probably needs to hook in somehow into commands/options available
        # under cmdline/
    except getopt.error as msg:
        sys.stderr.write(f"{sys.argv[0]}: {msg}\n")
        sys.stderr.write(f"Try `{sys.argv[0]} --help' for more information\n")
        sys.exit(1)

    # and now we need to execute target script "manually"
    # Borrowing up on from trace.py
    for opt, _ in opts:
        if opt == "--help":
            usage(sys.stdout, executable=argv[0])
            sys.exit(0)

        if opt == "--version":
            sys.stdout.write(f"duecredit {__version__}\n")
            sys.exit(0)

    sys.argv = prog_argv
    progname = prog_argv[0]
    sys.path[0] = os.path.split(progname)[0]

    try:
        with open(progname) as fp:
            code = compile(fp.read(), progname, "exec")
        # try to emulate __main__ namespace as much as possible
        globs = {
            "__file__": progname,
            "__name__": "__main__",
            "__package__": None,
            "__cached__": None,
        }
        # Since used explicitly -- activate the beast
        due.activate(True)
        runctx(code, globs, globs)
        # TODO: see if we could hide our presence from the final tracebacks if execution fails
    except OSError as err:
        lgr.error(f"Cannot run file {sys.argv[0]!r} because: {err}")
        sys.exit(1)
    except SystemExit:
        pass


if __name__ == "__main__":
    main()
