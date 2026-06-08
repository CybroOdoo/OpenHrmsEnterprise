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
from odoo.tests import tagged
from odoo.tests.common import TransactionCase


@tagged('post_install', '-at_install')
class TestHrEmployee(TransactionCase):

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.department_1 = cls.env['hr.department'].create({
            'name': 'Development',
        })
        cls.department_2 = cls.env['hr.department'].create({
            'name': 'Testing',
        })
        cls.job_1 = cls.env['hr.job'].create({
            'name': 'Developer',
        })
        cls.job_2 = cls.env['hr.job'].create({
            'name': 'Tester',
        })
        cls.employee = cls.env['hr.employee'].create({
            'name': 'Test Employee',
            'department_id': cls.department_1.id,
            'job_id': cls.job_1.id,
            'hourly_cost': 100,
        })

    def test_department_history_creation(self):
        """Test department history."""
        self.employee.write({
            'department_id': self.department_2.id,
        })
        history = self.env['department.history'].search([
            ('employee_id', '=', self.employee.id),
            ('changed_field', '=', 'Department')
        ], limit=1)
        self.assertTrue(history)
        self.assertEqual(
            history.current_value,
            self.department_2.name
        )

    def test_job_history_creation(self):
        """Test job history."""
        self.employee.write({
            'job_id': self.job_2.id,
        })
        history = self.env['department.history'].search([
            ('employee_id', '=', self.employee.id),
            ('changed_field', '=', 'Job Position')
        ], limit=1)
        self.assertTrue(history)
        self.assertEqual(
            history.current_value,
            self.job_2.name
        )

    def test_hourly_cost_history_creation(self):
        """Test hourly cost history."""
        self.employee.write({
            'hourly_cost': 150,
        })
        history = self.env['timesheet.cost'].search([
            ('employee_id', '=', self.employee.id)
        ], limit=1)
        self.assertTrue(history)
        self.assertEqual(
            float(history.current_value),
            150.0
        )
        