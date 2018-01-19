import os
import logging
import unittest
import datetime
import shutil
import numpy as np

from sentinelhub.ogc import OgcService
from sentinelhub.data_request import WmsRequest, WcsRequest, OgcRequest
from sentinelhub.constants import CRS, MimeType, CustomUrlParam, DataSource
from sentinelhub.common import BBox


logging.basicConfig(level=logging.DEBUG,
                    format='%(asctime)-15s %(module)s:%(lineno)d [%(levelname)s] %(funcName)s  %(message)s')

INSTANCE_ID = os.environ.get('INSTANCE_ID')


class TestOgcServices(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        bbox = BBox(bbox=(47.94, -5.23, 48.17, -5.03), crs=CRS.WGS84)
        cls.request = OgcRequest(image_format=MimeType.TIFF_d32f, layer='ALL_BANDS', maxcc=1.0,
                                 data_folder='TestOutputs', bbox=bbox, time=('2017-10-01', '2017-10-31'),
                                 time_difference=datetime.timedelta(days=10),
                                 source=DataSource.WMS, instance_id=INSTANCE_ID)

    def test_get_dates(self):
        dates = OgcService.get_dates(self.request)
        self.assertEqual(len(dates), 3, msg="Expected 3 dates, got {}".format(len(dates)))

    @classmethod
    def tearDownClass(cls):
        shutil.rmtree('./TestOutputs/', ignore_errors=True)


class TestWmsService(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        bbox = BBox(bbox=(47.94, -5.23, 48.17, -5.03), crs=CRS.WGS84)
        cls.stat_expect = {'min': 0.0008, 'max': 0.6438, 'mean': 0.2307, 'median': 0.2397}
        cls.request_save = WmsRequest(data_folder='TestOutputs', image_format=MimeType.TIFF_d32f, layer='ALL_BANDS',
                                      maxcc=1.0, width=512, height=512, bbox=bbox, time=('2017-10-01', '2017-10-02'),
                                      instance_id=INSTANCE_ID)
        cls.data_save = cls.request_save.get_data(save_data=True, redownload=True)

        cls.request_get = WmsRequest(image_format=MimeType.TIFF_d32f, layer='ALL_BANDS',
                                     maxcc=1.0, width=512, height=512, bbox=bbox, time=('2017-10-01', '2017-10-02'),
                                     instance_id=INSTANCE_ID)
        cls.data_get = cls.request_get.get_data()

    def test_return_type(self):
        self.assertTrue(isinstance(self.data_save, list), "Expected a list")
        self.assertEqual(len(self.data_save), 1,
                         "Expected a list of length 1, got length {}".format(str(len(self.data_save))))
        self.assertTrue(isinstance(self.data_get, list), "Expected a list")
        self.assertEqual(len(self.data_get), 1,
                         "Expected a list of length 1, got length {}".format(str(len(self.data_get))))

    def test_stats(self):
        stat_values_save = {'min': np.amin(self.data_save[0]), 'max': np.amax(self.data_save[0]),
                            'mean': np.mean(self.data_save[0]), 'median': np.median(self.data_save[0])}
        stat_values_get = {'min': np.amin(self.data_get[0]), 'max': np.amax(self.data_get[0]),
                           'mean': np.mean(self.data_get[0]), 'median': np.median(self.data_get[0])}
        for stat_name in self.stat_expect.keys():
            with self.subTest(msg=stat_name):
                expected = self.stat_expect[stat_name]
                real_val_save = stat_values_save[stat_name]
                self.assertAlmostEqual(expected, real_val_save, delta=1e-4,
                                       msg="Expected {}, got {}".format(str(expected), str(real_val_save)))
                real_val_get = stat_values_get[stat_name]
                self.assertAlmostEqual(expected, real_val_get, delta=1e-4,
                                       msg="Expected {}, got {}".format(str(expected), str(real_val_get)))

    @classmethod
    def tearDownClass(cls):
        shutil.rmtree('./TestOutputs/', ignore_errors=True)


class TestCustomUrlParameters(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        bbox = BBox(bbox=(47.94, -5.23, 48.17, -5.03), crs=CRS.WGS84)

        cls.stat_expect_atmfilter = {'min': 12, 'max': 255, 'mean': 190.0, 'median': 199.0}
        cls.stat_expect_preview = {'min': 28, 'max': 253, 'mean': 171.8, 'median': 171.0}
        cls.stat_expect_evalscript_url = {'min': 17, 'max': 255, 'mean': 162.4, 'median': 159.0}
        cls.stat_expect_evalscript = {'min': 0, 'max': 233, 'mean': 45.8, 'median': 54.0}

        cls.request_atmfilter = WmsRequest(data_folder='TestOutputs', image_format=MimeType.PNG, layer='TRUE_COLOR',
                                           maxcc=1.0, width=512, height=512, bbox=bbox, instance_id=INSTANCE_ID,
                                           time=('2017-10-01', '2017-10-02'),
                                           custom_url_params={CustomUrlParam.ATMFILTER: 'ATMCOR',
                                                              CustomUrlParam.QUALITY: 100,
                                                              CustomUrlParam.DOWNSAMPLING: 'BICUBIC',
                                                              CustomUrlParam.UPSAMPLING: 'BICUBIC'})

        cls.request_preview = WmsRequest(data_folder='TestOutputs', image_format=MimeType.PNG, layer='TRUE_COLOR',
                                         maxcc=1.0, width=512, height=512, bbox=bbox, time=('2017-10-01', '2017-10-02'),
                                         instance_id=INSTANCE_ID, custom_url_params={CustomUrlParam.PREVIEW: 2})

        cls.request_evalscript_url = WmsRequest(data_folder='TestOutputs', image_format=MimeType.PNG,
                                                layer='TRUE_COLOR', maxcc=1.0, width=512, height=512, bbox=bbox,
                                                time=('2017-10-01', '2017-10-02'), instance_id=INSTANCE_ID,
                                                custom_url_params={CustomUrlParam.EVALSCRIPTURL:
                                                                   'https://raw.githubusercontent.com/sentinel-hub/'
                                                                   'customScripts/master/sentinel-2/false_color_'
                                                                   'infrared/script.js'})
        cls.request_evalscript = WmsRequest(data_folder='TestOutputs', image_format=MimeType.PNG, layer='TRUE_COLOR',
                                            maxcc=1.0, width=512, height=512, bbox=bbox,
                                            time=('2017-10-01', '2017-10-02'), instance_id=INSTANCE_ID,
                                            custom_url_params={CustomUrlParam.EVALSCRIPT: 'return [B10,B8A,B03]'})

        cls.data_atmfilter = cls.request_atmfilter.get_data(redownload=True)
        cls.data_preview = cls.request_preview.get_data(redownload=True)
        cls.data_evalscript_url = cls.request_evalscript_url.get_data(redownload=True)
        cls.data_evalscript = cls.request_evalscript.get_data(redownload=True)

    def test_return_type(self):
        self.assertTrue(isinstance(self.data_atmfilter, list), "Expected a list")
        self.assertEqual(len(self.data_atmfilter), 1,
                         "Expected a list of length 1, got length {}".format(str(len(self.data_atmfilter))))
        self.assertTrue(isinstance(self.data_preview, list), "Expected a list")
        self.assertEqual(len(self.data_preview), 1,
                         "Expected a list of length 1, got length {}".format(str(len(self.data_preview))))
        self.assertTrue(isinstance(self.data_evalscript_url, list), "Expected a list")
        self.assertEqual(len(self.data_evalscript_url), 1,
                         "Expected a list of length 1, got length {}".format(str(len(self.data_evalscript_url))))
        self.assertTrue(isinstance(self.data_evalscript, list), "Expected a list")
        self.assertEqual(len(self.data_evalscript), 1,
                         "Expected a list of length 1, got length {}".format(str(len(self.data_evalscript_url))))

    def test_download_url(self):
        self.assertTrue(CustomUrlParam.ATMFILTER.value in self.request_atmfilter.get_url_list()[-1],
                        'AtmFilter parameter not in download url.')
        self.assertTrue(CustomUrlParam.QUALITY.value in self.request_atmfilter.get_url_list()[-1],
                        'Quality parameter not in download url.')
        self.assertTrue(CustomUrlParam.DOWNSAMPLING.value in self.request_atmfilter.get_url_list()[-1],
                        'Downsampling parameter not in download url.')
        self.assertTrue(CustomUrlParam.UPSAMPLING.value in self.request_atmfilter.get_url_list()[-1],
                        'Upsampling parameter not in download url.')

    def test_stats(self):
        atmfilter_values = {'min': np.amin(self.data_atmfilter[0]), 'max': np.amax(self.data_atmfilter[0]),
                            'mean': np.mean(self.data_atmfilter[0]), 'median': np.median(self.data_atmfilter[0])}
        preview_values = {'min': np.amin(self.data_preview[0]), 'max': np.amax(self.data_preview[0]),
                          'mean': np.mean(self.data_preview[0]), 'median': np.median(self.data_preview[0])}
        evalscript_url_values = {'min': np.amin(self.data_evalscript_url[0]),
                                 'max': np.amax(self.data_evalscript_url[0]),
                                 'mean': np.mean(self.data_evalscript_url[0]),
                                 'median': np.median(self.data_evalscript_url[0])}
        evalscript_values = {'min': np.amin(self.data_evalscript[0]), 'max': np.amax(self.data_evalscript[0]),
                             'mean': np.mean(self.data_evalscript[0]), 'median': np.median(self.data_evalscript[0])}

        for stat_name in self.stat_expect_atmfilter.keys():
            with self.subTest(msg='atmfilter_'+stat_name):
                expected = self.stat_expect_atmfilter[stat_name]
                real_val = atmfilter_values[stat_name]
                self.assertAlmostEqual(expected, real_val, delta=1e-1,
                                       msg="Expected {}, got {}".format(str(expected), str(real_val)))

        for stat_name in self.stat_expect_preview.keys():
            with self.subTest(msg='preview_'+stat_name):
                expected = self.stat_expect_preview[stat_name]
                real_val = preview_values[stat_name]
                self.assertAlmostEqual(expected, real_val, delta=1e-1,
                                       msg="Expected {}, got {}".format(str(expected), str(real_val)))

        for stat_name in self.stat_expect_evalscript_url.keys():
            with self.subTest(msg='evalscripturl_'+stat_name):
                expected = self.stat_expect_evalscript_url[stat_name]
                real_val = evalscript_url_values[stat_name]
                self.assertAlmostEqual(expected, real_val, delta=1e-1,
                                       msg="Expected {}, got {}".format(str(expected), str(real_val)))

        for stat_name in self.stat_expect_evalscript.keys():
            with self.subTest(msg='evalscript_'+stat_name):
                expected = self.stat_expect_evalscript[stat_name]
                real_val = evalscript_values[stat_name]
                self.assertAlmostEqual(expected, real_val, delta=1e-1,
                                       msg="Expected {}, got {}".format(str(expected), str(real_val)))

    @classmethod
    def tearDownClass(cls):
        shutil.rmtree('./TestOutputs/', ignore_errors=True)


class TestWmsServiceIO(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        bbox = BBox(bbox=(47.94, -5.23, 48.17, -5.03), crs=CRS.WGS84)
        cls.request = WmsRequest(data_folder='WmsIOTest', image_format=MimeType.PNG, layer='TRUE_COLOR', maxcc=1.0,
                                 width=512, height=512, time='latest', bbox=bbox, instance_id=INSTANCE_ID)
        cls.data = cls.request.get_data(save_data=False, redownload=True)

    def test_return_type(self):
        self.assertTrue(isinstance(self.data, list), "Expected a list")
        self.assertEqual(len(self.data), 1, "Expected a list of length 1, got length {}".format(str(len(self.data))))
        self.assertTrue(isinstance(self.data[0], np.ndarray), "Expected numpy array")
        self.assertEqual(self.data[0].shape, (512, 512, 3),
                         "Expected shape (512, 512, 3), got {}".format(str(self.data[0].shape)))

    @classmethod
    def tearDownClass(cls):
        shutil.rmtree('./WmsIOTest/', ignore_errors=True)


class TestWcsService(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        bbox = BBox((8.655, 111.7, 8.688, 111.6), crs=CRS.WGS84)
        cls.stat_expect = {'min': 0.1443, 'max': 0.4915, 'mean': 0.3565, 'median': 0.4033}
        cls.request = WcsRequest(data_folder='TestOutputs', bbox=bbox, layer='ALL_BANDS', resx='10m', resy='20m',
                                 time=('2017-01-01', '2017-02-01'), maxcc=1.0, image_format=MimeType.TIFF_d32f,
                                 instance_id=INSTANCE_ID)
        cls.data = cls.request.get_data(save_data=True, redownload=True)
        cls.dates = cls.request.get_dates()

    def test_return_type(self):
        self.assertTrue(isinstance(self.data, list), "Expected a list")
        self.assertEqual(len(self.data), 2, "Expected a list of length 2, got length {}".format(str(len(self.data))))
        self.assertTrue(isinstance(self.dates, list), "Expected a list")
        self.assertEqual(len(self.dates), 2, "Expected a list of length 2, got length {}".format(str(len(self.dates))))

    def test_stats(self):
        stat_values = {'min': np.amin(self.data[0]), 'max': np.amax(self.data[0]), 'mean': np.mean(self.data[0]),
                       'median': np.median(self.data[0])}

        for stat_name in self.stat_expect.keys():
            with self.subTest(msg=stat_name):
                expected = self.stat_expect[stat_name]
                real_val = stat_values[stat_name]
                self.assertAlmostEqual(expected, real_val, delta=1e-4,
                                       msg="Expected {}, got {}".format(str(expected), str(real_val)))

    def test_dates(self):
        exp_dates = [
            datetime.datetime.strptime('2017-01-02T03:04:33', '%Y-%m-%dT%H:%M:%S'),
            datetime.datetime.strptime('2017-01-12T03:04:10', '%Y-%m-%dT%H:%M:%S')
        ]

        self.assertEqual(exp_dates[0], self.dates[0], msg="Expected {}, got {}".format(str(exp_dates[0]),
                                                                                       str(self.dates[0])))
        self.assertEqual(exp_dates[1], self.dates[1], msg="Expected {}, got {}".format(str(exp_dates[1]),
                                                                                       str(self.dates[1])))

    @classmethod
    def tearDownClass(cls):
        shutil.rmtree('./TestOutputs/', ignore_errors=True)


if __name__ == '__main__':
    unittest.main()
