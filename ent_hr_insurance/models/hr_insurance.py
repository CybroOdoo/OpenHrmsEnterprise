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
from dateutil.relativedelta import relativedelta
from odoo import api, fields, models


class HRInsurance(models.Model):
    """Manage employee insurance policies and coverage details."""
    _name = 'hr.insurance'
    _description = 'Employee Insurance'
    _rec_name = 'employee_id'

    employee_id = fields.Many2one('hr.employee', string='Employee',
                                  required=True, help="Employee associated with the insurance")
    policy_id = fields.Many2one('insurance.policy', string='Policy',
                                required=True, help="Insurance policy assigned to the employee")
    amount = fields.Float(string='Premium', required=True, help="Policy amount")
    sum_insured = fields.Float(string="Sum Insured", required=True,
                               help="Insured sum")
    policy_coverage = fields.Selection(
        [('monthly', 'Monthly'), ('yearly', 'Yearly')],
        required=True, default='monthly',
        string='Policy Coverage', help="Duration of the policy")
    date_from = fields.Date(string='Date From',
                            default=fields.Date.today, readonly=True,
                            help="Start date")
    date_to = fields.Date(string='Date To', readonly=True, help="End date",
                          default=lambda self: fields.Date.today() + relativedelta(months=1, day=1, days=-1))
    state = fields.Selection([('active', 'Active'),
                              ('expired', 'Expired'), ],
                             default='active', string="State",
                             compute='_compute_state', store=True)
    company_id = fields.Many2one('res.company', string='Company', required=True,
                                 help="Company",
                                 default=lambda self: self.env.user.company_id)

    @api.depends('date_from', 'date_to')
    def _compute_state(self):
        """Return the status of the instance."""
        current_date = fields.Date.today()
        for record in self:
            date_from = record.date_from
            date_to = record.date_to
            if date_from <= current_date <= date_to:
                record.state = 'active'
            else:
                record.state = 'expired'

    @api.onchange('policy_coverage')
    def _onchange_policy_coverage(self):
        """Returns the period"""
        if self.policy_coverage == 'monthly':
            self.date_to = fields.Date.today() + relativedelta(months=1, day=1, days=-1)
        if self.policy_coverage == 'yearly':
            self.date_to = fields.Date.today() + relativedelta(months=12)