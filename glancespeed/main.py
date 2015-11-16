import argparse
from .core import glancespeed


def main():
    parser = argparse.ArgumentParser(description='Glance page speed')
    parser.add_argument('host', help='The host you want to test.')
    args = parser.parse_args()
    glancespeed(args.host)

if __name__ == '__main__':
    main()
