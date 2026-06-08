# -*- coding: utf-8 -*-
################################################################################
#
#    A part of OpenHRMS Project <https://www.openhrms.com>
#
#    Copyright (C) 2026-TODAY Cybrosys Technologies(<https://www.cybrosys.com>).
#    Author: Cybrosys Techno Solutions (odoo@cybrosys.com)
#
#    This program is under the terms of the Odoo Proprietary License v1.0
#    (OPL-1)
#    It is forbidden to publish, distribute, sublicense, or sell copies of the
#    Software or modified copies of the Software.
#
#    THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
#    IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
#    FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT.
#    IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM,
#    DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR
#    OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE
#    USE OR OTHER DEALINGS IN THE SOFTWARE.
#
################################################################################
from datetime import timedelta
from odoo import fields
from odoo.tests.common import TransactionCase

class TestHrEmployeeBase(TransactionCase):

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.employee = cls.env['hr.employee'].create({
            'name': 'Test Employee',
        })

    def test_compute_newly_hired_recent_employee(self):
        """Employee joined within 90 days"""
        if 'newly_hired' not in self.employee._fields:
            self.skipTest(
                "newly_hired field unavailable"
            )
        new_hire_field = self.employee._get_new_hire_field()
        self.employee[new_hire_field] = (
            fields.Datetime.now() -
            timedelta(days=10)
        )
        self.employee._compute_newly_hired()
        self.assertTrue(
            self.employee.newly_hired
        )

    def test_compute_newly_hired_old_employee(self):
        """Employee joined before 90 days"""
        if 'newly_hired' not in self.employee._fields:
            self.skipTest(
                "newly_hired field unavailable"
            )
        new_hire_field = self.employee._get_new_hire_field()
        self.employee[new_hire_field] = (
            fields.Datetime.now() -
            timedelta(days=120)
        )
        self.employee._compute_newly_hired()
        self.assertFalse(
            self.employee.newly_hired
        )
