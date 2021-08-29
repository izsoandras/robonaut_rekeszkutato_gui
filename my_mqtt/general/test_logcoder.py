import unittest
import LogCoder


class MyTestCase(unittest.TestCase):
    def test_encode(self):
        coder = LogCoder.LogCoder(0)
        msg = coder.encode({'level': 1, 'message': 'Test message'})
        # Ground truth converted with: http://string-functions.com/string-hex.aspx
        msg_gt = bytes.fromhex('01' + ' 54 65 73 74 20 6d 65 73 73 61 67 65')

        self.assertEqual(msg, msg_gt)

    def test_decode(self):
        coder = LogCoder.LogCoder(0)
        payload = bytes.fromhex('01' + ' 54 65 73 74 20 6d 65 73 73 61 67 65')
        data = coder.decode(payload)

        self.assertListEqual(list(data.keys()), ['name', 'level', 'message'])
        self.assertEqual(data['level'], 1)
        self.assertEqual(data['message'], 'Test message')


if __name__ == '__main__':
    unittest.main()
