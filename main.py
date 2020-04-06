import argparse
import os
import socket
import urllib2
from datetime import datetime
from cachet import Cachet
import json


def get_status_code(url):
    try:
        connection = urllib2.urlopen(url)
        code = connection.getcode()
        connection.close()
        return code
    except urllib2.HTTPError as e:
        return e.getcode()


def get_ping_status(host):
    try:
        ret = os.system("ping -c 1 " + host)
        if ret == 0:
            return True
        else:
            return False
    except Exception as e:
        return False


def get_port_status(host_port):
    ip = host_port.split(':')[0]
    port = host_port.split(':')[1]

    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    try:
        s.connect((ip, int(port)))
        s.shutdown(2)
        return True
    except:
        return False


def time_diff_in_seconds(time2):
    date_time_format = '%Y-%m-%d %H:%M:%S'  # type: str
    time1 = datetime.now()
    time_dif = time1 - datetime.strptime(time2, date_time_format)
    return int(time_dif.total_seconds())


def api_login(url, key):
    return Cachet(url, key)


def speed_test_monitoring(client, download_id, upload_id, latency_id):
    # obtain speed_test results
    speed_test = json.loads(os.popen("speedtest-cli --json").read().replace('\n',''))

    # export speed test values
    download = float(speed_test['download']) / (1000 * 1000) # Mbps
    upload = float(speed_test['upload']) / (1000 * 1000) # Mbps
    latency = float(speed_test['server']['latency']) # ms

    if args.debug:
        print("Download speed: %s Mbps" % download)
        print("Upload speed: %s Mbps" % upload)
        print("Latency: %s ms" % latency)

    # post download metric
    if download_id != 0:
        client.postMetricsPointsByID(download_id, download)

    # post upload metric
    if upload_id != 0:
        client.postMetricsPointsByID(upload_id, upload)

    # post latency metric
    if latency_id != 0:
        client.postMetricsPointsByID(latency_id, latency)


def component_monitoring(client):
    # get components
    request = client.getComponents().json()
    components = request['data']

    # in case there is more than 1 page of components
    while int(request['meta']['pagination']['current_page']) < int(request['meta']['pagination']['total_pages']):
        request = client.getComponents({'page': int(request['meta']['pagination']['current_page'] + 1)}).json()
        components += request['data']

    for item in components:
        # if component does not have tags or not enabled continue
        if len(item['tags']) == 0 or not item['enabled']:
            continue

        # components values
        component_id = item['id']
        component_name = item['name']
        component_link = item['link']
        component_tags = item['tags'].values()
        component_status = item['status']
        component_created_at = item['created_at']
        component_updated_at = item['updated_at']

        component_query_status = False

        # verify HTTP respond code
        if 'code' in component_tags:
            # remove code from tags list
            component_tags.remove('code')

            # goal HTTP code
            http_code = component_tags[0]

            # actual HTTP code
            result_code = get_status_code(component_link)

            if int(http_code) == int(result_code):
                component_query_status = True
            else:
                component_query_status = False

        # verify ping response
        elif 'ping' in component_tags:
            # remove ping from tags list
            component_tags.remove('ping')

            # ip address to ping
            ip_address = component_tags[0]

            if get_ping_status(ip_address):
                component_query_status = True
            else:
                component_query_status = False

        # verify port status (TCP only)
        elif 'port' in component_tags:
            # remove port from tags list
            component_tags.remove('port')

            # ip address with port (ex: 127.0.0.1:443)
            host_port = component_tags[0]

            if get_port_status(host_port):
                component_query_status = True
            else:
                component_query_status = False

        # print debug values
        if args.debug:
            print("Component %s analysis returned %b",component_name,component_query_status)

        # result analysis
        if component_query_status:
            # if components status is not operational
            if component_status != 1:
                # update incident as fixed
                incident = client.searchIncidents(component_id=component_id, status=2, order='desc', per_page=1).json()

                # if incident exists, write an update message
                if len(incident['data']) > 0:
                    client.postIncidentUpdate(incident['data'][0]['id'], 4, "The component has successfully recovered")

            # mark component as operational
            client.putComponentsByID(id=component_id, status=1)

        else:
            # could not be a failure (reboot), wait 5 minutes before raising a flag
            # mark component as suffering from Performance Issue
            if component_status == 1:
                client.putComponentsByID(id=component_id, status=2)

            # partial failure (after 5 minutes since last component status update)
            elif component_status == 2 and time_diff_in_seconds(component_updated_at) > 5 * 60:
                # create incident about the failure, marking component as suffering from Partial Outage
                client.postIncidents("Service Disruption", "Component did not answer during the past 5 minutes", 2, 1,
                                     component_id=component_id, component_status=3)

            # complete failure (after 25 minutes since last component status update)
            elif component_status == 3 and time_diff_in_seconds(component_updated_at) > 25 * 60:
                # mark component as suffering from Major Outage
                client.putComponentsByID(id=component_id, status=4)

                # obtain incident object
                incident = client.searchIncidents(component_id=component_id, status=2, order='desc', per_page=1).json()

                # if incident exists, write an update message
                if len(incident['data']) > 0:
                    client.postIncidentUpdate(incident['data'][0]['id'], 2,
                                              "Component continues not answering during past 30 minutes")


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--url', dest='url', required=True, help="Cachet API url ex: http://127.0.0.1/api/v1")
    parser.add_argument('--key', dest='key', required=True, help="Cachet API key")
    parser.add_argument('--components', action='store_true', help="Check components status")
    parser.add_argument('--speedtest', action='store_true', help="Post SpeedTest results on Cachet metrics graph")
    parser.add_argument('--download-id', type=int, default=0, help="Metric ID for download graph (Optional)")
    parser.add_argument('--upload-id', type=int, default=0, help="Metric ID for upload graph (Optional)")
    parser.add_argument('--latency-id', type=int, default=0, help="Metric ID for latency graph (Optional)")
    parser.add_argument('--debug', action='store_true', help="Enable debug")
    args = parser.parse_args()

    print(args)

    api = api_login(args.url, args.key)

    if "data" not in api.ping().json():
        print("Unable to establish connection with the API server")
        exit(1)

    if args.components:
        component_monitoring(api)

    if args.speedtest:
        speed_test_monitoring(api, args.download_id, args.upload_id, args.latency_id)
