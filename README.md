# whyd — CLI for What Have You Done?!

This is a command line utility designed to be used in conjunction with [What Have You Done?!](https://www.whyd.io), an incredibly flexible time tracking solution that also has unix command line plus an ios application. 

This repository is for the command-line utility which includes zsh tab completion.

Example:
```bash
16:45:14]:kurt@macbook:~ $ whyd -month
                                                 Time Tracked This Month                                                  
┏━━━━━━┳━━━━━━━━━━┳━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┳━━━━━━━━━━━━━━━━━━━━━━━━━┳━━━━━━━━━━━━━━━━━━━┳━━━━━━━━━━━━━━━━━━━━━┓
┃ ID   ┃ Dur.     ┃ Message                          ┃ Project                 ┃ Client            ┃ Start               ┃
┡━━━━━━╇━━━━━━━━━━╇━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━╇━━━━━━━━━━━━━━━━━━━━━━━━━╇━━━━━━━━━━━━━━━━━━━╇━━━━━━━━━━━━━━━━━━━━━┩
│ 553d │ 300m     │ Dashboard of Dashboards          │ Applications wor (45e5) │ Blue Bana (b302)  │ 08/03/2026 09:00 AM │
│ 1d40 │ 120m     │ Monday sync with Tony            │ Applications wor (45e5) │ Blue Bana (b302)  │ 08/11/2026 11:30 AM │
│ 4ed4 │ 45m      │ Apple Store login                │ Operations/Netwo (8d9f) │ Blue Bana (b302)  │ 08/11/2026 01:00 PM │
│ 21e6 │ 30m      │ Meeting with John                │ Developer Coachi (2cd5) │ Applix (15ad)     │ 08/04/2026 09:00 AM │
├──────┼──────────┼──────────────────────────────────┼─────────────────────────┼───────────────────┼─────────────────────┤
│      │ 14h 45m  │                                  │                         │                   │                     │
└──────┴──────────┴──────────────────────────────────┴─────────────────────────┴───────────────────┴─────────────────────┘

```

## Installation

```bash
pip install whyd
```

Or from source:

```bash
git clone https://github.com/DreadPirateFlint/whyd.git
cd whyd
pip install .
```

## Configuration

Create `~/.whyd/config` with your credentials:

```bash
mkdir -p ~/.whyd
cat > ~/.whyd/config <<EOF
API_KEY=your-api-key-here
WHYD_URL=https://api.whyd.io/
HOME_DIR=~/.whyd
EOF
```

Your API key is on the Account page at [whyd.io](https://www.whyd.io).

You can also override the API key at runtime with the `WHYD_API_KEY` environment variable:

```bash
WHYD_API_KEY=your-key whyd -today
```

## Usage

```
Time Tracking:
  whyd -n -p <project> -t <duration> -m <message>   Add a time entry
  whyd -s                                            Start the internal timer
  whyd -v                                            View elapsed timer time
  whyd -x                                            Record and reset timer
  whyd -clear                                        Discard the current timer

Reporting:
  whyd -today                List time tracked today
  whyd -week                 List time tracked this week
  whyd -month                List time tracked this month
  whyd -lastmonth            List time tracked last month
  whyd -c <client>           Filter reports by client ID
  whyd -ap                   List all projects/clients (parsable)
  whyd -apt                  List all projects/clients (table)
  whyd -d <n>                Delete entry #n from the last report
```

**Duration format:** `1h`, `30m`, `1h30m`

### Examples

```bash
# Log 90 minutes to a project
whyd -n -p ab12 -t 1h30m -m "Implemented login flow"

# See what you tracked today
whyd -today

# Start a timer, then record it later
whyd -s
whyd -x
```

## Shell Completion

Tab completion covers all flags. `-p` completes from your project list, `-c` from clients, `-m` from recent messages, and `-t` from common durations.

Run `whyd -refresh` to update the local caches after adding new projects or clients.

### zsh

Copy `scripts/_whyd` to a directory on your `$fpath`:

```bash
cp scripts/_whyd ~/.zsh/completions/_whyd
```

Make sure that directory is on your fpath in `~/.zshrc`:

```zsh
fpath=(~/.zsh/completions $fpath)
autoload -Uz compinit && compinit
```

### bash

Add this to your `~/.bashrc`:

```bash
source /path/to/whyd-completion.bash
```

Or install system-wide:

```bash
sudo cp scripts/whyd-completion.bash /etc/bash_completion.d/whyd
```

## License

MIT
