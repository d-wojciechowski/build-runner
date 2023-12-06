from typing import Optional

from pydantic import BaseModel


class Suite(BaseModel):
    restart: bool
    build: dict
    custom: Optional[list]


class OOTBCommands(BaseModel):
    restart: str


class Commands(BaseModel):
    ootb: OOTBCommands
    custom: dict


class Input(BaseModel):
    build_order: str
    module_registry: str


class AppConfig(BaseModel):
    profile: str
    root: str
    fail_on_error: bool
    commands: Commands
    input: Input
    aliases: dict
    suites: dict
