#!/usr/bin/env python3

import os
import sys
import subprocess
import multiprocessing
import argparse
import json
import distutils.spawn

# IPFS directory where the monkey metadata is stored. See baseURI() in:
# https://etherscan.io/token/0xbc4ca0eda7647a8ab7c2061c2e118a18a936f13d#readContract
MONKEY_DIR = "QmeSjSinHpPnmXmspMjwiXyN6zS4E9zccariGR3jxcaWtq"


def get_monkey(monkey_id):
    """Download the specified monkey."""

    monkey_fname = f"{monkey_id:05d}.png"
    print(monkey_fname)

    # skip this monkey if it's on disk already
    if os.path.isfile(monkey_fname):
        return True, monkey_fname

    # fetch the monkey's metadata
    cmd_meta = ["ipfs", "cat", f"/ipfs/{MONKEY_DIR}/{monkey_id:d}"]
    print(" ".join(cmd_meta))
    with subprocess.Popen(cmd_meta, stdout=subprocess.PIPE) as proc_metadata:
        monkey_metadata = proc_metadata.communicate()[0]
        print("MM>", monkey_metadata)
        if not monkey_metadata:
            sys.stderr.write("IPFS failed. Remember to run \"ipfs daemon\" first.\n")
            return False, monkey_fname
    monkey_json = json.loads(monkey_metadata)

    # fetch the monkey image data
    cmd_png = ["ipfs", "cat", monkey_json["image"][7:]]
    print(" ".join(cmd_png))
    with subprocess.Popen(cmd_png, stdout=subprocess.PIPE) as proc_monkey:
        monkey_png = proc_monkey.communicate()[0]
        if not monkey_png:
            sys.stderr.write(f"Couldn't retrieve tokenID {monkey_id:d}\n")
            return False, monkey_fname

    # write the monkey image
    with open(monkey_fname, "wb") as fd:
        fd.write(monkey_png)

    return True, monkey_fname


def download_monkeys(threads=multiprocessing.cpu_count(), min_monkey=0, max_monkey=10000):
    """Download all of the monkeys (multithreaded)."""
    print(threads, "threads")
    if 1 == threads:
        for monkey_id in range(min_monkey, max_monkey + 1):
            assert(get_monkey(monkey_id)[0])
    else:
        with multiprocessing.Pool(threads) as pool:
            for result in pool.imap_unordered(get_monkey, range(min_monkey, max_monkey + 1)):
                assert(result[0])


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Download 10,000 monkey cartoons.')
    parser.add_argument('-t', dest="threads", type=int, nargs=1,
                        default=[multiprocessing.cpu_count()],
                        help='parallel threads')

    args = parser.parse_args()

    if distutils.spawn.find_executable("ipfs"):
        download_monkeys(threads=args.threads[0])
    else:
        print("NOPE")
