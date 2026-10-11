import unittest
from main import SUGFv3

class TestFVG(unittest.TestCase):
    def setUp(self):
        self.bot = SUGFv3()

    def test_bullish_fvg(self):
        # Bullish FVG: Low of candle 3 is greater than High of candle 1
        candles = [
            {'high': 100, 'low': 90},
            {'high': 120, 'low': 105},
            {'high': 130, 'low': 110} # 110 > 100
        ]
        fvgs = self.bot.calculate_fvg(candles)
        self.assertEqual(len(fvgs), 1)
        self.assertEqual(fvgs[0]['type'], 'bullish')
        self.assertEqual(fvgs[0]['top'], 110)
        self.assertEqual(fvgs[0]['bottom'], 100)
        self.assertEqual(fvgs[0]['middle_candle_index'], 1)

    def test_bearish_fvg(self):
        # Bearish FVG: High of candle 3 is less than Low of candle 1
        candles = [
            {'high': 100, 'low': 90},
            {'high': 85, 'low': 70},
            {'high': 80, 'low': 60} # 80 < 90
        ]
        fvgs = self.bot.calculate_fvg(candles)
        self.assertEqual(len(fvgs), 1)
        self.assertEqual(fvgs[0]['type'], 'bearish')
        self.assertEqual(fvgs[0]['top'], 90)
        self.assertEqual(fvgs[0]['bottom'], 80)
        self.assertEqual(fvgs[0]['middle_candle_index'], 1)

    def test_no_fvg(self):
        candles = [
            {'high': 100, 'low': 90},
            {'high': 105, 'low': 95},
            {'high': 110, 'low': 95} # 95 is not > 100, and 110 is not < 90
        ]
        fvgs = self.bot.calculate_fvg(candles)
        self.assertEqual(len(fvgs), 0)

if __name__ == "__main__":
    unittest.main()