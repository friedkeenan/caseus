from .proxies  import LoggingProxy
from .servers  import LoggingServer
from .sniffers import LoggingSniffer

import argparse

def run_proxy(args):
    print("Proxying...")

    LoggingProxy().run()

def run_server(args):
    print("Serving...")

    LoggingServer().run()

def run_sniffer(args):
    print("Sniffing...")

    # TODO: Add way to supply key sources path.
    LoggingSniffer().run()

def main(args):
    if args.action == "proxy":
        run_proxy(args)

    elif args.action == "server":
        run_server(args)

    elif args.action == "sniffer":
        run_sniffer(args)

parser = argparse.ArgumentParser(prog="caseus")

parser.add_argument("action", choices=["proxy", "server", "sniffer"])

main(parser.parse_args())
