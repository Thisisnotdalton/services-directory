from importlib.resources import files
from pathlib import Path
from functools import cached_property, lru_cache
from pydantic import Field, BaseModel
from pydantic_settings import BaseSettings, SettingsConfigDict


class Service(BaseModel):
    name: str
    url: str
    description: str
    groups: list[str]


class ServiceOptions(BaseModel):
    services: dict[str, Service]


class Settings(BaseSettings):
    app_name: str = Field('Services', description='Name of the application.')
    root_path: str = Field('', description='Root path url for the application.')
    config_path: str = Field('', description='Path to JSON file containing the service options.')
    redirect_slashes: bool = Field(True,
                                   description='Whether the application should redirect requests with trailing slashes to the same URL without the trailing slash.')
    case_insensitive: bool = Field(True,
                                   description='Whether the application should be case-insensitive with service ids.')
    static_path: str = Field('static', description='Path for static files.')
    templates_path: str = Field('templates', description='Path for templates files.')
    model_config = SettingsConfigDict(env_prefix='SERVICES_')

    @cached_property
    def services(self) -> dict[str, Service]:
        if not Path(self.config_path).is_file():
            services = ServiceOptions(services={
                'default': Service(name='Default', url='https://example.com', description='Default service',
                                   groups=['default']),
                'example': Service(name='Example', url='https://admin.example.com', description='Example service',
                                   groups=['admin']),
            }).services
        else:
            services = ServiceOptions.model_validate_json(Path(self.config_path).read_text()).services
        if self.case_insensitive:
            services = {k.lower(): v for k, v in services.items()}
        return services

    @cached_property
    def absolute_static_path(self) -> Path:
        if self.static_path.startswith('/'):
            return Path(self.static_path)
        return Path(str(files("app") / self.static_path))

    @cached_property
    def absolute_templates_path(self) -> Path:
        if self.templates_path.startswith('/'):
            return Path(self.templates_path)
        return Path(str(files("app") / self.templates_path))


@lru_cache
def get_settings() -> Settings:
    return Settings()
