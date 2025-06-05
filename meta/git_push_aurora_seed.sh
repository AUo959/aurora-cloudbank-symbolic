#!/bin/bash
git add ./memory
git add ./aurora.seed.json
git add .gptcontext.json
git add symbolic_config.yaml
git commit -m "SEED::UPDATE – Symbolic memory sync"
git push
