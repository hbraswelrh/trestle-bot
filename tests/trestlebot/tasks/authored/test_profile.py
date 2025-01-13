# SPDX-License-Identifier: Apache-2.0
# Copyright (c) 2023 Red Hat, Inc.


"""Test for Trestle Bot Authored Profile."""

import os
import pathlib

from trestle.common.model_utils import ModelUtils
from trestle.core.models.file_content_type import FileContentType
from trestle.oscal.profile import CombinationMethodValidValues, Profile

from tests import testutils
from trestlebot.tasks.authored.profile import AuthoredProfile


test_prof = "simplified_nist_profile"
test_cat = "simplified_nist_catalog"


def test_create_new_default(tmp_trestle_dir: str) -> None:
    """Test creating new default profile"""
    # Prepare the workspace
    trestle_root = pathlib.Path(tmp_trestle_dir)
    _ = testutils.setup_for_catalog(trestle_root, test_cat, "")

    authored_prof = AuthoredProfile(tmp_trestle_dir)

    cat_path = os.path.join("catalogs", test_cat, "catalog.json")

    authored_prof.create_new_default(cat_path, test_prof)

    prof, _ = ModelUtils.load_model_for_class(
        trestle_root, test_prof, Profile, FileContentType.JSON
    )

    assert prof.merge is not None
    assert prof.merge.combine is not None
    assert prof.merge.combine.method is CombinationMethodValidValues.merge

    assert len(prof.imports) == 1
    assert prof.imports[0].include_all is not None
    assert cat_path in prof.imports[0].href

    authored_prof.create_new_default(cat_path, test_prof, ["ac-1", "ac-2"])
    prof, _ = ModelUtils.load_model_for_class(
        trestle_root, test_prof, Profile, FileContentType.JSON
    )
    assert prof.merge is not None
    assert prof.merge.combine is not None
    assert prof.merge.combine.method is CombinationMethodValidValues.merge

    assert len(prof.imports) == 1
    assert prof.imports[0].include_all is None
    assert cat_path in prof.imports[0].href
    assert prof.imports[0].include_controls is not None
    assert len(prof.imports[0].include_controls[0].with_ids) == 2


def test_create_new_default_existing(tmp_trestle_dir: str) -> None:
    """Test updating an existing profile"""
    # Prepare the workspace
    trestle_root = pathlib.Path(tmp_trestle_dir)
    _ = testutils.setup_for_profile(trestle_root, test_prof, "")

    authored_prof = AuthoredProfile(tmp_trestle_dir)

    cat_path = os.path.join("catalogs", test_cat, "catalog.json")

    authored_prof.create_new_default(cat_path, test_prof)

    prof, _ = ModelUtils.load_model_for_class(
        trestle_root, test_prof, Profile, FileContentType.JSON
    )

    assert prof.merge is not None
    assert prof.merge.combine is not None
    assert prof.merge.combine.method is CombinationMethodValidValues.merge

    assert prof.imports is not None
    assert prof.imports[0].include_all is not None
    assert cat_path in prof.imports[0].href


def test_create_or_update(tmp_trestle_dir: str) -> None:
    """Test updating a profile in place."""
    # Prepare the workspace
    trestle_root = pathlib.Path(tmp_trestle_dir)
    _ = testutils.setup_for_profile(trestle_root, test_prof, "")

    authored_prof = AuthoredProfile(tmp_trestle_dir)

    cat_path = os.path.join("catalogs", test_cat, "catalog.json")

    updated = authored_prof.create_or_update(cat_path, test_prof, ["ac-1", "ac-2"])
    assert updated

    prof, _ = ModelUtils.load_model_for_class(
        trestle_root, test_prof, Profile, FileContentType.JSON
    )

    assert prof.imports is not None
    assert prof.imports[0].include_all is None
    assert cat_path in prof.imports[0].href
    assert prof.imports[0].include_controls is not None
    assert len(prof.imports[0].include_controls[0].with_ids) == 2

    updated = authored_prof.create_or_update(cat_path, test_prof, ["ac-1", "ac-2"])
    assert not updated
