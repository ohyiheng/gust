import argparse
import pytest
from gust.cli import parse_args

class TestParser():

    def test_no_arguments(self):
        with pytest.raises(SystemExit):
            parse_args([])

    def test_tag(self):
        args = parse_args(["tag"])
        assert args.command == "tag"

    def test_config(self):
        args = parse_args(["config", "api"])
        assert args.config_action == "api"

    def test_flags(self):
        args = parse_args(["tag", "-i", "--date-full"])
        assert args.interactive == True
        assert args.date_full == True
