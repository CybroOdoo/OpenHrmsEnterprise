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
from odoo.tests import tagged
from odoo.tests.common import TransactionCase


@tagged('post_install', '-at_install')
class TestHrEmployee(TransactionCase):

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.employee = cls.env['hr.employee'].create({
            'name': 'Demo Employee',
            'work_email': 'employee@test.com',
            'identification_id': 'ID001',
            'passport_id': 'PASS001',
        })

    def test_employee_default_notice_days(self):
        """Test employee default notice days."""
        self.env['ir.config_parameter'].sudo().set_param(
            'ent_hr_employee_updation.notice_period',
            True
        )
        self.env['ir.config_parameter'].sudo().set_param(
            'ent_hr_employee_updation.no_of_days',
            30
        )
        employee = self.env['hr.employee'].create({
            'name': 'Notice Employee',
        })
        self.assertEqual(
            employee.notice_days,
            30
        )

    def test_mail_reminder_id_expiry(self):
        """Test ID expiry reminder mail."""
        self.employee.write({
            'id_expiry_date': (
                fields.Date.today() + timedelta(days=13)
            )
        })
        mail_before = self.env['mail.mail'].search_count([])
        self.env['hr.employee'].mail_reminder()
        mail_after = self.env['mail.mail'].search_count([])
        self.assertEqual(
            mail_after,
            mail_before + 1
        )

    def test_mail_reminder_passport_expiry(self):
        """Test passport expiry reminder mail."""
        self.employee.write({
            'passport_expiry_date': (
                fields.Date.today() + timedelta(days=179)
            )
        })
        mail_before = self.env['mail.mail'].search_count([])
        self.env['hr.employee'].mail_reminder()
        mail_after = self.env['mail.mail'].search_count([])
        self.assertEqual(
            mail_after,
            mail_before + 1
        )

    def test_onchange_spouse(self):
        """Test spouse onchange creates family record."""
        self.employee.spouse_complete_name = 'Jane'
        self.employee.spouse_birthdate = fields.Date.today()
        self.employee._onchange_spouse()
        self.assertTrue(
            self.employee.fam_ids
        )
        family = self.employee.fam_ids[0]
        self.assertEqual(
            family.member_name,
            'Jane'
        )

    def test_employee_family_creation(self):
        """Test employee family creation."""
        relation = self.env['hr.employee.relation'].create({
            'name': 'Father',
        })
        family = self.env['hr.employee.family'].create({
            'employee_id': self.employee.id,
            'relation_id': relation.id,
            'member_name': 'John',
            'member_contact': '9999999999',
        })
        self.assertEqual(
            family.employee_id,
            self.employee
        )
        self.assertEqual(
            family.relation_id,
            relation
        )
        self.assertEqual(
            family.member_name,
            'John'
        )
