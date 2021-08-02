import unittest
import PayloadCoder


class GeneralCoderTestCase(unittest.TestCase):
    def test_names_fields_mismatch(self):
        self.assertRaises(AssertionError, PayloadCoder.MessageCoder, *['batt', 0x01, '>HH', ['aux']])
        self.assertRaises(AssertionError, PayloadCoder.MessageCoder, *['batt', 0x01, '>H', ['aux', 'mot']])

    def test_encode(self):
        coder = PayloadCoder.MessageCoder('batt', 0x01, '>HH', ['aux', 'mot'])
        msg = coder.encode({'aux': 2612, 'mot': 1959})
        msg_gt = bytes.fromhex('04 01 0A 34 07 A7')
        self.assertEqual(msg, msg_gt)

    def test_decode(self):
        coder = PayloadCoder.PayloadCoder('batt', 0x01, '>HH', ['aux', 'mot'], [209 / 45500, 209 / 45500])
        payload = bytes.fromhex('0A 34 07 A7')
        data = coder.decode(payload)

        self.assertListEqual(list(data.keys()), ['aux', 'mot'])
        self.assertAlmostEqual(data['aux'],11.99797802)
        self.assertAlmostEqual(data['mot'], 8.998483516)


if __name__ == '__main__':
    unittest.main()
