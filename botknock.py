#!/usr/bin/env python
# encoding: utf-8
"""
Twitterbot that doesn't quite get the point of knock-knock jokes.
"""
from __future__ import print_function, unicode_literals
import argparse
import os
import json
import random
import sys
import twitter  # pip install twitter
import webbrowser
import wget  # pip install wget
import yaml  # pip install pyaml

# from pprint import pprint


TWITTER = None

FIRSTNAMES_URL = ("https://raw.githubusercontent.com/dariusk/corpora/master/"
                  "data/humans/firstNames.json")
SURNAMES_URL = ("https://raw.githubusercontent.com/dariusk/corpora/master/"
                "data/humans/authors.json")


def print_it(text):
    """ cmd.exe cannot do Unicode so encode first """
    print(text.encode('utf-8'))


def load_yaml(filename):
    """
    File should contain:
    consumer_key: TODO_ENTER_YOURS
    consumer_secret: TODO_ENTER_YOURS
    access_token: TODO_ENTER_YOURS
    access_token_secret: TODO_ENTER_YOURS
    """
    f = open(filename)
    data = yaml.safe_load(f)
    f.close()
    if not data.viewkeys() >= {
            'access_token', 'access_token',
            'consumer_key', 'consumer_secret'}:
        sys.exit("Twitter credentials missing from YAML: " + filename)
    return data


def tweet_it(string, credentials):
    """ Tweet string using credentials """

    global TWITTER
    if len(string) <= 0:
        return

    # Create and authorise an app with (read and) write access at:
    # https://dev.twitter.com/apps/new
    # Store credentials in YAML file
    if TWITTER is None:
        TWITTER = twitter.Twitter(auth=twitter.OAuth(
            credentials['access_token'],
            credentials['access_token_secret'],
            credentials['consumer_key'],
            credentials['consumer_secret']))

    print_it("TWEETING THIS:\n" + string)

    if args.test:
        print("(Test mode, not actually tweeting)")
    else:
        result = TWITTER.statuses.update(status=string)
        url = "http://twitter.com/" + \
            result['user']['screen_name'] + "/status/" + result['id_str']
        print("Tweeted:\n" + url)
        if not args.no_web:
            webbrowser.open(url, new=2)  # 2 = open in a new tab, if possible


def path_and_filename_from_url(url, data_dir):
    """ Given a URL and directory, return the filename in that dir """
    filename = wget.filename_from_url(url)
    filename = os.path.join(data_dir, filename)
    return filename


def wget_this(url, data_dir):
    """ If the file isn't already in data_dir, download it from url """
    filename = path_and_filename_from_url(url, data_dir)
    if not os.path.exists(filename):
        wget.download(url, data_dir)


def download_data(data_dir):
    """ Download files from Corpora project """
    wget_this(FIRSTNAMES_URL, data_dir)
    wget_this(SURNAMES_URL, data_dir)


def json_from_file(filename):
    with open(filename) as data_file:
        data = json.load(data_file)
    return data


def knockknock(data_dir):
    """ Compose a hilarious knock knock joke """

    # Pick a first name
    filename = path_and_filename_from_url(FIRSTNAMES_URL, data_dir)
    data = json_from_file(filename)
    firstnames = data['firstNames']
    firstname = random.choice(firstnames)

    # Pick a surname
    filename = path_and_filename_from_url(SURNAMES_URL, data_dir)
    data = json_from_file(filename)
    surnames = data['authors']
    surname = random.choice(surnames)

    # Joke time!
    output = ("Knock, knock!\n" +
              "Who's there?\n" +
              firstname + ".\n" +
              firstname + " who?\n" +
              firstname + " " + surname + "!")
    print_it(output)
    return output


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Twitterbot that doesn't quite get the point of "
        "knock-knock jokes.",
        formatter_class=argparse.ArgumentDefaultsHelpFormatter)
    parser.add_argument(
        '-d', '--datadir',
        default='/Users/hugo/Dropbox/bin/data/',
        help="Directory for data files")
    parser.add_argument(
        '-y', '--yaml',
        default='/Users/hugo/Dropbox/bin/data/botknock.yaml',
        help="YAML file location containing Twitter keys and secrets")
    parser.add_argument(
        '-nw', '--no-web', action='store_true',
        help="Don't open a web browser to show the tweeted tweet")
    parser.add_argument(
        '-x', '--test', action='store_true',
        help="Test mode: go through the motions but don't tweet anything")
    args = parser.parse_args()

    download_data(args.datadir)

    tweet = knockknock(args.datadir)

    credentials = load_yaml(args.yaml)
    tweet_it(tweet, credentials)

# End of file
