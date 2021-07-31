import unittest
from SeriesDataHolder import SeriesDataHolder


class SeriesDataHolderTest(unittest.TestCase):
    def test_dataflow(self):
        seriesDH = SeriesDataHolder(['mot', 'aux'], 50)

        for idx in range(0,100):
            seriesDH.pushData({'mot':idx,'aux':100-idx})

        data = seriesDH.getData()

        self.assertListEqual(data['mot'], list(range(50, 100)))
        self.assertListEqual(data['aux'], list(range(50, 0, -1)))
        self.assertListEqual(data['idx'], list(range(50, 100)))


if __name__ == '__main__':
    unittest.main()
