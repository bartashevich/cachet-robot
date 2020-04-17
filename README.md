# CachetHQ Monitoring tool, easy to use and friendly for new components

## How to configure component monitoring
### Check HTTP result code


## Requirements
- CachetHQ version 3.x
- Python 2.x

## Usage
usage: main.py [-h] --url URL --key KEY [--components] [--speedtest]
               [--download-id DOWNLOAD_ID] [--upload-id UPLOAD_ID]
               [--latency-id LATENCY_ID] [--debug]

optional arguments:
  -h, --help            show this help message and exit
  --url URL             Cachet API url ex: http://127.0.0.1/api/v1
  --key KEY             Cachet API key
  --components          Check components status
  --speedtest           Post SpeedTest results on Cachet metrics graph
  --download-id DOWNLOAD_ID
                        Metric ID for download graph (Optional)
  --upload-id UPLOAD_ID
                        Metric ID for upload graph (Optional)
  --latency-id LATENCY_ID
                        Metric ID for latency graph (Optional)
  --debug               Enable debug

## Automation
### Monitoring Cachet components every minute using crontab
\* \* \* \* \* /usr/bin/python /var/www/cachet/cachet-robot/main.py --url http://URL/api/v1 --key API_KEY --components > /dev/null

### Obtain SpeedTest results and save in Cachet metric graphs every 5 minutes using crontab
\*/5 \* \* \* \* /usr/bin/python /var/www/cachet/cachet-robot/main.py --url http://URL/api/v1 --key API_KEY --speedtest --download-id 1 --upload-id 2 --latency-id 3 > /dev/null

## Demo
https://status.engageska-portugal.pt/
