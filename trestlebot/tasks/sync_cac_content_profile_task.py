# Current work for sync_cac_content_profile
# Task to leverage ComplianceasCode/content ControlsManager
# Interaction with CLI
import logging
import os
from typing import Any, Dict, List

from ssg.controls import ControlsManager
from ssg.products import (
    get_profile_files_from_root,
    load_product_yaml,
    product_yaml_path,
)

from trestlebot import const
from trestlebot.tasks.authored.profile import AuthoredProfile
from trestlebot.tasks.base_task import TaskBase


logger = logging.getLogger(__name__)


class SyncCacContentProfileTask(TaskBase):
    def __init__(
        self,
        cac_content_root: str,
        product: str,
        control_file: str,
        filter_by_level: List[str],
        authored_profile: AuthoredProfile,
    ):
        self.cac_content_root = cac_content_root
        self.product = product
        self.control_file = control_file
        self.filter_by_level = filter_by_level
        self.authored_profile = authored_profile
        working_dir = self._authored_profile.get_trestle_root()
        super().__init__(working_dir=trestle_root, model_filter=None)

    def get_control_ids_by_level(self, control_file: str, filter_by_level: str) -> None:
        """
        Collecting control file product data
        """

        product_yml_path = product_yaml_path(self.cac_content_root, self.product)
        product_data = load_product_yaml(product_yml_path)

        control_manager = ControlsManager(
            os.path.join(self.cac_content_root, "controls"), product_data
        )

        control_manager.load()
        # control_manager is an instance of the ControlsManager() and it is using
        # cac_content_root/controls to evaluate
        # accessing control file within content/controls
        # the instance can use the methods within the ControlsManager() class
        # Use for parsing and organizing by level
        default_levels = control_manager.get_all_controls(control_file)
        extract_policy = control_manager._get_policy(control_file)

        if not filter_by_level:
            all_controls = control_manager.get_all_controls(control_file)
            self.create_oscal_profile(all_controls)
            logger.debug(
                f"No level indicated. Sorting based on {control_file} defaults."
            )
        else:
            for level in filter_by_level:
                eligible_controls = control_manager.get_all_controls_of_level(level)
                self.create_oscal_profile(eligible_controls)
            # make oscal profile
            logger.debug(
                f"Organizing controls based on {filter_by_level}. If no level is specified, all controls will be organized."
            )
            # if filter_by_profile = "high" filter_by_profile.upper()
            # when making new json -> profile-HIGH.json

    def create_oscal_profile(
        self,
        import_path: str,
        controls: List[str],
        name_update: str,
    ):
        # Step 1: If filter by level returns eligible controls, create OSCAL profile with suffix change based on level
        # Step 2: Fill in with control id, loading from eligible controls and all controls
        self.import_path = kwargs["catalog"]
        # catalog is import_path
        self.name_update = name_update
        name_update = f"{self.control_file}-{self.get_control_ids_by_level.level}.json"
        self.authored_profile.create_new_default(controls, name_update)

    def execute(self) -> int:
        # calling to get_control_ids _by_level and checking for valid control file name
        try:
            self.get_control_ids_by_level(
                control_file=self.control_file, filter_by_level=self.filter_by_level
            )
        except KeyError:
            raise f"The control file {self.control_file} does not exist."
        return const.SUCCESS_EXIT_CODE
