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
from odoo.exceptions import ValidationError
from odoo.tests import tagged
from odoo.tests.common import TransactionCase


@tagged('post_install', '-at_install')
class TestHrResignation(TransactionCase):

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.employee = cls.env['hr.employee'].create({
            'name': 'Test Employee',
            'joining_date': fields.Date.today() - timedelta(days=365),
            'notice_days': 30,
        })

    def _create_resignation(self, **vals):
        values = {
            'employee_id': self.employee.id,
            'joined_date': self.employee.joining_date,
            'expected_revealing_date':
                fields.Date.today() + timedelta(days=30),
            'reason': 'Personal Reason',
        }
        values.update(vals)
        return self.env['hr.resignation'].create(values)

    def test_onchange_employee(self):
        """Test employee onchange."""
        resignation = self.env['hr.resignation'].new({
            'employee_id': self.employee.id,
        })
        resignation._onchange_employee_id()
        self.assertEqual(
            resignation.joined_date,
            self.employee.joining_date
        )
        self.assertEqual(
            int(resignation.notice_period),
            self.employee.notice_days
        )

    def test_sequence_generation(self):
        """Test resignation sequence generation."""
        resignation = self._create_resignation()
        self.assertNotEqual(
            resignation.name,
            'New'
        )

    def test_confirm_resignation(self):
        """Test resignation confirmation."""
        resignation = self._create_resignation()
        resignation.action_confirm_resignation()
        self.assertEqual(
            resignation.state,
            'confirm'
        )
        self.assertTrue(
            resignation.resign_confirm_date
        )

    def test_confirm_resignation_without_joining_date(self):
        """Test confirmation without joining date."""
        resignation = self._create_resignation(
            joined_date=False
        )
        with self.assertRaises(ValidationError):
            resignation.action_confirm_resignation()

    def test_confirm_resignation_invalid_date(self):
        """Test last day before joining date."""
        resignation = self._create_resignation(
            joined_date=fields.Date.today(),
            expected_revealing_date=fields.Date.today()
        )
        with self.assertRaises(ValidationError):
            resignation.action_confirm_resignation()

    def test_cancel_resignation(self):
        """Test resignation cancellation."""
        resignation = self._create_resignation()
        resignation.action_cancel_resignation()
        self.assertEqual(
            resignation.state,
            'cancel'
        )

    def test_reject_resignation(self):
        """Test resignation rejection."""
        resignation = self._create_resignation()
        resignation.action_reject_resignation()
        self.assertEqual(
            resignation.state,
            'cancel'
        )

    def test_reset_to_draft(self):
        """Test reset to draft."""
        resignation = self._create_resignation(
            state='cancel'
        )
        self.employee.write({
            'active': False,
            'resigned': True,
        })
        resignation.action_reset_to_draft()
        self.assertEqual(
            resignation.state,
            'draft'
        )
        self.assertTrue(
            self.employee.active
        )
        self.assertFalse(
            self.employee.resigned
        )

    def test_approve_resignation(self):
        """Test resignation approval."""
        resignation = self._create_resignation(
            expected_revealing_date=fields.Date.today()
        )
        resignation.action_confirm_resignation()
        resignation.action_approve_resignation()
        self.assertEqual(
            resignation.state,
            'approved'
        )
        self.assertTrue(
            resignation.approved_revealing_date
        )

    def test_approve_resignation_without_confirmation(self):
        """Test approval without confirmation."""
        resignation = self._create_resignation()
        with self.assertRaises(ValidationError):
            resignation.action_approve_resignation()

    def test_update_employee_status_resigned(self):
        """Test employee status update."""
        resignation = self._create_resignation(
            state='approved',
            expected_revealing_date=fields.Date.today(),
            resignation_type='resigned'
        )
        resignation.update_employee_status()
        self.assertFalse(
            self.employee.active
        )
        self.assertTrue(
            self.employee.resigned
        )

    def test_update_employee_status_fired(self):
        """Test fired employee status update."""
        self.employee.write({
            'active': True,
            'fired': False,
        })
        resignation = self._create_resignation(
            state='approved',
            expected_revealing_date=fields.Date.today(),
            resignation_type='fired'
        )
        resignation.update_employee_status()
        self.assertTrue(
            self.employee.fired
        )