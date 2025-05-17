#!/bin/bash

# Store the test path
TEST_PATH="$1"

# Default repetitions
REPETITIONS=100

# Array to hold arguments for run_nested.sh
RUN_NESTED_ARGS=()

# Shift off the first argument (test path)
shift

RUNNER=./run_nested.sh

# Parse remaining arguments
while (( "$#" )); do
  case "$1" in
    -n)
      if [ -n "$2" ]; then
        REPETITIONS="$2"
        shift 2 # Consume -n and the number
      else
        echo "Error: -n requires a number of repetitions." >&2
        exit 1
      fi
      ;;
    --show)
      RUNNER=./my_run.sh
      shift
      ;;
    *)
      RUN_NESTED_ARGS+=("$1") # Add other arguments to the array
      shift # Consume the current argument
      ;;
  esac
done

mkdir -p /tmp/replicated-tests/
rm -rf /tmp/replicated-tests/test-*

for i in $(seq 1 $REPETITIONS); do
    cp "$TEST_PATH" /tmp/replicated-tests/test-$i -r
done

# Pass the collected arguments to run_nested.sh
$RUNNER /tmp/replicated-tests "${RUN_NESTED_ARGS[@]}"
