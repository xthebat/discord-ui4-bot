from dataclasses import dataclass, field
from datetime import datetime
from typing import List
from dataclasses_json import dataclass_json

from misc.functions import read_json


@dataclass_json
@dataclass
class ConfigBase(object):

    @classmethod
    def load(cls, filepath: str) -> "ConfigBase":
        data = read_json(filepath)
        return cls.from_dict(data)


@dataclass
class DiscordConfig(ConfigBase):
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

    daily_task_time: datetime = field(metadata=dict(
        dataclasses_json=dict(decoder=lambda it: datetime.strptime(it, "%H:%M:%S"))
    ))


@dataclass
class GithubConfig(ConfigBase):
    token: str
    nickname: str

    webhook_events: list
