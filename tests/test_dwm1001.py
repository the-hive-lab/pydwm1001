# Standard library imports
import unittest

# Third party imports
import dwm1001


class MockSerial:
    def __init__(self, response: bytes = b"") -> None:
        self.response = response
        self.write_history = []

    def readline(self) -> bytes:
        return self.response

    def write(self, value: bytes) -> None:
        self.write_history.append(value)


class TestTagPosition(unittest.TestCase):
    def test_construction(self) -> None:
        position = dwm1001.TagPosition(1.23, 4.56, 7.89, 42)

        self.assertAlmostEqual(position.x_m, 1.23)
        self.assertAlmostEqual(position.y_m, 4.56)
        self.assertAlmostEqual(position.z_m, 7.89)
        self.assertEqual(position.quality, 42)

    def test_almost_equal(self) -> None:
        position1 = dwm1001.TagPosition(1.23, 4.56, 7.89, 42)
        position2 = dwm1001.TagPosition(1.23, 4.56, 7.89, 42)

        self.assertTrue(position1.almost_equal(position2))


class TestListener(unittest.TestCase):
    def test_construction(self) -> None:
        serial_handle = MockSerial()
        dwm1001.Listener(serial_handle)

        self.assertEqual(serial_handle.write_history[0], b"\r\r")
        self.assertEqual(serial_handle.write_history[1], b"lep")

    def test_wait_for_position_report_good(self) -> None:
        serial_handle = MockSerial(b"POS,1,TEST1,1.23,4.56,7.89,20,86")
        listener = dwm1001.Listener(serial_handle)

        tag_id, tag_position = listener.wait_for_position_report()
        self.assertEqual(tag_id, "TEST1")

        expected_position = dwm1001.TagPosition(1.23, 4.56, 7.89, 20)
        self.assertTrue(tag_position.almost_equal(expected_position))

    def test_wait_for_position_report_short(self) -> None:
        serial_handle = MockSerial(b"POS,1,TEST1,1.23,4.56,7.89")
        listener = dwm1001.Listener(serial_handle)

        self.assertRaises(ValueError, listener.wait_for_position_report)

    def test_wait_for_position_report_wrong_header(self) -> None:
        serial_handle = MockSerial(b"BAD,1,TEST1,1.23,4.56,7.89")
        listener = dwm1001.Listener(serial_handle)

        self.assertRaises(ValueError, listener.wait_for_position_report)


if __name__ == "__main__":
    unittest.main()