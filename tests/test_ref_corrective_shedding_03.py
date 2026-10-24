import unittest,json
from pathlib import Path
from tests.reference_runner import verify
class Reference(unittest.TestCase):
    def test_corrective_shedding_03(self):
        case=json.loads((Path(__file__).parents[1]/'references/corrective_shedding_03.json').read_text(encoding='utf-8'))
        verify(self,case)
