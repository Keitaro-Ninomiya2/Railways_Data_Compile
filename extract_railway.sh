#!/bin/bash
#SBATCH --time=04:00:00
#SBATCH --mem=32G
#SBATCH --account=keitaro2-ic
#SBATCH --partition=IllinoisComputes-GPU
#SBATCH --gres=gpu:1
#SBATCH --output=railway_extraction_%j.out

set -e # Exit if any command fails

source .venv/bin/activate

echo "Syncing OCR data..."
mkdir -p ./data/1875
# Update this path with the one you just verified
rclone copy "uiucbox:Research Notes (keitaro2@illinois.edu)/RailwayUnions/Processed_Data/ASRS/BalanceSheets/1875" ./data/1875 -P

# Verify files exist before running Python
if [ "$(ls -A ./data/1875)" ]; then
     echo "Files downloaded successfully. Starting LLM Extraction..."
     python ./extract_railway_data.py
else
    echo "Error: Directory ./data/1875 is empty. Check rclone path."
    exit 1
fi

echo "Uploading results..."
rclone copy "extracted_railway_results.csv" "uiucbox:Research Notes (keitaro2@illinois.edu)/RailwayUnions/Processed_Data/ASRS/BalanceSheets/1875/Results/" -P

echo "Pipeline Complete."
