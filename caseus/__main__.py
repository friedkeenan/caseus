from .proxies  import LoggingProxy
from .sniffers import LoggingSniffer

import argparse

def run_proxy(args):
    print("Proxying...")

    LoggingProxy().run()

def run_sniffer(args):
    print("Sniffing...")

    # TODO: Add way to supply key sources path.
    LoggingSniffer().run()

def main(args):
    if args.action == "proxy":
        run_proxy(args)

    elif args.action == "sniff":
        run_sniffer(args)

parser = argparse.ArgumentParser(prog="caseus")

parser.add_argument("action", choices=["proxy", "sniff"])

main(parser.parse_args())
