import unittest,json
from pathlib import Path
from tests.reference_runner import verify
class Reference(unittest.TestCase):
    def test_voltage_severity_05(self):
        case=json.loads((Path(__file__).parents[1]/'references/voltage_severity_05.json').read_text(encoding='utf-8'))
        verify(self,case)
