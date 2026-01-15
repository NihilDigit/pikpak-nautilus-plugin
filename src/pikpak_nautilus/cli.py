import argparse
from .installer import install, uninstall

def main():
    parser = argparse.ArgumentParser(description="PikPak Nautilus Plugin Manager")
    subparsers = parser.add_subparsers(dest="command", help="Commands")
    
    subparsers.add_parser("install", help="Install the Nautilus extension")
    subparsers.add_parser("uninstall", help="Uninstall the Nautilus extension")
    
    args = parser.parse_args()
    
    if args.command == "install":
        install()
    elif args.command == "uninstall":
        uninstall()
    else:
        parser.print_help()

if __name__ == "__main__":
    main()
