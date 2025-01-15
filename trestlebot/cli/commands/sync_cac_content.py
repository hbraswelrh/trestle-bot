# SPDX-License-Identifier: Apache-2.0
# Copyright (c) 2024 Red Hat, Inc.

"""Module for sync cac content command"""
import logging
from typing import Any, List

import click

from trestlebot.cli.options.common import common_options, git_options, handle_exceptions
from trestlebot.cli.utils import run_bot
from trestlebot.tasks.authored.compdef import AuthoredComponentDefinition
from trestlebot.tasks.authored.profile import AuthoredProfile
from trestlebot.tasks.base_task import TaskBase
from trestlebot.tasks.sync_cac_content_profile_task import SyncCacContentProfileTask

# from trestlebot.tasks.sync_cac_content_profile_task import SyncCacContentProfileTask
from trestlebot.tasks.sync_cac_content_task import SyncCacContentTask


logger = logging.getLogger(__name__)


@click.group(
    name="sync-cac-content-cmd",
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
    type=click.Choice(["service", "validation"]),
    help="Type of component definition. Default: service",
    required=False,
    default="service",
)
@handle_exceptions
def sync_cac_content_cmd(ctx: click.Context, **kwargs: Any) -> None:
    """Transform CaC content to OSCAL component definition."""
    # Steps:
    # 1. Check options, logger errors if any and exit.
    # 2. Initial product component definition with product name
    # 3. Create a new task to run the data transformation.
    # 4. Initialize a Trestlebot object and run the task(s).

    pre_tasks: List[TaskBase] = []

    product = kwargs["product"]
    cac_content_root = kwargs["cac_content_root"]
    component_definition_type = kwargs.get("component_definition_type", "service")
    working_dir = kwargs["repo_path"]

    authored_comp: AuthoredComponentDefinition = AuthoredComponentDefinition(
        trestle_root=working_dir,
    )
    authored_comp.create_update_cac_compdef(
        comp_type=component_definition_type,
        product=product,
        cac_content_root=cac_content_root,
        working_dir=working_dir,
    )

    sync_cac_content_task: SyncCacContentTask = SyncCacContentTask(
        working_dir=working_dir
    )

    pre_tasks.append(sync_cac_content_task)

    run_bot(pre_tasks, kwargs)


@sync_cac_content_cmd.command(
    name="oscal-profile", help="Authoring Oscal Profiles with synced CaC content."
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
    help="Product to build OSCAL Profile for.",
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
    type=List[str],
    required=False,
    help="Optionally produce OSCAL Profiles by filtered baseline level.",
)
@handle_exceptions
def sync_cac_content_profile_cmd(
    ctx: click.Context,
    **kwargs: Any,
) -> None:
    # WIP test
    # The cac_content_root accesses the repository of control files
    # User will input control file name to begin authoring OSCAL Profiles
    # If user indicates level, a profile specific to indicated level will be produced
    # If no level associated with control file, task will create single profile with all controls

    pre_tasks: List[TaskBase] = []

    working_dir = kwargs["repo_path"]
    cac_content_root = kwargs["cac_content_root"]
    product = kwargs["product"]
    oscal_catalog = kwargs["oscal_catalog"]
    policy_id = kwargs["policy_id"]
    filter_by_level = kwargs.get("filter_by_level", list())

    authored_profile: AuthoredProfile = AuthoredProfile(trestle_root=working_dir)

    sync_cac_content_profile_task: SyncCacContentProfileTask = (
        SyncCacContentProfileTask(
            cac_content_root=cac_content_root,
            product=product,
            oscal_catalog=oscal_catalog,
            policy_id=policy_id,
            filter_by_level=filter_by_level,
            authored_profile=authored_profile,
        )
    )
    logger.debug(f"No levels included in control file.")

    pre_tasks.append(sync_cac_content_profile_task)
    run_bot(pre_tasks, kwargs)


if __name__ == "__main__":
    sync_cac_content_profile_cmd()
