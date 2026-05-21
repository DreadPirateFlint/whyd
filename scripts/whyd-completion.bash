# whyd bash completion
#
# Installation:
#   Source this file in your ~/.bashrc:
#     source /path/to/whyd-completion.bash
#
#   Or copy it to the system completions directory:
#     sudo cp whyd-completion.bash /etc/bash_completion.d/whyd

_whyd_completions() {
    local cur prev
    cur="${COMP_WORDS[COMP_CWORD]}"
    prev="${COMP_WORDS[COMP_CWORD-1]}"

    # Flags that take an argument
    case "$prev" in
        -p)
            # Complete with full "ident: Project Name, Client" so user can see context
            if [[ -f ~/.whyd/projectcache ]]; then
                local -a projects
                while IFS= read -r line; do
                    line="${line//\'/}"
                    [[ -n "$line" ]] && projects+=("$line")
                done < ~/.whyd/projectcache
                COMPREPLY=( $(compgen -W "${projects[*]}" -- "$cur") )
                compopt -o nospace 2>/dev/null
            fi
            return
            ;;
        -c)
            # Complete with full "ident: Client Name" so user can see context
            if [[ -f ~/.whyd/clientcache ]]; then
                local -a clients
                while IFS= read -r line; do
                    line="${line//\'/}"
                    [[ -n "$line" ]] && clients+=("$line")
                done < ~/.whyd/clientcache
                COMPREPLY=( $(compgen -W "${clients[*]}" -- "$cur") )
                compopt -o nospace 2>/dev/null
            fi
            return
            ;;
        -t)
            local durations="5m 10m 15m 30m 45m 1h 1h30m 2h 3h 4h"
            COMPREPLY=( $(compgen -W "$durations" -- "$cur") )
            return
            ;;
        -m|--msg)
            # Complete from message cache
            if [[ -f ~/.whyd/messagecache ]]; then
                local messages
                messages=$(tr -d "'" < ~/.whyd/messagecache | cut -d':' -f1)
                COMPREPLY=( $(compgen -W "$messages" -- "$cur") )
            fi
            return
            ;;
        -d)
            # No useful completions for a row index
            return
            ;;
    esac

    # Top-level flags
    local flags="-n -t -p -m --msg -s -v -x -clear -d -c -ap -apt -today -week -month -lastmonth -refresh -pcomp -ccomp -mcomp"
    COMPREPLY=( $(compgen -W "$flags" -- "$cur") )
}

complete -F _whyd_completions whyd
