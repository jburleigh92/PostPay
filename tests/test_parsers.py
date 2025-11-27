import unittest

from parsers.zelle_parser import ZelleParser
from parsers.venmo_parser import VenmoParser
from parsers.cashapp_parser import CashAppParser
from parsers.apple_parser import AppleParser
from parsers.other_parsers import OtherParser


class TestParsers(unittest.TestCase):

    def test_zelle_parser(self):
        body = (
            "You received $45.00 from John Doe via Zelle on February 3, 2024 1:14 PM."
        )
        p = ZelleParser()
        result = p.parse(body)

        self.assertIsNotNone(result)
        self.assertEqual(result["provider"], "Zelle")
        self.assertEqual(result["amount"], "$45.00")
        self.assertEqual(result["sender"], "John Doe")

    def test_venmo_parser(self):
        body = "John Smith paid you $27.50 on February 4, 2024 9:32 AM."
        p = VenmoParser()
        result = p.parse(body)

        self.assertIsNotNone(result)
        self.assertEqual(result["provider"], "Venmo")
        self.assertEqual(result["amount"], "$27.50")
        self.assertEqual(result["sender"], "John Smith")

    def test_cashapp_parser(self):
        body = (
            "You received $18.25 from Jane Roe. Jane Roe sent you money using Cash App."
        )
        p = CashAppParser()
        result = p.parse(body)

        self.assertIsNotNone(result)
        self.assertEqual(result["provider"], "Cash App")
        self.assertEqual(result["amount"], "$18.25")
        self.assertEqual(result["sender"], "Jane Roe")

    def test_apple_parser(self):
        body = (
            "You received $55.00 from Mike Thompson using Apple Cash on Feb 2, 2024."
        )
        p = AppleParser()
        result = p.parse(body)

        self.assertIsNotNone(result)
        self.assertEqual(result["provider"], "Apple Cash")
        self.assertEqual(result["amount"], "$55.00")
        self.assertEqual(result["sender"], "Mike Thompson")

    def test_other_parser(self):
        body = (
            "You received a payment of $120.00 from Acme Services for invoice #00401."
        )
        p = OtherParser()
        result = p.parse(body)

        self.assertIsNotNone(result)
        self.assertEqual(result["provider"], "Other")
        self.assertEqual(result["amount"], "$120.00")
        self.assertEqual(result["sender"], "Acme Services")


if __name__ == "__main__":
    unittest.main()
