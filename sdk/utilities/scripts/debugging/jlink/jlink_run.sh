#!/bin/sh

# Export any variables we need.
# Note that '.' (dot) is like an "include" statement.
DIR="`dirname "$0"`"
JLinkExe -commandfile "$DIR/jlink_cmd.jlink"

# Run GDB using the parameters passed in
exec JLinkGDBServer "$@"
