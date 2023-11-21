import os

from ipfabric import IPFClient

from .classDefinitions import AristaCvpWebhook, Settings


def write_logs(timestamp: str, cvp_webhooks: AristaCvpWebhook, log_folder: str):
    """
    Writes the given AristaCvpWebhook object to a log file with the specified timestamp.

    Args:
        timestamp (str): The timestamp to be included in the log line.
        cvp_webhook: The AristaCvpWebhook object to be logged.
    """
    os.makedirs(log_folder, exist_ok=True)
    log_line = f"{timestamp} {cvp_webhooks}"

    # We create a new log file for each day
    log_file_path = os.path.join(log_folder, f"log_{timestamp[:10]}.txt")

    with open(log_file_path, "a") as log_file:
        log_file.write(log_line + "\n")
    return True


def action_ipfabric(timestamp: str, cvp_webhook: AristaCvpWebhook, settings: Settings):
    print("##DEBUG## action_ipfabric")
    for webhook in cvp_webhook:
        print(f'##DEBUG## {webhook["is_firing"]}')
        if webhook["is_firing"]:
            ipf = IPFClient(base_url=settings.IPF_URL, token=settings.IPF_TOKEN)
            ipf_settings = {
                "snapshotName": "Discovery by CloudVision webhook",
                "notes": webhook.description,
            }
            ipf.post("snapshots", json=ipf_settings)

    return True
