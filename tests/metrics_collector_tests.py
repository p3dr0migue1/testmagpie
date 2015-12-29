import os
import csv
import unittest
import datetime

from apiclient.discovery import build
from apiclient.http import HttpMockSequence

from metrics_app.settings import base
from metrics_app.metrics_collector import (row_builder,
                                           write_to_csv,
                                           set_date_range,
                                           encode_dict_reader,
                                           query_search_console_data)


class TestSearchConsoleApi(unittest.TestCase):

    def setUp(self):
        self.dates = [
            (u'2015-09-11', u'2015-10-10'),
            (u'2015-10-11', u'2015-11-09'),
            (u'2015-11-10', u'2015-12-12')
        ]
        self.request_data = {
            u'rows': [
                {
                    u'keys': [u'www.simpleexample.com'],
                    u'impressions': 1905291.0,
                    u'clicks': 498250.0,
                    u'ctr': 0.2615086094460111,
                    u'position': 1.048671830182371
                }
            ],
            u'responseAggregationType': u'byProperty'
        }
        self.list_metrics = [
            {
                'CTR': 0.2615086094460111,
                'Clicks': 498250.0,
                'Date Range': u'2015-09-11',
                'Phrase': u'www.example.com',
                'Impressions': 1905291.0,
                'Av Position': 1.048671830182371
            },
            {
                'CTR': 0.2615086094460111,
                'Clicks': 498250.0,
                'Date Range': u'2015-10-10',
                'Phrase': u'www.example.com',
                'Impressions': 1905291.0,
                'Av Position': 1.048671830182371
            }
        ]
        self.DATA_DIR = os.path.join(
            os.path.dirname(os.path.realpath(__file__)), 'fixtures')
        # create csv file
        self.csv_file = os.path.join('csv_test_file.csv')

    def datafile(self, filename):
        return os.path.join(self.DATA_DIR, filename)

    def tearDown(self):
        # remove csv file
        if os.path.exists(self.csv_file):
            os.remove(self.csv_file)

    def test_encode_dict_values_to_utf8(self):
        list_metrics = [
            {
                "BatPhrase": u"Rage AGAINST the MachiNe!",
                "SuperPhrase": u"Another ONE BitEs the Dust!"
            }
        ]
        returned_data = encode_dict_reader(list_metrics)
        self.assertIsInstance(returned_data[0]['BatPhrase'], str)
        self.assertIsInstance(returned_data[0]['SuperPhrase'], str)

    def test_encode_dict_values_to_string(self):
        list_metrics = [
            {
                "SuperClicks": 123456,
                "CrazyClicks": 5.4321
            }
        ]
        returned_data = encode_dict_reader(list_metrics)
        self.assertIsInstance(returned_data[0]['SuperClicks'], str)
        self.assertIsInstance(returned_data[0]['CrazyClicks'], str)

    def test_set_date_range(self):
        base.CLIENT_URL = 'www.example.com'
        base.START_DATE = '2015-09-11'
        base.END_DATE = '2015-12-12'
        build_response_data = self.datafile('response_data.json')
        request_data = self.datafile('date_range_request.json')
        http_auth = HttpMockSequence([
            ({'status': '200'}, open(build_response_data, 'rb').read()),
            ({'status': '200'}, open(request_data, 'rb').read())
        ])
        service = build('webmasters',
                        'v3',
                        http=http_auth,
                        cache_discovery=False)
        returned_data = set_date_range(service)

        for tpl in returned_data:
            self.assertIsInstance(tpl, tuple)
            for item in tpl:
                self.assertIsInstance(
                    datetime.datetime.strptime(item, '%Y-%m-%d'),
                    datetime.datetime
                )
        self.assertEqual(returned_data, self.dates)

    def test_row_builder_with_empty_list_data(self):
        expected = [
            {
                'CTR': 0.2615086094460111,
                'Clicks': 498250.0,
                'Date Range': u'2015-09-11',
                'Phrase': u'www.simpleexample.com',
                'Impressions': 1905291.0,
                'Av Position': 1.048671830182371
            }
        ]
        returned_data = row_builder(self.request_data, u'2015-09-11', [])
        self.assertEqual(returned_data, expected)

    def test_row_builder_with_duplicate_list_data(self):
        list_data = [
            {
                'CTR': 0.2615086094460111,
                'Clicks': 498250.0,
                'Date Range': u'2015-09-11',
                'Phrase': u'www.simpleexample.com',
                'Impressions': 1905291.0,
                'Av Position': 1.048671830182371
            }
        ]
        returned_data = row_builder(
            self.request_data, u'2015-09-11', list_data)

        self.assertEqual(returned_data, list_data)

    def test_query_search_console_data(self):
        base.CLIENT_URL = 'www.example.com'
        # Because the query_search_console function loops through all
        # the items in the IGNORE list (there are 74 items in the list) and
        # executes a request on each loop (148 requests total).
        #
        # This means that we would need to create 148 Mock json request
        # objects to represent each of the 148 requests executed.
        # (more info regarding HtppMocksequence:
        # https://developers.google.com/api-client-library/python/guide/mocks#example_1)
        #
        # As an alternative we can override the contents of the IGNORE list
        base.IGNORE = ['0']
        build_response_data = self.datafile('response_data.json')
        request_data = open(self.datafile('data_request.json'), 'rb').read()

        # duplicate the json request objects
        request_data1 = request_data
        request_data2 = request_data

        http_auth = HttpMockSequence([
            ({'status': '200'}, open(build_response_data, 'rb').read()),
            ({'status': '200'}, request_data1),
            ({'status': '200'}, request_data2)
        ])
        service = build(
            'webmasters',
            'v3',
            http=http_auth,
            cache_discovery=False
        )
        returned_data = query_search_console_data(self.dates[0], service)
        self.assertEqual(returned_data, self.list_metrics)

    def test_write_data_to_csv(self):
        list_data = [
            {
                'CTR': '0.278761869929',
                'Clicks': '520568.0',
                'Date Range': "(u'2015-08-29', u'2015-09-27')",
                'Phrase': 'Superman kicked tha shit out of Batman!',
                'Impressions': '1867429.0',
                'Av Position': '1.05094544424'
            }
        ]
        write_to_csv(list_data, self.csv_file)

        with open(self.csv_file, 'rb') as f:
            reader = csv.DictReader(f)
            csv_data = [row for row in reader]
            # assert that the Phrase in the first row of the csv is equal
            # to the Phrase in the first item of the list_data
            self.assertEqual(csv_data[0]['Phrase'], list_data[0]['Phrase'])
            # assert that the Date Range in the first row of the csv
            # is equal to the Date Range in the first item of the list_data
            self.assertEqual(
                csv_data[0]['Date Range'], list_data[0]['Date Range'])


if __name__ == "__main__":
    unittest.main()
