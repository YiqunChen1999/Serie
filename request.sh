#!/bin/zsh
# nohup ./request.sh >> outputs/nohup.out &
# filepath: /Users/yiqunchen/Library/CloudStorage/OneDrive-中国科学院自动化研究所/projects/arxiv/arxiv_manager.sh

source /Users/yiqunchen/.zshrc

script_folder="${0:a:h}"
python="$HOME/miniconda3/envs/serie/bin/python" 
main="$script_folder/serie/main.py"


# Function to run jobs in background
run_job() {
    nohup $python $main --pipeline Request --overwrite True >> ./outputs/scheduled-yesterday.txt &
    nohup $python $main --pipeline Request --datetime $(date -v-3d +%Y-%m-%d) >> ./outputs/scheduled.txt &
    echo "Submitted job to background at $(date)"
}

# Calculate seconds until target time
get_sleep_seconds() {
    target="$1"  # Format: "YYYY-MM-DD HH:MM"
    
    # Get current and target timestamps
    current_ts=$(date +%s)
    target_ts=$(date -j -f "%Y-%m-%d %H:%M" "$target" +%s)
    
    # Calculate difference
    diff_seconds=$((target_ts - current_ts))
    
    # Return positive value only
    if [ $diff_seconds -lt 0 ]; then
        echo 0
    else
        echo $diff_seconds
    fi
}

# Sleep until specified time
sleep_until_time() {
    target="$1"  # Format: "YYYY-MM-DD HH:MM"
    echo "Wait Until Time: $target"
    sleep_seconds=$(get_sleep_seconds "$target")
    echo "Sleeping $sleep_seconds seconds"
    sleep $sleep_seconds
}

# Schedule recurring jobs
schedule_requests() {
    local wait_until_time=${1:-"$(date -v+1d +%Y-%m-%d) 11:45"}
    
    # Endless loop to schedule the job daily
    while true; do
        sleep_until_time "$wait_until_time"
        run_job
        # Update wait_until_time to the next day
        wait_until_time=$(date -v+1d -j -f "%Y-%m-%d %H:%M" "$wait_until_time" "+%Y-%m-%d %H:%M")
    done
}

wait_until_time=${1:-"$(date -v+1d +%Y-%m-%d) 11:45"}
while true; do
    schedule_requests "$wait_until_time"
    wait_until_time=$(date -v+1d -j -f "%Y-%m-%d %H:%M" "$wait_until_time" "+%Y-%m-%d %H:%M")
    echo "Next scheduled time: $wait_until_time"
done
