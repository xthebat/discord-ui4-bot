import json
import requests
from dataclasses import dataclass
from typing import Dict

from configs import OK_RESPONSE
from dc import DiscordConfig

DISCORD_API_PREFIX = "https://discordapp.com/api"


@dataclass
class GithubWebhookData:
    request_header: Dict[str, str]
    create_webhook_data: Dict[str, str]

    @classmethod
    def from_json(cls, filepath: str) -> "GithubWebhookData":
        with open(filepath, "rt") as file:
            data = json.loads(file.read())
        return GithubWebhookData(
            request_header=data["requestHeader"],
            create_webhook_data=data["createWebhookData"],
        )


@dataclass
class GithubWebhook:
    token: str
    github_webhook_channel_id: int
    webhook_url: str
    data: GithubWebhookData

    @classmethod
    def from_dc(cls, dc: DiscordConfig, data: GithubWebhookData) -> "GithubWebhook":
        return GithubWebhook(
            token=dc.token,
            github_webhook_channel_id=dc.github_webhook_channel_id,
            webhook_url=f"{DISCORD_API_PREFIX}/channels/{dc.github_webhook_channel_id}/webhooks",
            data=data
        )

    def create_webhook(self):
        if not self.if_webhook_exists():
            r = requests.post(self.webhook_url, headers=self.data.request_header, json=self.data.create_webhook_data)
            if r.status_code != OK_RESPONSE:
                print(f"Couldn't connect to url: {self.webhook_url}")
                return
            content = json.loads(r.content.decode("utf-8"))
            print(f"Github Webhook created\nWebhook ID: {content['id']}\nWebhook Token: {content['token']}")
        else:
            print("Github Webhook found")

    def get_webhook_list(self) -> list:
        r = requests.get(self.webhook_url, headers=self.data.request_header)
        if r.status_code != OK_RESPONSE:
            print(f"Couldn't connect to url: {self.webhook_url}")
            return []
        content = json.loads(r.content.decode("utf-8"))
        return content

    def if_webhook_exists(self) -> bool:
        webhook_lst = self.get_webhook_list()
        for webhook in webhook_lst:
            if webhook["name"] == self.data.create_webhook_data["name"]:
                return True
        return False