import os
import csv
import unittest
import datetime

from apiclient import discovery
from apiclient import http

from metrics_app.metrics_collector import (row_builder,
                                           write_to_csv,
                                           set_date_range,
                                           encode_dict_reader,
                                           query_search_console_data)


class TestSearchConsoleApi(unittest.TestCase):

    def setUp(self):
        self.dates = [('2015-08-31', '2015-09-01')]
        self.response = {
            u'rows': [
                {
                    u'keys': [u'ee'],
                    u'impressions': 1916834.0,
                    u'clicks': 532218.0,
                    u'ctr': 0.2776547160578329,
                    u'position': 1.05003093642955
                }
            ],
            u'responseAggregationType': u'byProperty'
        }

        self.list_metrics = [
            {
                'CTR': 0.2776547160578329,
                'Clicks': 532218.0,
                'Date Range': ('2015-08-31', '2015-09-01'),
                'Phrase': u'ee',
                'Impressions': 1916834.0,
                'Av Position': 1.05003093642955
            }
        ]

        self.fixture_dir = os.path.dirname(os.path.realpath(__file__))
        # create csv file
        self.csv_file = os.path.join('csv_test_file.csv')

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

    # def test_set_date_range(self):
    #     # get the path to the right fixture
    #     fixture = os.path.join(self.fixture_dir, 'set_date_range_fixture.json')

    #     http_auth = http.HttpMock(fixture, {'status': '200'})
    #     service = discovery.build('webmasters', 'v3', http=http_auth)

    #     returned_data = set_date_range(service)
    #     expected_data = [
    #         (u'2015-08-31', u'2015-09-29'),
    #         (u'2015-09-30', u'2015-10-29'),
    #         (u'2015-10-30', u'2015-11-30')
    #     ]
    #     for tpl in returned_data:
    #         self.assertIsInstance(tpl, tuple)
    #         for item in tpl:
    #             self.assertIsInstance(
    #                 datetime.datetime.strptime(item, '%Y-%m-%d'),
    #                 datetime.datetime
    #             )
    #     self.assertEqual(returned_data, expected_data)

    def test_row_builder_with_empty_list_data(self):
        returned_data = row_builder(
            self.response, self.dates[0], [])

        self.assertEqual(returned_data, self.list_metrics)

    def test_row_builder_with_duplicate_list_data(self):
        returned_data = row_builder(
            self.response, self.dates[0], self.list_metrics)

        self.assertEqual(returned_data, self.list_metrics)

    # def test_query_search_console_data(self):
    #     fixture = os.path.join(self.fixture_dir, 'query_data_fixture.json')

    #     http_auth = http.HttpMock(fixture, {'status': '200'})
    #     service = discovery.build('webmasters', 'v3', http=http_auth)
    #     returned_data = query_search_console_data(self.dates, service)

    #     self.assertEqual(returned_data, self.list_metrics)

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
