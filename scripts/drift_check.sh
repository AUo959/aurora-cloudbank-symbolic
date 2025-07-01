#!/bin/bash
# Run symbolic drift check and report status
python3 -m modules.reflective_autonomy.reflective_autonomy_loop
echo "Drift check complete. Review logs for Δ > 0.02"
