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
            # Complete from project cache
            if [[ -f ~/.whyd/projectcache ]]; then
                local projects
                projects=$(tr -d "'" < ~/.whyd/projectcache | cut -d':' -f1 | tr -d ' ')
                COMPREPLY=( $(compgen -W "$projects" -- "$cur") )
            fi
            return
            ;;
        -c)
            # Complete from client cache
            if [[ -f ~/.whyd/clientcache ]]; then
                local clients
                clients=$(tr -d "'" < ~/.whyd/clientcache | cut -d':' -f1 | tr -d ' ')
                COMPREPLY=( $(compgen -W "$clients" -- "$cur") )
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
