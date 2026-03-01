#!/bin/bash
echo "🚨 TERMINAL DIAGNOSTIC"
echo "===================="
echo "Date: $(date)"
echo "User: $(whoami)"
echo "Directory: $(pwd)"
echo "Shell: $SHELL"
echo "PATH: $PATH"
ls -la | head -5
echo "Terminal test complete"
