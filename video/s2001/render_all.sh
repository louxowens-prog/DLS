#!/bin/bash
# Order: cheap shots first so partial results are useful early.
cd "$(dirname "$0")/.."
R=out/_2001/frames
run() { python3 s2001/render_shots.py "$@" 2>&1 | grep --line-buffered -E "DONE|/|rror" ; }
run alignment 24 5.3  0.0 1.0 $R/open
run monolith  24 12.5 0.0 1.0 $R/monolith
run dawn      24 6.5  0.0 1.0 $R/dawn
run station   12 10.0 0.0 1.0 $R/station
run alignment 24 5.8  0.35 1.0 $R/close
run memory    12 24.8 0.0 1.0 $R/memory
run centrifuge 12 15.4 0.0 1.0 $R/corridor 10
echo ALL_RENDERS_DONE
