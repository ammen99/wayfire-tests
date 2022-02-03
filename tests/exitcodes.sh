# Test ran successfully, no errors detected
export WF_TEST_OK=0

# Test ran successfully, but the state we reached was wrong
export WF_TEST_WRONG=10

# Wayfire crashed at some point
export WF_TEST_CRASH=11

# Test could not be run, for ex. required executable is missing from $PATH
export WF_TEST_SKIP=12
