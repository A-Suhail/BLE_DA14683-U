#!/bin/bash

###############################################################
# P0_PADPWR_CTRL_REG (0x500030C0) Value: (0x000000C0)
# P1_PADPWR_CTRL_REG (0x500030C2) Value: (0x000000FF)
# P2_PADPWR_CTRL_REG (0x500030C4) Value: (0x000000FF)
# P3_PADPWR_CTRL_REG (0x500030C6) Value: (0x000000FF)
# P4_PADPWR_CTRL_REG (0x500030C8) Value: (0x000000FF)
###############################################################
echo Programming PADPWR_CTRL_REGs for 1.8 volt
"${0%/*}/../../../binaries/cli_programmer" "$1" write_tcs 10 0x500030C0 0x000000C0 0x500030C2 0x000000FF 0x500030C4 0x000000FF 0x500030C6 0x000000FF 0x500030C8 0x000000FF
