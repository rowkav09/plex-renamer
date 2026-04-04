#!/usr/bin/env bash

ROOT="/r/media/tv"

API_SEARCH="https://api.tvmaze.com/search/shows?q="
API_EPISODES="https://api.tvmaze.com/shows"

declare -a ACTIONS=()

# --- helpers ---

clean_name() {
    echo "$1" | sed 's/[^a-zA-Z0-9 ]//g' | xargs
}

get_show_id() {
    local query="$1"
    curl -s "${API_SEARCH}${query}" | jq '.[0].show.id' 2>/dev/null
}

get_show_name() {
    local query="$1"
    curl -s "${API_SEARCH}${query}" | jq -r '.[0].show.name' 2>/dev/null
}

get_episode_name() {
    local show_id="$1"
    local season="$2"
    local episode="$3"

    curl -s "${API_EPISODES}/${show_id}/episodes" \
        | jq -r ".[] | select(.season==$season and .number==$episode) | .name" 2>/dev/null
}

# --- file processing ---

plan_rename() {
    local file="$1"
    local dir=$(dirname "$file")
    local filename=$(basename "$file")

    if [[ ! "$filename" =~ [sS]([0-9]+)[eE]([0-9]+) ]]; then
        return
    fi

    local season="${BASH_REMATCH[1]}"
    local episode="${BASH_REMATCH[2]}"

    local guess_show=$(clean_name "$(basename "$dir")")

    local show_id=$(get_show_id "$guess_show")
    if [[ -z "$show_id" || "$show_id" == "null" ]]; then
        return
    fi

    local show_name=$(get_show_name "$guess_show")
    local ep_name=$(get_episode_name "$show_id" "$season" "$episode")

    if [[ -z "$ep_name" || "$ep_name" == "null" ]]; then
        return
    fi

    local ext="${file##*.}"

    local new_name="${show_name} - S$(printf "%02d" $season)E$(printf "%02d" $episode) - $ep_name.$ext"
    local new_path="${dir}/${new_name}"

    # Only add if different
    if [[ "$file" != "$new_path" ]]; then
        ACTIONS+=("$file|$new_path")
        echo "PLAN:"
        echo "  $file"
        echo "  -> $new_path"
        echo ""
    fi
}

rename_folders() {
    find "$ROOT" -depth -type d | while read dir; do
        base=$(basename "$dir")
        parent=$(dirname "$dir")

        new_base=$(clean_name "$base")

        if [[ "$base" != "$new_base" ]]; then
            new_path="${parent}/${new_base}"

            ACTIONS+=("$dir|$new_path")

            echo "PLAN (folder):"
            echo "  $dir"
            echo "  -> $new_path"
            echo ""
        fi
    done
}

# --- apply changes ---

commit_changes() {
    for action in "${ACTIONS[@]}"; do
        IFS="|" read -r src dst <<< "$action"

        if [ -e "$dst" ]; then
            echo "SKIP (exists): $dst"
            continue
        fi

        echo "MOVING:"
        echo "  $src"
        echo "  -> $dst"

        mv "$src" "$dst"
    done
}

# --- run ---

echo "Scanning $ROOT..."
echo ""

while IFS= read -r file; do
    case "$file" in
        *.mkv|*.mp4|*.avi|*.mov)
            plan_rename "$file"
            ;;
    esac
done < <(find "$ROOT" -type f)

rename_folders

echo ""
echo "=============================="
echo "Total actions: ${#ACTIONS[@]}"
echo "=============================="

read -p "Commit these changes? (y/n): " confirm

if [[ "$confirm" == "y" || "$confirm" == "Y" ]]; then
    commit_changes
    echo "Done."
else
    echo "Aborted. No changes made."
fi