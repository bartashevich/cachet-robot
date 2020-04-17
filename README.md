# CachetHQ Monitoring tool, easy to use and friendly for new components
This Python script will parse the obtain component data, and accordingly to the tags values monitor that component. Current there are only 3 monitoring mechanisms (check for open port, check ping result and check http return code), but they can be easily modified for personal usage.

## How to configure component monitoring
### Check HTTP result code
For HTTP code check, create a component, set **Link** with the target to monitor and specify in the **Tags** `code, 200` if you are expecting 200 HTTP code.
![code](https://user-images.githubusercontent.com/9809095/79589794-e6612a80-80cd-11ea-989f-345830d3fe28.png)

### Check ping result
For ping check, create a component, set in the **Tags** `ping, 8.8.8.8` if you want to ping 8.8.8.8. Here you can also specify DNS name.
![ping](https://user-images.githubusercontent.com/9809095/79589801-e82aee00-80cd-11ea-86b0-4ac2b0011fcb.png)

### Check port status
For port status check, create a component, set **Tags** `port, 193.136.92.1:1194` if you are expecting **1194** to be open on **193.136.92.1**.
![port](https://user-images.githubusercontent.com/9809095/79589797-e7925780-80cd-11ea-8637-fae27d37abe9.png)

### Metrics
Here I'm interested in Internet, Upload and Latency metrics. But they are option, you don't need to have all 3 metrics for this to work. But you do need to create this manually and write down the ID of each metric for script to know which metrics is which.
![metrics](https://user-images.githubusercontent.com/9809095/79589802-e8c38480-80cd-11ea-9199-742a0040a59a.png)

#### How to obtain metric ID
In the metric edit page you can obtain the ID by grabbing the last number in the URL.
![metric_id](https://user-images.githubusercontent.com/9809095/79589804-e95c1b00-80cd-11ea-8fac-6ef40574f5de.png)

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
