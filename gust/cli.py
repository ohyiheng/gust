import argparse
from functools import lru_cache
import os

@lru_cache(maxsize=1)
def _get_parser():
    parser = argparse.ArgumentParser(
        prog="gust",
        description="Get Ur Songs Tagged with metadata from Spotify",
    )

    parser_subparsers = parser.add_subparsers(dest="command", required=True)
    parser_tag = parser_subparsers.add_parser("tag", help="tag music files")
    parser_config = parser_subparsers.add_parser("config", help="configure GUST")

    parser_tag.add_argument(
        '-p', '--path',
        type=str,
        default=os.path.curdir,
        help="specify the path to music files, defaults to the current directory",
    )

    parser_tag.add_argument(
        '-i', '--interactive',
        action='store_true',
        help="select tags from query results interactively",
    )

    parser_tag.add_argument(
        '--date-full',
        action='store_true',
        help="use full date instead of just the year",
    )

    parser_tag.add_argument(
        '--always-keep-discs',
        action='store_true',
        help="keep disc tags even if there's only one disc",
    )
    
    parser_config_subparsers = parser_config.add_subparsers(
        dest="config_action",
        required=True,
    )

    parser_config_subparsers.add_parser("api", help="configure spotify's api client id and secret")
    parser_config_subparsers.add_parser("reset", help="reset config file")
    
    return parser

def parse_args(args: list[str] | None = None):
    parser = _get_parser()
    return parser.parse_args(args)