# whyd — CLI for What Have You Done?!

Command-line time tracker for [What Have You Done?!](https://www.whyd.io), with zsh tab completion.

## Installation

```bash
pip install whyd
```

Or from source:

```bash
git clone https://github.com/xrtic/whyd.git
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

## zsh Completion

Copy `scripts/_whyd` to a directory on your `$fpath`:

```bash
cp scripts/_whyd ~/.zsh/completions/_whyd
```

Make sure that directory is on your fpath in `~/.zshrc`:

```zsh
fpath=(~/.zsh/completions $fpath)
autoload -Uz compinit && compinit
```

Tab completion covers all flags, and `-p` completes from your project list, `-m` from recent messages, and `-t` from common durations.

Run `whyd -refresh` to update the local completion caches after adding new projects or clients.

## License

MIT
