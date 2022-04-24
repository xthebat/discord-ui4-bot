import json
import requests
from dataclasses import dataclass
from typing import Any, Optional

DISCORD_API_PREFIX = "https://discordapp.com/api"
GITHUB_API_PREFIX = "https://api.github.com"


@dataclass
class Requests:
    data: Any
    fail_message = "Couldn't connect to url: {}"

    @classmethod
    def from_data(cls, data: Any) -> "Requests":
        return cls(data)

    def is_ok(self, request: requests.models.Response) -> bool:
        if not request.ok:
            print(self.fail_message.format(request.url))
            return False
        return True


@dataclass
class DiscordRequests(Requests):
    headers = {
        "Content-Type": "application/json",
        "Authorization": "Bot {}",
    }

    def create_webhook(self, channel_id: int, webhook_name: str) -> bool:
        url = f"{DISCORD_API_PREFIX}/channels/{channel_id}/webhooks"
        self.headers["Authorization"] = self.headers["Authorization"].format(self.data.token)
        data = {
            "name": webhook_name,
        }
        r = requests.post(url, headers=self.headers, json=data)
        return self.is_ok(r)

    def get_webhook_list(self, channel_id: int):
        url = f"{DISCORD_API_PREFIX}/channels/{channel_id}/webhooks"
        self.headers["Authorization"] = self.headers["Authorization"].format(self.data.token)
        r = requests.get(url, headers=self.headers)
        if self.is_ok(r):
            return json.loads(r.content.decode("utf-8"))
        return None

    def get_webhook_by_name(self, channel_id: int, webhook_name: str):
        webhook_lst = self.get_webhook_list(channel_id)
        for webhook in webhook_lst:
            if webhook["name"] == webhook_name:
                return webhook


@dataclass
class GithubRequests(Requests):

    def create_webhook(
            self,
            webhook_id: int,
            webhook_token: str,
            repo_name: str,
            thread_id: Optional[int] = None,
    ) -> bool:
        url = f"{GITHUB_API_PREFIX}/repos/{self.data.nickname}/{repo_name}/hooks"
        body = {
            "config": {
                "url": f"{DISCORD_API_PREFIX}/webhooks/{webhook_id}/{webhook_token}/github" +
                       (f"?thread_id={thread_id}" if thread_id else ""),
                "content_type": "json"
            },
            "events": self.data.events,
        }
        r = requests.post(url, auth=(self.data.nickname, self.data.token), json=body)
        return self.is_ok(r)

    def get_repos_list(self):
        url = f"{GITHUB_API_PREFIX}/user/repos"
        r = requests.get(url, auth=(self.data.nickname, self.data.token))
        if self.is_ok(r):
            return json.loads(r.content.decode("utf-8"))
        return None
