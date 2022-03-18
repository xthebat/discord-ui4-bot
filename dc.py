import json
from dataclasses import dataclass
from datetime import datetime
from typing import List
from configs import TZ_INFO


@dataclass
class DiscordConfig(object):
    token: str
    server_id: int

    command_prefix: str

    bot_command_roles_id: List[int]

    root_role_id: int
    undefined_role_id: int
    everyone_role_id: int

    privileged_roles_id: List[int]

    dont_check_name_role_id: int

    warnings_channel_id: int
    questions_channel_id: int
    rules_channel_id: int

    daily_task_time: datetime

    @classmethod
    def from_json(cls, filepath: str) -> "DiscordConfig":
        with open(filepath, "rt") as file:
            data = json.loads(file.read())
        data["daily_task_time"] = datetime.strptime(data["daily_task_time"], "%H:%M:%S")
        return DiscordConfig(**data)
