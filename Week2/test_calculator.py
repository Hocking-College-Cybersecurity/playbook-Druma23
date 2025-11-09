import unittest

from Week2.calculator import compute


class TestCalculator(unittest.TestCase):
    def test_add(self):
        self.assertEqual(compute('+', 2, 3), 5)

    def test_subtract(self):
        self.assertEqual(compute('-', 5, 3), 2)

    def test_multiply(self):
        self.assertEqual(compute('*', 4, 3), 12)

    def test_divide(self):
        self.assertEqual(compute('/', 10, 2), 5)

    def test_division_by_zero(self):
        self.assertEqual(compute('/', 1, 0), "Error: Division by zero")

    def test_invalid_operator(self):
        self.assertEqual(compute('%', 1, 2), "Invalid operator")

    def test_operator_with_whitespace(self):
        self.assertEqual(compute(' + ', 1, 2), 3)


if __name__ == '__main__':
    unittest.main()
