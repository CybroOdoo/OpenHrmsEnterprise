# -*- coding: utf-8 -*-
################################################################################
#
#    A part of OpenHRMS Project <https://www.openhrms.com>
#
#    Copyright (C) 2024-TODAY Cybrosys Technologies(<https://www.cybrosys.com>).
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
from odoo import fields, models


class HrEmployee(models.Model):
    """ Inheriting hr employee for computing number of loans for employees """
    _inherit = "hr.employee"

    def _compute_loan_count(self):
        """ Compute the number of loans associated with the employee. """
        for record in self:
            record.loan_count = self.env['hr.loan'].search_count(
                [('employee_id', '=', self.id)])

    loan_count = fields.Integer(string="Loan Count", help="Count of Loans.",
                                compute='_compute_loan_count')

    def action_loans(self):
        """ Get the list of loans associated with the current employee.
           This method returns an action that opens a window displaying a tree
           view and form view of loans related to the employee. """
        self.ensure_one()
        return {
            'type': 'ir.actions.act_window',
            'name': 'Loans',
            'view_mode': 'tree,form',
            'res_model': 'hr.loan',
            'domain': [('employee_id', '=', self.id)],
            'context': "{'create': False}"
        }
