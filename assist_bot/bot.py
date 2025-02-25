import os
import time
import re
import json
from slack import WebClient

# instantiate Slack client
client = WebClient(token=os.environ.get('SLACK_BOT_TOKEN'))
# starterbot's user ID in Slack: value is assigned after the bot starts up
starterbot_id = None

# constants
RTM_READ_DELAY = 1 # 1 second delay between reading from RTM
ALERT_REGEX = "[[]FIRING:[0-9]+[]](.*)[(]"

def parse_events(slack_events):
    """
        Returns message events that match an alert
    """
    # for each event received
    for event in slack_events:
        # if the event is a message (https://api.slack.com/events/message)
        if event["type"] == "message" and not "subtype" in event:
            # try to extract an alert 
            alert = parse_message(event["text"])
            # if an alert message is detected
            if alert:
                # return this event and alert for further processing
                return event, alert
    # return nothing otherwise
    return None, None


def parse_message(message_text):
    """
        Finds a message that matches an alert from Prometheus, 
        extracts the alert name and returns it
    """
    matches = re.search(ALERT_REGEX, message_text)
    # Split the alert name and cluster to remove the cluster name, then return the alert name
    return " ".join(matches.group(1).strip(" ").split()[:-1]) if matches else None


def handle_alert(event, alert):
    """
        Process the alert and send message to thread
    """
    # TODO: Process message
    # Sends the response back to the channel
    client.chat_postMessage(
        channel=event["channel"],
        thread_ts=event["ts"],
        text=""
    )


def main():
    if client.rtm_connect(with_team_state=False):
        print("Starter Bot connected and running!")
        # Read bot's user ID by calling Web API method `auth.test`
        starterbot_id = client.api_call("auth.test")["user_id"]

        with open("resources/alerts.json") as fd:
            alerts = json.load(fd)

        while True:
            event, alert = parse_events(client.rtm_read())
            if event:
                handle_alert(event, alert)
            time.sleep(RTM_READ_DELAY)
    else:
        print("Connection failed. Exception traceback printed above.")


if __name__ == "__main__":
    main()
