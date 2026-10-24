import unittest,json
from pathlib import Path
from tests.reference_runner import verify
class Reference(unittest.TestCase):
    def test_real_adequacy_02(self):
        case=json.loads((Path(__file__).parents[1]/'references/real_adequacy_02.json').read_text(encoding='utf-8'))
        verify(self,case)
