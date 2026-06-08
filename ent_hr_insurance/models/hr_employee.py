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
from odoo import api, fields, models
from odoo.exceptions import ValidationError


class HREmployee(models.Model):
    """Extends hr.employee model to add the custom fields and methods"""
    _inherit = 'hr.employee'

    insurance_percentage = fields.Float(
        string="Company Percentage",
        help="Company insurance percentage")
    # store=True ensures the computed value is persisted in the DB so that
    # salary rules (amount_python_compute) can reliably read it without
    # depending on hr.payslip's get_inputs() hook (removed in Odoo 19).
    deduced_amount_per_month = fields.Float(
        string="Salary Deducted per Month",
        compute="_compute_deduced_amount",
        store=True,
        help="Amount deducted from the salary per month for insurance")
    deduced_amount_per_year = fields.Float(
        string="Salary Deducted per Year",
        compute="_compute_deduced_amount",
        store=True,
        help="Amount deducted from the salary per year for insurance")
    insurance_ids = fields.One2many(
        'hr.insurance', 'employee_id',
        string="Insurance",
        help="Active insurance policies for this employee",
        domain=[('state', '=', 'active')])

    @api.depends('insurance_ids', 'insurance_ids.amount',
                 'insurance_ids.policy_coverage', 'insurance_ids.date_from',
                 'insurance_ids.date_to', 'insurance_percentage')
    def _compute_deduced_amount(self):
        """Compute the monthly and yearly insurance deduction for the employee.

        The result is stored so that payroll salary rules can access
        employee.deduced_amount_per_month directly via amount_python_compute
        without relying on hr.payslip.get_inputs() which is not available
        in Odoo 19.
        """
        current_date = fields.Date.today()
        for emp in self:
            total_ins_amount = 0.0
            for ins in emp.insurance_ids:
                if ins.date_from and ins.date_to:
                    if ins.date_from <= current_date <= ins.date_to:
                        if ins.policy_coverage == 'monthly':
                            total_ins_amount += ins.amount * 12
                        else:
                            total_ins_amount += ins.amount
            deduced_per_year = total_ins_amount - (
                total_ins_amount * emp.insurance_percentage / 100)
            emp.deduced_amount_per_year = deduced_per_year
            emp.deduced_amount_per_month = deduced_per_year / 12

    @api.constrains('insurance_percentage')
    def _check_percentage(self):
        for rec in self:
            if rec.insurance_percentage < 0 or rec.insurance_percentage > 100:
                raise ValidationError("Percentage must be between 0 and 100")
