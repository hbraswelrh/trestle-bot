# SPDX-License-Identifier: Apache-2.0
# Copyright (c) 2024 Red Hat, Inc.

"""Module for sync cac content command"""
import logging
import os
import sys
import traceback
from typing import Any, List

import click
import trestle.oscal.catalog as cat
from trestle.common.model_utils import ModelUtils
from trestle.core.models.file_content_type import FileContentType

from trestlebot.cli.options.common import common_options, git_options, handle_exceptions
from trestlebot.cli.utils import run_bot
from trestlebot.const import ERROR_EXIT_CODE
from trestlebot.tasks.authored.profile import AuthoredProfile
from trestlebot.tasks.base_task import TaskBase
from trestlebot.tasks.sync_cac_content_profile_task import SyncCacContentProfileTask
from trestlebot.tasks.sync_cac_content_task import SyncCacContentTask


logger = logging.getLogger(__name__)


@click.command(
    name="sync-cac-content",
    help="Transform CaC content to component definition in OSCAL.",
)
@click.pass_context
@common_options
@git_options
@click.option(
    "--cac-content-root",
    help="Root of the CaC content project.",
    required=True,
)
@click.option(
    "--product",
    type=str,
    help="Product to build OSCAL component definition with",
    required=True,
)
@click.option(
    "--cac-profile",
    type=str,
    help="CaC profile used to collect product data for transformation",
    required=True,
)
@click.option(
    "--oscal-profile",
    type=str,
    help="Main profile href, or name of the profile in trestle workspace",
    required=True,
)
@click.option(
    "--component-definition-type",
    type=click.Choice(["service", "validation", "software"]),
    help="Type of component definition. Default: service",
    required=False,
    default="service",
)
def sync_cac_content_cmd(ctx: click.Context, **kwargs: Any) -> None:
    """Transform CaC content to OSCAL component definition."""

    product = kwargs["product"]
    cac_content_root = kwargs["cac_content_root"]
    component_definition_type = kwargs["component_definition_type"]
    cac_profile = os.path.join(cac_content_root, kwargs["cac_profile"])
    oscal_profile = kwargs["oscal_profile"]
    working_dir = str(kwargs["repo_path"].resolve())

    try:
        pre_tasks: List[TaskBase] = []
        sync_cac_content_task = SyncCacContentTask(
            product,
            cac_profile,
            cac_content_root,
            component_definition_type,
            oscal_profile,
            working_dir,
        )
        pre_tasks.append(sync_cac_content_task)
        results = run_bot(pre_tasks, kwargs)
        logger.debug(f"Trestlebot results: {results}")
    except Exception as e:
        traceback_str = traceback.format_exc()
        logger.error(f"Trestle-bot Error: {str(e)}")
        logger.debug(traceback_str)
        sys.exit(ERROR_EXIT_CODE)


@click.command(
    name="sync-cac-content-profile",
    help="Authoring Oscal Profiles by level with synced CaC content.",
)
@click.pass_context
@common_options
@git_options
@click.option(
    "--cac-content-root",
    required=True,
    help="Root of the CaC content project.",
)
@click.option(
    "--product",
    type=str,
    required=True,
    help="Product name for building OSCAL Profile.",
)
@click.option(
    "--oscal-catalog",
    type=str,
    required=True,
    help="Main catalog href, or name of the catalog in trestle workspace.",
)
@click.option(
    "--policy-id",
    type=str,
    required=True,
    help="Policy id for source control file.",
)
@click.option(
    "--filter-by-level",
    type=str,
    required=False,
    multiple=True,
    help="Optionally produce OSCAL Profiles by filtered baseline level.",
)
@handle_exceptions
def sync_cac_content_profile_cmd(
    ctx: click.Context,
    **kwargs: Any,
) -> None:
    # The cac_content_root accesses the repository of control files.
    # User will input policy_id name to amend name of OSCAL Profile.
    # If the user indicates level, an OSCAL Profile will be produced with criteria specific to that level.
    # If no baseline level associated with policy id, task will create OSCAL Profiles for all levels.
    """
    Sync cac content for authoring OSCAL Profiles.
    """
    pre_tasks: List[TaskBase] = []

    working_dir = kwargs["repo_path"]
    cac_content_root = kwargs["cac_content_root"]
    product = kwargs["product"]
    oscal_catalog = kwargs["oscal_catalog"]
    policy_id = kwargs["policy_id"]
    filter_by_level = kwargs.get("filter_by_level", list())

    # Getting the catalog as a path from user input
    oscal_catalog_path = ModelUtils.get_model_path_for_name_and_class(
        working_dir,
        oscal_catalog,
        cat.Catalog,
        FileContentType.JSON,
    )
    authored_profile: AuthoredProfile = AuthoredProfile(trestle_root=working_dir)

    sync_cac_content_profile_task: SyncCacContentProfileTask = (
        SyncCacContentProfileTask(
            cac_content_root=cac_content_root,
            product=product,
            oscal_catalog=str(oscal_catalog_path),
            policy_id=policy_id,
            filter_by_level=filter_by_level,
            authored_profile=authored_profile,
        )
    )
    logger.debug("The sync cac content profile task is complete.")

    pre_tasks.append(sync_cac_content_profile_task)
    run_bot(pre_tasks, kwargs)
