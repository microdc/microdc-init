import unittest
from microdc.parse_arguments import parse_args


class TestParseArguments(unittest.TestCase):

    def test_parse_args_with_no_options(self):
        """
        If no options are given then we expect a valid arguments object
        """
        result = parse_args([])
        self.assertEquals(result.config, None)
        self.assertEquals(result.account, 'default')

    def test_parse_args_with_valid_options(self):
        """
        If valid options are given then we expect a valid arguments object
        """
        result = parse_args(['--config',
                             '../dir/file.yaml',
                             '--account',
                             'nonprod'])
        self.assertEquals(result.config[0], '../dir/file.yaml')
        self.assertEquals(result.account[0], 'nonprod')
