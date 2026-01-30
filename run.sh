#!/bin/bash

# ---------CONDA SETUP
CONDA_BASE="$HOME/software/anaconda3"
source "$CONDA_BASE/etc/profile.d/conda.sh"
conda activate jax

BASE_PATH=$HOME/PhD/3d_runs
cd $BASE_PATH

# get date and time for unique output folder
NOW=$(date +"%Y%m%d_%H%M%S")

CONFIGS_PATH="$BASE_PATH/configs"
OUT_PATH="$BASE_PATH/out/$NOW"

# Create necessary directories
mkdir -p "$OUT_PATH"
mkdir -p "$CONFIGS_PATH/done"
mkdir -p "$CONFIGS_PATH/error"

# check that there is nothing in out except the folder of OLD runs
if [ "$(ls -A $OUT_PATH)" ] && [ "$(ls -A $OUT_PATH | grep -v '^[.]$' | grep -v '^done$' | grep -v '^error$')" ]; then
    echo "Error: $OUT_PATH is not empty. Please clear it before running the script."
    exit 1
fi

for FILE in "$CONFIGS_PATH"/*.txt; do
    # Skip if no .txt files exist
    [ -e "$FILE" ] || continue

    NAME=$(basename "$FILE" .txt)
    OUT_DIR="$OUT_PATH"
    OVERRIDES=""

    while IFS= read -r line; do
        [[ "$line" =~ ^#.*$ ]] && continue
        [[ -z "$line" ]] && continue
        OVERRIDES+="--override $line "
    done < "$FILE"

    OVERRIDES+="--override output.save_dir=$OUT_DIR"

    # --- EXECUTION & ERROR HANDLING ---
    
    # Create a temporary file for the current run's errors
    TEMP_ERR=$(mktemp)

    # Run the command, sending stderr to the temp file
    qvarnet run -c ./base.json $OVERRIDES 2> "$TEMP_ERR"
    EXIT_CODE=$?

    # Always show the errors in the terminal regardless of success/fail
    # (Use 'cat' to print the contents of the error buffer)
    if [ -s "$TEMP_ERR" ]; then
        cat "$TEMP_ERR" >&2
    fi

    if [ $EXIT_CODE -eq 0 ]; then
        # Success: Move config to done and delete the temp error log
        mv "$FILE" "$CONFIGS_PATH/done/"
        rm "$TEMP_ERR"
    else
        # Failure: Move config to error AND save the log permanently
        echo "Error detected in $NAME. Exit code: $EXIT_CODE"
        mv "$FILE" "$CONFIGS_PATH/error/"
        mv "$TEMP_ERR" "$OUT_PATH/${NAME}_error.txt"
    fi
    
done