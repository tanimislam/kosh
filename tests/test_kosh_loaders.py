import os
from koshbase import KoshTest
import kosh
import h5py


class KoshTestLoaders(KoshTest):
    def test_loader(self):
        store, kosh_db = self.connect()
        ds = store.create(metadata={"key1": 1, "key2": "A"})
        ds.associate(
            "tests/baselines/node_extracts2/node_extracts2.hdf5", "hdf5")
        l, _ = store._find_loader(ds._associated_data_[0])
        self.assertEqual(sorted(l.known_types()), ["hdf5"])
        self.assertEqual(l.known_load_formats("file"), [])
        os.remove(kosh_db)

    def test_generic_loader(self):
        store, kosh_db = self.connect()
        ds = store.create(metadata={"key1": 1, "key2": "A"})
        ds.associate("setup.py", "ascii")
        l, _ = store._find_loader(ds._associated_data_[0])
        self.assertIsInstance(l, kosh.loaders.core.KoshFileLoader)
        self.assertEqual(sorted(l.known_types()), ["file"])
        self.assertEqual(l.known_load_formats("file"), [])
        self.assertIsInstance(ds.get(None), list)
        os.remove(kosh_db)

    def test_images(self):
        store, kosh_db = self.connect()
        ds = store.create(metadata={"key1": 1, "key2": "A"})
        ds.associate(
            "tests/baselines/images/LLNLiconWHITE.png", "png")
        features = sorted(ds.list_features())
        self.assertEqual(features, ["image", ])
        ds.get("image")
        # Duplicate features names URI should be added
        ds.associate(
            "share/icons/png/Kosh_Logo_Blue.png", "png")
        features = sorted(ds.list_features(use_cache=False))[::-1]
        self.assertEqual(features, ["image_@_{}/tests/baselines/images/LLNLiconWHITE.png".format(os.getcwd()),
                                    "image_@_{}/share/icons/png/Kosh_Logo_Blue.png".format(os.getcwd())])

        ds = store.create(metadata={"key1": 1, "key2": "A"})
        ds.associate("tests/baselines/images/buffalo.pgm", "pgm")
        img = ds.get("image")
        self.assertEqual(img.shape, (321, 481))

        ds = store.create(metadata={"key1": 1, "key2": "A"})
        ds.associate("tests/baselines/images/brain_398.ascii.pgm", "pgm")
        img = ds.get("image")
        self.assertEqual(img.shape, (486, 720))

        info = ds.describe_feature("image")

        self.assertEqual(sorted(info.keys()), ["format", "max_value", "size"])
        self.assertEqual(info["format"], "pgm (P2)")
        self.assertEqual(info["max_value"], 255)
        ds.associate("share/icons/png/Kosh_Logo_Blue.png", mime_type="png")
        self.assertEqual(sorted(ds.list_features(use_cache=False))[::-1],
                         ['image_@_{}/tests/baselines/images/brain_398.ascii.pgm'.format(os.getcwd()),
                          'image_@_{}/share/icons/png/Kosh_Logo_Blue.png'.format(
                              os.getcwd())])  # URI is now added to feature to deambiguous them
        info = ds.describe_feature(
            "image_@_{}/share/icons/png/Kosh_Logo_Blue.png".format(os.getcwd()))
        self.assertEqual(info["size"], (1035, 403))
        data = ds.get(
            "image_@_{}/share/icons/png/Kosh_Logo_Blue.png".format(os.getcwd()))
        self.assertEqual(data.shape[:-1], info["size"][::-1])

    def test_hdf5(self):
        store, kosh_db = self.connect()
        ds = store.create(metadata={"key1": 1, "key2": "A"})
        kosh_id = ds.associate(
            "tests/baselines/node_extracts2/node_extracts2.hdf5", "hdf5")
        features = sorted(ds.list_features())
        self.assertEqual(features,
                         ['cycles', 'direction', 'elements', 'node/metrics_0',
                          'node/metrics_1', 'node/metrics_10', 'node/metrics_11',
                          'node/metrics_12', 'node/metrics_2', 'node/metrics_3',
                          'node/metrics_4', 'node/metrics_5', 'node/metrics_6',
                             'node/metrics_7', 'node/metrics_8', 'node/metrics_9',
                             'zone/metrics_0', 'zone/metrics_1', 'zone/metrics_2',
                          'zone/metrics_3', 'zone/metrics_4'])
        features = sorted(
            ds.list_features(
                None,
                group="node",
                use_cache=False))
        self.assertEqual(features,
                         ['metrics_0', 'metrics_1', 'metrics_10', 'metrics_11',
                          'metrics_12', 'metrics_2', 'metrics_3',
                          'metrics_4', 'metrics_5', 'metrics_6',
                             'metrics_7', 'metrics_8', 'metrics_9', ])

        features = sorted(
            ds.list_features(
                ds._associated_data_[0],
                group="node",
                use_cache=False))
        self.assertEqual(features,
                         ['metrics_0', 'metrics_1', 'metrics_10', 'metrics_11',
                          'metrics_12', 'metrics_2', 'metrics_3',
                          'metrics_4', 'metrics_5', 'metrics_6',
                             'metrics_7', 'metrics_8', 'metrics_9', ])
        data = ds.get("node/metrics_1")
        self.assertEqual(data.shape, (2, 18))
        data = ds.get("node/metrics_1", cycles=slice(1, 2), elements=[47, 79])
        self.assertEqual(data.shape, (1, 2))
        ds.associate("tests/baselines/images/brain_398.ascii.pgm", "pgm")
        info = ds.describe_feature("node/metrics_1")
        self.assertEqual(info["size"], (2, 18))
        self.assertEqual(info["format"], "hdf5")
        h5 = ds.open(Id=kosh_id, mode="r")
        self.assertIsInstance(h5, h5py._hl.files.File)
        self.assertEqual(h5.mode, "r")
        h5.close()
        h5 = ds.open(Id=kosh_id, mode="r+")
        self.assertEqual(h5.mode, "r+")
        h5.close()
        os.remove(kosh_db)
