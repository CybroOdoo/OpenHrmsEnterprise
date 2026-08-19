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
from unittest.mock import patch

from odoo.tests import tagged, TransactionCase

from odoo.addons.hr_payroll.models.hr_payslip import HrPayslip as BaseHrPayslip


@tagged("-at_install", "post_install")
class TestHrPayslip(TransactionCase):

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.employee = cls.env["hr.employee"].create({
            "name": "Payslip Employee",
        })
        cls.overtime = cls.env["hr.overtime"].create({
            "employee_id": cls.employee.id,
            "type": "cash",
            "duration_type": "hours",
            "date_from": "2026-01-01 08:00:00",
            "date_to": "2026-01-01 12:00:00",
            "cash_hrs_amount": 125.0,
            "state": "approved",
        })

    def test_action_payslip_done_marks_cash_overtime_paid(self):
        payslip = self.env["hr.payslip"].new({})
        payslip.overtime_ids = self.overtime

        with patch.object(BaseHrPayslip, "action_payslip_done", return_value=True):
            payslip.action_payslip_done()

        self.assertTrue(payslip.overtime_ids.payslip_paid)
