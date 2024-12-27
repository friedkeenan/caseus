from . import util

from .proxies import LoggingProxy
from .servers import LoggingServer

import argparse

def run_proxy(args):
    print("Proxying...")

    LoggingProxy().run()

def run_server(args):
    print("Serving...")

    LoggingServer().run()

def run_shakikoo(args):
    print("Shakikoo hash:", util.shakikoo(args.target))

def main(args):
    if args.action == "proxy":
        run_proxy(args)

    elif args.action == "server":
        run_server(args)

    elif args.action == "shakikoo":
        run_shakikoo(args)

parser = argparse.ArgumentParser(prog="caseus")

subparsers = parser.add_subparsers()

proxy_parser = subparsers.add_parser("proxy")
proxy_parser.set_defaults(action="proxy")

server_parser = subparsers.add_parser("server")
server_parser.set_defaults(action="server")

shakikoo_parser = subparsers.add_parser("shakikoo")
shakikoo_parser.set_defaults(action="shakikoo")

shakikoo_parser.add_argument("target", help="The string to hash")

main(parser.parse_args())
