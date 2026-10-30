import unittest

from checks import check_facts, check_style
from schema import ProductCopy

FACTS = {"name": "Summit Dry Bag", "category": "Packs", "material": "70D nylon with TPU coating",
         "weight_g": "120 g", "color": "orange", "capacity_l": "10 l", "waterproof_rating": "IPX6"}


def copy(description, title="Summit Dry Bag", used=("name",)):
    return ProductCopy(title=title, description=description,
                       bullets=["Roll-top closure", "10 l capacity", "Weighs 120 g"],
                       meta_title=title, meta_description=description[:155],
                       used_attributes=list(used))


class CheckTest(unittest.TestCase):

    def test_listed_facts_pass(self):
        text = "A 10 l orange dry bag in 70D nylon. It is waterproof to IPX6 and weighs 0.12 kg."
        self.assertEqual(check_facts(copy(text), FACTS), [])

    def test_invented_number_and_spec(self):
        text = "A 10 l dry bag with a lifetime warranty, made of 420D ripstop."
        self.assertEqual(check_facts(copy(text), FACTS),
                         ["invented number: 420", "invented spec: lifetime",
                          "invented spec: warranty"])

    def test_unknown_attribute(self):
        text = "A 10 l dry bag."
        self.assertEqual(check_facts(copy(text, used=("name", "seam_type")), FACTS),
                         ["unknown attribute: seam_type"])

    def test_banned_word_and_exclamation(self):
        text = "The ultimate dry bag!"
        self.assertEqual(check_style(copy(text), ["ultimate", "perfect"]),
                         ["banned word: ultimate", "banned word: exclamation mark"])


if __name__ == "__main__":
    unittest.main()
