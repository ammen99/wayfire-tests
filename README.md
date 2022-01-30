# wayfire-smoke-tests

A collection of scripts and tests used for testing Wayfire and discovering regressions.

# Usage

Tests are organized in directories, starting in `./tests`, and each test is contained in its own directory.
To execute a test or group of tests, run:

```sh
./run_tests.sh <test directory> <wayfire A> <wayfire B>
```

`<test directory>` is the directory which contains all the tests you want to run.
Information about each test run will be printed on the terminal.

`<wayfire A>` is a folder which contains a checked out version of Wayfire to test.
`<wayfire B>` is also a folder with a checked out version of Wayfire to compare with the first version.

# Motivation & How it all works

Automated tests are almost universally recognized to help in the development and testing of an application.
As Wayfire's code has accumulated a lot of bug fixes and tweaks to account for the variety of clients and their behaviors,
   it becomes clear we need a way to test new versions of the code and compare behavior with previous versions.

Unit tests are widely used for this purpose.
However, a wayland compositor is not purely a data processing application, where most classes are self-contained and functions are mostly pure.
Many of the actions we would like to test, even simpler ones like resizing a view, basically involve half of the codebase in one way or another.
Individual steps can be unit-tested, of course, but the majority of Wayfire's bugs stem from unwanted/unplanned interactions between components.
These interactions are usually spread out in time and involve one or more actual clients.
An additional problem with unit-tests is that they cannot be used to effectively see the graphical output of Wayfire, which is of course the most
important output for a wayland compositor.
This renders unit tests insufficient for Wayfire, although they are still used where they make sense (e.g. wf-config, wf-touch, transactions API).

### Smoke tests

For the reasons outlined above, we need a way to test the entirety of Wayfire.
The strategy used in these tests is the following:

- Run Wayfire in the headless wlroots backend. This allows us to test rendering, multiple outputs, output plug/unplug, etc.
- Submit commands to Wayfire via a custom IPC plugin from a test script.
- Query Wayfire's state via the same IPC to verify state (view geometry/state, etc.)
- Testing the graphical output of Wayfire with real clients is very difficult, because their appearance may change depending on system settings.
  For this reason, we compile two versions of Wayfire - one known to work, and one to test - and compare their outputs.
  By rendering at the same resolution, with the same executables on the same system, the outputs should be the same if there are no regressions.
