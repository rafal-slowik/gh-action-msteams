import pymsteams
import os
import logging
import json

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(threadName)s -  %(levelname)s - %(message)s')

job_status = os.environ.get("STATUS")
job_name = os.environ.get("JOB_NAME")
workflow_name = os.environ.get("WORKFLOW_NAME")
facts = os.environ.get("FACTS")
repo_server_url = os.environ.get("REPO_SERVER_URL")
repo_name = os.environ.get("REPO_NAME")
hook_url = os.environ.get("WEBHOOK_URI")
triggering_actor = os.environ.get("TRIGGERING_ACTOR")
github_sha = os.environ.get("GITHUB_SHA")
run_id = os.environ.get("RUN_ID")


def send_sectioned_message():
    """
        This sends a message with sections.
    """

    input_data = determine_input()
    # start the message
    teams_message = pymsteams.connectorcard(hook_url)
    teams_message.title(f"Workflow '{workflow_name}' {input_data['status']}")
    teams_message.text(f"{ repo_server_url }/{ repo_name }/commit/{ github_sha }")

    # section 1
    section_1 = pymsteams.cardsection()
    # section_1.title(input_data["title"])
    section_1.activityTitle(f"Triggering actor: {triggering_actor}")
    section_1.activityImage(input_data["iconUrl"])

    # add link button
    teams_message.addLinkButton("Go to the action", f"{ repo_server_url }/{ repo_name }/actions/runs/{ run_id }")

    # add facts
    for k, v in json.loads(facts).items():
        section_1.addFact(k, v)
    for k, v in dict({"Job name": f"{job_name}", "Workflow name": f"{workflow_name}"}).items():
        section_1.addFact(k, v)
    teams_message.addSection(section_1)
    teams_message.color(input_data["color"])
    # teams_message.printme()
    # send
    teams_message.send()
    evaluate_response(teams_message.last_http_response.status_code)


def evaluate_response(resp_status_code):
    if isinstance(resp_status_code, int) and \
            0 <= resp_status_code <= 299:
        logging.info("Response code ok: %s", resp_status_code)
    else:
        logging.error("Unexpected response: %s", resp_status_code)
        raise ValueError(f"Unexpected response: '{resp_status_code}'")


def determine_input():
    """
        This function determines and icon, color and a title text based on the status of the job.
        The expected status values 'failed', 'cancelled', 'success'
    """

    msg = f"Job name: '{job_name}' of the workflow '{workflow_name}'"
    match job_status:
        case 'failure':
            return {
                "iconUrl": "https://raw.githubusercontent.com/rafal-slowik/gh-action-msteams/master/icons/fail.png",
                "color": "ae1314",
                "title": f"{msg} has failed",
                "status": "failed"
            }
        case 'cancelled':
            return {
                "iconUrl": "https://raw.githubusercontent.com/rafal-slowik/gh-action-msteams/master/icons/"
                           "cancelled-screenshot.png",
                "color": "ffec50",
                "title": f"{msg} has been cancelled",
                "status": "cancelled"
            }
        case 'success':
            return {
                "iconUrl": "https://raw.githubusercontent.com/rafal-slowik/gh-action-msteams/master/icons/success.png",
                "color": "2cc73b",
                "title": f"{msg} has successfully finished",
                "status": "succeeded"
            }
        case _:
            logging.error("Unexpected response: %s", job_status)
            raise ValueError(f"The job_status contains unexpected value: '{job_status}'")
