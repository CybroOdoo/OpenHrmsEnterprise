# -*- coding: utf-8 -*-
######################################################################################
#
#    A part of Open HRMS Project <https://www.openhrms.com>
#
#    Copyright (C) 2026-TODAY Cybrosys Technologies(<https://www.cybrosys.com>).
#    Author: Cybrosys Techno Solutions (odoo@cybrosys.com)
#
#    This program is under the terms of the Odoo Proprietary License v1.0 (OPL-1)
#    It is forbidden to publish, distribute, sublicense, or sell copies of the Software
#    or modified copies of the Software.
#
#    THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
#    IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
#    FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT.
#    IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM,
#    DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE,
#    ARISING FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER
#    DEALINGS IN THE SOFTWARE.
#
########################################################################################
from datetime import datetime

from odoo.exceptions import UserError, ValidationError
from odoo.tests import tagged, TransactionCase


@tagged("-at_install", "post_install")
class TestHrOvertime(TransactionCase):

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.employee = cls.env["hr.employee"].create({
            "name": "Test Employee",
        })
        cls.department = cls.env["hr.department"].create({
            "name": "Test Department",
        })
        cls.job = cls.env["hr.job"].create({
            "name": "Test Job",
        })
        cls.employee.write({
            "department_id": cls.department.id,
            "job_id": cls.job.id,
        })

    def _create_overtime(self, **values):
        defaults = {
            "employee_id": self.employee.id,
            "type": "cash",
            "duration_type": "hours",
            "date_from": datetime(2026, 1, 1, 8, 0, 0),
            "date_to": datetime(2026, 1, 1, 12, 0, 0),
        }
        defaults.update(values)
        return self.env["hr.overtime"].create(defaults)

    def test_create_assigns_sequence_name(self):
        overtime = self._create_overtime()
        self.assertTrue(overtime.name.startswith("OVT-"))

    def test_compute_days_no_tmp_in_hours(self):
        overtime = self._create_overtime()
        overtime._compute_days_no_tmp()

        self.assertEqual(overtime.days_no_tmp, 4.0)
        self.assertEqual(overtime.days_no, 4.0)

    def test_compute_days_no_tmp_in_days(self):
        overtime = self._create_overtime(duration_type="days")
        overtime._compute_days_no_tmp()

        self.assertEqual(overtime.days_no_tmp, 0.16666666666666666)

    def test_compute_days_no_tmp_raises_for_invalid_range(self):
        with self.assertRaises(ValidationError):
            overtime = self._create_overtime(
                date_from=datetime(2026, 1, 1, 12, 0, 0),
                date_to=datetime(2026, 1, 1, 8, 0, 0),
            )
            overtime._compute_days_no_tmp()

    def test_unlink_raises_when_not_draft(self):
        overtime = self._create_overtime(state="approved")

        with self.assertRaises(UserError):
            overtime.unlink()

    def test_action_submit_changes_state(self):
        overtime = self._create_overtime()

        overtime.action_submit()

        self.assertEqual(overtime.state, "f_approve")

    def test_action_reject_changes_state(self):
        overtime = self._create_overtime()

        overtime.action_reject()

        self.assertEqual(overtime.state, "refused")

    def test_onchange_employee_id_updates_related_fields(self):
        overtime = self.env["hr.overtime"].new({
            "employee_id": self.employee.id,
        })

        overtime._onchange_employee_id()

        self.assertEqual(overtime.department_id, self.department)
        self.assertEqual(overtime.job_id, self.job)
