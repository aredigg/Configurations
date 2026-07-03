# based on Andreas Korb SteamShutdown, MIT license
acf_to_json() {
    local -a raw_lines=("$@")
    local -a lines
    local l i

    lines+=('"__root__"')
    lines+=('{')
    for l in "${raw_lines[@]}"; do
        lines+=($'\t'"$l")
    done
    lines+=('}')

    local n=${#lines[@]}
    local output=""
    local next key value

    local re_single=$'^(\t+".+")\t\t(".*")$'
    local re_start_of_object=$'^\t+".+"$'

    for ((i = 2; i <= n; i++)); do
        line="${lines[i]}"
        next="${lines[i + 1]}"

        if [[ "$line" =~ $re_single ]]; then
            key="${match[1]}"
            value="${match[2]}"
            output+="${key}: ${value}"

            if ((i + 1 <= n)) && [[ "$next" == *"}" ]]; then
                output+=$'\n'
            else
                output+=$',\n'
            fi

        elif [[ "$line" == $'\t'* && "$line" == *"}" ]]; then
            output+="$line"

            if ((i + 1 <= n)) && [[ "$next" == *"}" ]]; then
                output+=$'\n'
            else
                output+=$',\n'
            fi

        elif [[ "$line" =~ $re_start_of_object ]]; then
            output+="${line}:"$'\n'

        else
            output+="${line}"$'\n'
        fi
    done

    print -r -- "$output"
}

acf_data=$(curl -sf "https://client-update.steamstatic.com/steam_client_osx")
acf_lines=("${(f)acf_data}")
json_output=$(acf_to_json "${acf_lines[@]}")
zip_file=$(jq .osx.appdmg_osx.file <<<$json_output)
zip_file=${zip_file//\"/}
temp_dir=$(mktemp -d)
curl -L# "https://client-update.steamstatic.com/$zip_file" -o "$temp_dir/appdmg_osx.zip"
unzip -q "$temp_dir/appdmg_osx.zip" -d "$temp_dir"
tar xf "$temp_dir/SteamMacBootstrapper.tar.gz" -C "$temp_dir"
cp -R "$temp_dir/Steam.app" "/Applications/"
xattr -dr com.apple.quarantine "/Applications/Steam.app"
package_dir="$HOME/Library/Application Support/Steam/package"
mkdir -p "$package_dir"
echo "publicbeta" >"$package_dir/beta"
rm -rf "$temp_dir"
