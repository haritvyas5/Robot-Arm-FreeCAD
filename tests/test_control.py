"""Check parsing and angle mapping without requiring FreeCAD."""
from pathlib import Path
import sys
import unittest

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from robot_arm import read_values, to_angle


class Controls(unittest.TestCase):
    def test_valid_and_invalid_readings(self):
        self.assertEqual(read_values("0,512,1023,9\r"), [0, 512, 1023, 9])
        for line in ["1,2,3", "1,2,3,4,5", "-1,2,3,4", "1024,2,3,4",
                     "a,2,3,4", "1.5,2,3,4", ""]:
            self.assertIsNone(read_values(line))

    def test_mapping_and_reverse_direction(self):
        self.assertEqual(to_angle(0, (-90, 90)), -90)
        self.assertEqual(to_angle(1023, (-90, 90)), 90)
        self.assertEqual(to_angle(0, (90, -90)), 90)
        self.assertAlmostEqual(to_angle(511.5, (-90, 90)), 0)


if __name__ == "__main__":
    unittest.main()
