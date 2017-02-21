import unittest
from Garbler import Garbler
from Crumbs import Element
import os
from builders.Drawerer import Drawerer


class DrawererTest(unittest.TestCase):
    @classmethod
    def setUpClass(self):
        self.grblr = Garbler(os.path.join(os.path.dirname(__file__), "..", "files\\config"))
        self.grblr.run_to_end_auto(True)
        crumbs = self.grblr.crumbs
        sample_key = "a"  # nested thesaurus path, has specific asset (a)
        sample_key_x = "x"  # nested thesaurus path, has generic asset (n1, n2, but not n3)
        sample_key_x2 = "x2"  # nested thesaurus path, no asset
        sample_key_y = "y"  # not nested, is in thesaurus, has specific asset (y2)
        sample_key_y2 = "y2"  # not nested, is in thesaurus, no asset
        sample_key_z = "z"  # not in thesaurus, has specific asset (z)
        sample_key_z2 = "z2"  # not in thesaurus, no asset
        crumbs.thesaurus_map[sample_key_x] = ["n1", "n2", "n3"]
        crumbs.thesaurus_map[sample_key_x2] = ["na", "na"]
        crumbs.thesaurus_map[sample_key_y] = []
        crumbs.thesaurus_map[sample_key_y2] = []
        self.drawerer = Drawerer(self.grblr.files_path, crumbs)
        self.drawerer.asset_names = ["n1.png", "n2.png", "y.png", "z.png", "a.png"]
        self.all_keys = [sample_key, sample_key_x, sample_key_x2, sample_key_y,
                         sample_key_y2, sample_key_z, sample_key_z2]

        self.keys_without_asset = [sample_key_x2, sample_key_y2, sample_key_z2]

        # replacement types are always going to be in the instructions
        crumbs.instructions_map[sample_key_x] = ["n1", "n2", "n3"]
        crumbs.instructions_map[sample_key_x2] = ["na", "na"]
        crumbs.instructions_map[sample_key_y] = []
        crumbs.instructions_map[sample_key_y2] = []
        self.drawerer.skeleton_names = ["n1.png", "a.png", "n2.png", "y.png"]
        self.skeleton_type = sample_key  # nested, specific asset
        self.skeleton_type_a = sample_key_x # nested, generic asset
        self.skeleton_type_b = sample_key_x2  # nested, no asset
        self.skeleton_type_c = sample_key_y  # specific asset
        self.skeleton_type_d = sample_key_y2  # no asset

    @classmethod
    def tearDownClass(self):
        self.drawerer = None

    def testGetAssets(self):
        found = self.drawerer.get_assets(self.all_keys)
        self.assertEqual(4, len(found))
        self.assertEqual("a.png", found[0])
        self.assertEqual("n2.png", found[1])
        self.assertEqual("y.png", found[2])
        self.assertEqual("z.png", found[3])

    def testAssetsNotFoundGetsPotato(self):
        found = self.drawerer.get_assets(self.keys_without_asset)
        self.assertEqual(1, len(found))
        self.assertEqual(self.drawerer.potato_token + self.drawerer.extension, found[0])

    def testGetSkeletonNestedSpecific(self):
        found = self.drawerer.get_skeleton(self.skeleton_type, True)
        self.assertEqual("a", found)

    def testGetSkeletonNestedGeneric(self):
        found = self.drawerer.get_skeleton(self.skeleton_type_a, True)
        self.assertEqual("n2", found)

    def testGetSkeletonNestedNoAsset(self):
        found = self.drawerer.get_skeleton(self.skeleton_type_b, True)
        self.assertEqual(self.drawerer.potato_token, found)

    def testGetSkeletonNotNestedSpecificAsset(self):
        found = self.drawerer.get_skeleton(self.skeleton_type_c, True)
        self.assertEqual("y", found)

    def testGetSkeletonNotNestedNoAsset(self):
        found = self.drawerer.get_skeleton(self.skeleton_type_d, True)
        self.assertEqual(self.drawerer.potato_token, found)

    def testGetsCorrectCanvas(self):
        self.expected = "cake"
        self.key = "key"
        self.drawerer.canvas_cache[self.key] = self.expected
        self.grblr.crumbs.instructions_map["subtype"] = ["non existent type" , self.key, "non existent type"]
        location_obj = Element('subtype', '', [])
        canvas_type = self.drawerer.get_canvas(location_obj)
        self.assertEqual(self.expected, canvas_type)