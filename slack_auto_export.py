#!/usr/bin/env python

import time
import json
import os

import slacker
import click


class SlackAutoExport(object):
    def __init__(self, token, verbose=False):
        self.slack = slacker.Slacker(token)
        self.verbose = verbose

    def _get_channels_list(self):
        return {c["name"]: c for c in
                self.slack.channels.list().body["channels"]}

    def _get_channel_history(self, channel_id, request_pause_period=0.5):
        latest = None
        has_more = True
        messages = []
        while has_more:
            m = self.slack.channels.history(
                channel_id,
                count=1000,
                latest=latest
            )
            messages.extend(m.body['messages'])
            if self.verbose:
                print("{}: Retrieved {} messages from channel {}".format(
                    self.__class__.__name__,
                    len(messages), [c_name for c_name, c in self.channels.items() if c['id'] == channel_id],
                ))

            if m.body['messages']:
                latest = m.body['messages'][-1]['ts']
            has_more = m.body["has_more"]
            time.sleep(request_pause_period)
        return messages

    def _get_history(self):
        channels = self._get_channels_list()
        history = {}
        for channel_name in channels:
            channel_id = channels[channel_name]["id"]
            history[channel_name] = self._get_channel_history(channel_id)
        return history

    def _get_users(self):
        return {c["name"]: c for c in
                self.slack.users.list().body["members"]}

    @property
    def history(self):
        if not hasattr(self, "_history"):
            self._history = self._get_history()
        return self._history

    @property
    def channels(self):
        if not hasattr(self, "_channels"):
            self._channels = self._get_channels_list()
        return self._channels

    @property
    def users(self):
        if not hasattr(self, "_users"):
            self._users = self._get_users()
        return self._users

    def write_history(self, output_dir):
        os.makedirs(os.path.join(output_dir, "channels"), exist_ok=True)

        for channel_name, data in self.history.items():
            self._write_json_file(
                data,
                (
                    output_dir,
                    "channels",
                    "{}.json".format(channel_name)
                )
            )

        self._write_json_file(self.channels, (output_dir, "channels.json"))
        self._write_json_file(self.users, (output_dir, "users.json"))

    def _write_json_file(self, obj, paths):
        filepath = os.path.join(*paths)
        with open(filepath, "w+") as f:
            json.dump(obj, f, indent=4)
            if self.verbose:
                print("Wrote {}".format(filepath))


@click.command()
@click.option('-t', "--token", type=click.STRING, required=True,
              help="Slack API token")
@click.option("-o", "--output-dir", type=click.Path(), required=True,
              help="Output directory for JSON files")
@click.option('-q', '--quiet', is_flag=True,
              help="Set this if you don't want progress printed"
                   " to your terminal.")
def main(token, output_dir, quiet):
    s = SlackAutoExport(token=token, verbose=not quiet)
    s.write_history(output_dir)


if __name__ == '__main__':
    main()
