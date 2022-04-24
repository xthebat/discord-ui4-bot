from dataclasses import dataclass
from typing import Optional

from config import DiscordConfig, GithubConfig
from misc.api_requests import DiscordRequests, GithubRequests


@dataclass
class GithubWebhook:
    discord_req: DiscordRequests
    github_req: GithubRequests

    @classmethod
    def from_data(cls, dc_data: DiscordConfig, g_data: GithubConfig) -> "GithubWebhook":
        return GithubWebhook(
            discord_req=DiscordRequests.from_data(dc_data),
            github_req=GithubRequests.from_data(g_data),
        )

    def create(self, webhook_name: str, channel_id: int, repo_name: str, thread_id: Optional[int] = None) -> bool:
        if self.check_if_exists(webhook_name, channel_id):
            print(f"Couldn't create webhook in Discord! Github Webhook with name {webhook_name} found")
            return False
        if not self.check_if_repo_exists(repo_name):
            print(f"Couldn't find repo with name: {repo_name}")
            return False
        if not self.discord_req.create_webhook(channel_id, webhook_name):
            return False
        webhook = self.discord_req.get_webhook_by_name(channel_id, webhook_name)
        if not self.github_req.create_webhook(webhook["id"], webhook["token"], repo_name, thread_id):
            return False
        return True

    def check_if_exists(self, webhook_name: str, channel_id: int) -> bool:
        webhook_lst = self.discord_req.get_webhook_list(channel_id)
        if webhook_lst is None:
            return True
        for webhook in webhook_lst:
            if webhook["name"] == webhook_name:
                return True
        return False

    def check_if_repo_exists(self, repo_name: str):
        repo_lst = self.github_req.get_repos_list()
        if repo_lst is None:
            return False
        for repo in repo_lst:
            if repo["name"] == repo_name:
                return True
        return False
