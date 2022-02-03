# Test format

Each test is a folder containing an entry point, an executable named `main`,
a file specifying test options `options.sh` and a configuration file for wayfire, `wayfire.ini`.

# `options.sh`

This script is sourced every time the test is run.
It can be used to set environment variables needed for the test,
as well as several options for the test runner itself:

- `IS_GUI_TEST=0/1` - Whether the current test is a GUI test. See the section GUI tests.
- `_WAYFIRE_SOCKET=<...>` - This is used to set the path to the IPC socket when Wayfire
  starts. Without this option, the test cannot know how to communicate with the compositor,
  because tests are run outside of the compositor.

# `wayfire.ini`

This file follows the standard Wayfire config file format.
Tests should generally contain the minimal amount of options and plugins needed to test the given behavior.

# `main`

The main entry point of a test.
It can be executable in any format, e.g. a bash script, a python script, etc.
The test can communicate with Wayfire through the socket configured with `_WAYFIRE_SOCKET`.
Since the test is run outside of Wayfire, it also should be able to deal with Wayfire crashing.
Usually, this is done by checking whether certain IPC requests are successful.

After the test is done running, its exit code determines the outcome of the test.
See `../wfpyipc/wftest.py` for a list of possible exit codes and their meaning.

# GUI Tests

**NOTE: GUI Tests are not implemented yet!***

Sometimes, we want to verify the graphical output of Wayfire instead of verifying its state
by using information from the debug IPC.
In these cases, the test runner can start two revisions of Wayfire, execute the test on them,
take a screenshot of each compositor, and then check that output.
This is useful if we want for example to check whether a transformer works as intended.
