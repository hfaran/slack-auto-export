# slack-auto-export

A simple library, and command-line tool, to export your team's entire history using Slack's API. All you need is a token.

`slack-auto-export` performs the function as Slack's web export service; only better because this is programmatic and can be automated for a rolling history archive.

## Usage

### Command-Line Tool

```bash
pip install -r requirements.txt
./slack_auto_export.py --help
/slack_auto_export.py -t your-api-token -o /path/to/output/dir
```
