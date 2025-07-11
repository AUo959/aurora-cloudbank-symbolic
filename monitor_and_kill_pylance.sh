#!/bin/bash
# Continuous Pylance Monitor and Killer

echo "🔄 Continuous Pylance Performance Monitor"
echo "========================================"
echo ""

# Function to kill Pylance
kill_pylance() {
    local killed=0
    while IFS= read -r pid; do
        if [[ -n "$pid" ]]; then
            kill -9 "$pid" 2>/dev/null && killed=1
        fi
    done < <(pgrep -f pylance)
    
    if [[ $killed -eq 1 ]]; then
        echo "   🔥 Killed Pylance processes"
    fi
}

# Function to check memory usage
check_memory() {
    local memory_mb
    memory_mb=$(ps aux | awk 'NR>1 {sum+=$6} END {printf "%.0f", sum/1024}')
    echo "   💾 Memory: ${memory_mb}MB"
    
    # If memory is above 3GB, kill Pylance
    if [[ $memory_mb -gt 3000 ]]; then
        echo "   ⚠️  High memory detected - killing Pylance"
        kill_pylance
    fi
}

# Function to monitor processes
monitor_processes() {
    local pylance_count
    pylance_count=$(pgrep -f pylance | wc -l)
    
    if [[ $pylance_count -gt 0 ]]; then
        echo "   ⚠️  $pylance_count Pylance process(es) detected"
        kill_pylance
        return 1
    else
        echo "   ✅ No Pylance processes"
        return 0
    fi
}

# Main monitoring loop
echo "🎯 Starting continuous monitoring (Ctrl+C to stop)..."
echo "   Will check every 10 seconds and kill Pylance if detected"
echo ""

iteration=0
while true; do
    iteration=$((iteration + 1))
    echo "📊 Check #$iteration ($(date '+%H:%M:%S')):"
    
    monitor_processes
    check_memory
    
    echo ""
    sleep 10
done
