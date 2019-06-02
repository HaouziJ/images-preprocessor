#!/usr/bin/env python
# -*- coding: utf-8 -*-

import pytest
from images_preprocessor.lib.resources.resource_manager import ResourceManager
from configparser import SectionProxy


def test_empty_resources():
    resources: SectionProxy = ResourceManager(env="dev").get_resources(section="ENVIRONMENT")

    assert resources["ENV"] is not None


def test_env_resources():
    dev_resources: SectionProxy = ResourceManager(env="dev").get_resources(section="ENVIRONMENT")
    prod_resources: SectionProxy = ResourceManager(env="prod").get_resources(section="ENVIRONMENT")

    assert dev_resources["ENV"] != prod_resources["ENV"]


