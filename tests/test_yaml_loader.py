import unittest
import yaml
import collections
from microdc.yaml_loader import (readyaml, ordered_load)


class TestYamlLoader(unittest.TestCase):

    def test_readyaml_with_valid_yaml(self):
        """
        If valid YAML is loaded then an ordered dict is returned with valid
        data
        """
        result = readyaml('tests/good_config.yaml')
        self.assertIs(type(result), collections.OrderedDict)
        self.assertEquals(result['project'], 'testproject')
        self.assertEquals(result['accounts']['nonprod']['account_id'], 454545454545)
        self.assertEquals(result['accounts']['nonprod']['environments']['dev']['network_offset'], 0)
        self.assertEquals(result['accounts']['prod']['domain'], 'prod.test.com')

    def test_readyaml_with_invalid_yaml(self):
        """
        If valid arugment is given an ordered dict is returned
        """
        self.assertRaises(yaml.scanner.ScannerError,
                          readyaml,
                          "tests/bad_config.yaml")

    def test_ordered_load(self):
        """
        When given yaml it should come out in the same order
        """
        YAML = """
        apps:
          one: "test"
          two: "test"
          three: "test"
          four: "test"
          five: "test"
        """
        result = ordered_load(YAML, yaml.SafeLoader)
        ordered_apps = []
        for key, value in result['apps'].items():
            ordered_apps.append(key)
        self.assertEquals(ordered_apps,
                          ['one', 'two', 'three', 'four', 'five'])
