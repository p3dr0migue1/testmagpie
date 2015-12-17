import argparse
import csv
import httplib2
import logging

from apiclient import discovery
from oauth2client import client
from oauth2client.file import Storage
from oauth2client import tools

from settings import base


logging.basicConfig()


def execute_request(service, client_url, request):
    """
    Executes a searchAnalytics.query request.

    :param service:       The webmasters service to use when executing the
                          query.
    :param client_url:    The site or app URI to request data for.
    :param request:       The request to be executed.

    :returns:             An array of response rows.
    """
    return service.searchanalytics().query(siteUrl=client_url,
                                           body=request).execute()


def get_credentials():
    """
    This function checks for credentials, in the storage data file.
    If no credentials are stored of if the stored credentials
    are invalid, new credentials are return by the function run_flow().
    The new credentials are also stored in the storage argument, which
    updates the file associated with the Storage object.

    :returns credentials:    credentials object
    """
    flow = client.flow_from_clientsecrets(base.CLIENT_SECRET,
                                          scope=base.SCOPE,
                                          redirect_uri=base.REDIRECT_URI)
    storage = Storage(base.STORAGE_FILE)
    credentials = storage.get()
    if credentials is None or credentials.invalid:
        parser = argparse.ArgumentParser(parents=[tools.argparser])
        flags = parser.parse_args(['--noauth_local_webserver'])
        credentials = tools.run_flow(flow=flow, storage=storage, flags=flags)

    return credentials


def set_date_range(service):
    """
    Set the date range available by querying the Search Console API with a
    simple query. This will return the list of available dates, which should
    always be 90 days in length. There is an offset of between 3 and 6 days
    from todays date that needs to be accounted for, hence starting the query
    on 2015-01-01.

    This function is designed to gather the data by 30 day period, i.e. day 0
    to day 29, day 30 to day 59, etc.

    :returns query_dates:    List of tuples, containing string formatted
                             dates.
    """
    list_of_dates = []
    request_body = {'startDate': base.START_DATE,
                    'endDate': base.END_DATE,
                    'dimensions': ['date']}

    response = execute_request(service, base.CLIENT_URL, request_body)

    for row in response['rows']:
        list_of_dates.append(row['keys'][0])

    query_dates = [(list_of_dates[0], list_of_dates[29]),
                   (list_of_dates[30], list_of_dates[59]),
                   (list_of_dates[60], list_of_dates[-1])]

    return query_dates


def query_search_console_data(query_dates, service):
    """
    Query the Search Console using ignore characters, and date ranges.
    Returns raw unencoded data.

    :param query_dates:    query dates, list of tuples for 30 day splits
    :param service:        service object
    """
    list_data = []
    for date in query_dates:
        for character in base.IGNORE:
            request_body = {
                'startDate': '{}'.format(date[0]),
                'endDate': '{}'.format(date[1]),
                'dimensions': ['query'],
                'dimensionFilterGroups': [
                    {'groupType': 'and',
                     'filters': [
                         {'dimension': 'query',
                          'operator': 'notContains',
                          'expression': character}]}
                ],
                'rowLimit': 1}
            request_data = execute_request(
                service, base.CLIENT_URL, request_body
            )
            metrics_list = row_builder(request_data, date, list_data)

    return metrics_list


def row_builder(request_data, date, list_data):
    """
    Creates a dictionary and appends to a list

    :param request_data:     a list of dictionaries
    :param data:             a tuple of date strings yyyy-mm-dd
    :param list_data:        a list to write the dictionary too

    :returns list_data:  returns a list of dictionaries
    """
    for row in request_data['rows']:
        new_row = {
            'Date Range': date,
            'Phrase': row['keys'][0],
            'Impressions': row['impressions'],
            'Clicks': row['clicks'],
            'CTR': row['ctr'],
            'Av Position': row['position']
        }
        # don't add the row to list if there is one that already matches
        if new_row not in list_data:
            list_data.append(new_row)

    return list_data


def write_to_csv(list_data, csv_file):
    """
    Create a csv file from a list of lists

    :param list_data:    A list of dictionaries
    """
    keys = set([key for item in list_data for key in item.keys()])
    with open(csv_file, 'wb') as f:
        writer = csv.DictWriter(f, fieldnames=keys)
        # write headers
        writer.writeheader()
        for item in list_data:
            # write the data into the rows according to the headers
            writer.writerow(item)


def encode_dict_reader(data):
    """
    Loops through a list of dictionaries and returns a list of encoded
    dictionaries.

    :param data:          list of dictionaries
    :returns list_data:   list of dictionaries
    """
    list_data = []
    for item in data:
        # encode to utf-8 if the instance is unicode, otherwise, make it a
        # string.
        for key, value in item.iteritems():
            if isinstance(value, unicode):
                item[key] = value.encode('utf-8')
            else:
                item[key] = str(value)
            list_data.append(item)
    return list_data


def main():
    credentials = get_credentials()
    http_auth = credentials.authorize(httplib2.Http())
    service = discovery.build('webmasters', 'v3', http=http_auth)
    query_dates = set_date_range(service)
    api_data = query_search_console_data(query_dates, service)
    encoded_csv_data = encode_dict_reader(api_data)
    csv_file = base.CSV_PATH
    write_to_csv(encoded_csv_data, csv_file)
