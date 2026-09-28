# -*- coding: utf-8 -*-
#############################################################################
#
#    Cybrosys Technologies Pvt. Ltd.
#
#    Copyright (C) 2026-TODAY Cybrosys Technologies (<https://www.cybrosys.com>).
#    Author: Cybrosys Techno Solutions (<https://www.cybrosys.com>)
#
#    This program is under the terms of the Odoo Proprietary License v1.0
#    (OPL-1). It is forbidden to publish, distribute, sublicense, or sell
#    copies of the Software or modified copies of the Software.
#
#    The above copyright notice and this permission notice must be included in
#    all copies or substantial portions of the Software.
#
#############################################################################

from odoo.exceptions import UserError
from odoo.tests.common import TransactionCase, tagged


@tagged("post_install", "-at_install")
class TestHrHolidayApproval(TransactionCase):

    @classmethod
    def setUpClass(cls):
        super().setUpClass()

        cls.user = cls.env["res.users"].create({
            "name": "Validator",
            "login": "validator@test.com",
            "email": "validator@test.com",
        })

    # ------------------------------------------------------------------
    # hr.leave.type
    # ------------------------------------------------------------------

    def test_leave_type_single_validation(self):
        """Single validation should be created normally."""

        leave_type = self.env["hr.leave.type"].create({
            "name": "Casual Leave",
            "leave_validation_type": "hr",
        })

        self.assertEqual(
            leave_type.leave_validation_type,
            "hr",
        )

    def test_multi_level_without_validator(self):
        """Multi-level approval requires at least one validator."""

        with self.assertRaises(UserError):
            self.env["hr.leave.type"].create({
                "name": "Annual Leave",
                "leave_validation_type": "multi",
            })

    def test_multi_level_with_validator(self):
        """Leave type should be created successfully."""

        leave_type = self.env["hr.leave.type"].create({
            "name": "Annual Leave",
            "leave_validation_type": "multi",
            "leave_validators_ids": [
                (0, 0, {
                    "holiday_validators_id": self.user.id,
                })
            ],
        })

        self.assertEqual(
            leave_type.leave_validation_type,
            "multi",
        )

        self.assertEqual(
            len(leave_type.leave_validators_ids),
            1,
        )

    # ------------------------------------------------------------------
    # hr.leave
    # ------------------------------------------------------------------

    def test_compute_multi_level_flag(self):
        """Computed field should become True for multi approval."""

        leave_type = self.env["hr.leave.type"].create({
            "name": "Medical Leave",
            "leave_validation_type": "multi",
            "leave_validators_ids": [
                (0, 0, {
                    "holiday_validators_id": self.user.id,
                })
            ],
        })

        employee = self.env["hr.employee"].create({
            "name": "Employee One",
        })

        leave = self.env["hr.leave"].new({
            "employee_id": employee.id,
            "holiday_status_id": leave_type.id,
        })

        leave._compute_is_multi_level_validation()

        self.assertTrue(
            leave.is_multi_level_validation
        )

    def test_compute_single_level_flag(self):
        """Computed field should be False."""

        leave_type = self.env["hr.leave.type"].create({
            "name": "Normal Leave",
            "leave_validation_type": "hr",
        })

        employee = self.env["hr.employee"].create({
            "name": "Employee Two",
        })

        leave = self.env["hr.leave"].new({
            "employee_id": employee.id,
            "holiday_status_id": leave_type.id,
        })

        leave._compute_is_multi_level_validation()

        self.assertFalse(
            leave.is_multi_level_validation
        )