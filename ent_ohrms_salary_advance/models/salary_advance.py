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
import time
from datetime import datetime
from odoo import fields, models, api, _
from odoo import exceptions
from odoo.exceptions import UserError


class SalaryAdvance(models.Model):
    """ Model for managing salary advances. """
    _name = "salary.advance"
    _description = "Salary Advance"
    _inherit = ['mail.thread', 'mail.activity.mixin']

    name = fields.Char(string='Name', readonly=True, help="Name",
                       default=lambda self: 'Adv/')
    employee_id = fields.Many2one(comodel_name='hr.employee', string='Employee',
                                  required=True, help="Employee")
    date = fields.Date(string='Date', required=True,
                       default=lambda self: fields.Date.today(),
                       help="Submit date")
    reason = fields.Text(string='Reason', help="Reason")
    currency_id = fields.Many2one(comodel_name='res.currency', string='Currency'
                                  , required=True, help="Select Currency",
                                  default=lambda
                                      self:self.env.user.company_id.currency_id)
    company_id = fields.Many2one(comodel_name='res.company', string='Company',
                                 required=True, help="Company",
                                 default=lambda self: self.env.user.company_id)
    advance = fields.Float(string='Advance', help="Advance amount",
                           required=True)
    payment_method_id = fields.Many2one(comodel_name='account.journal',
                                        string='Payment Method',
                                        help="Payment method")
    exceed_condition = fields.Boolean(string='Exceed than Maximum',
                                      help="The Advance is greater than the "
                                           "maximum percentage in salary "
                                           "structure")
    department_id = fields.Many2one(comodel_name='hr.department',
                                 string='Department', help="Choose Department.")
    state = fields.Selection([('draft', 'Draft'),
                              ('submit', 'Submitted'),
                              ('waiting_approval', 'Waiting Approval'),
                              ('approve', 'Approved'),
                              ('cancel', 'Cancelled'),
                              ('reject', 'Rejected')], string='Status',
                             default='draft')
    debit_id = fields.Many2one(comodel_name='account.account',
                               string='Debit Account', help="Debit account")
    credit_id = fields.Many2one(comodel_name='account.account',
                                string='Credit Account', help="Credit account")
    journal_id = fields.Many2one(comodel_name='account.journal',
                                 string='Journal', help="Journal")
    employee_contract_id = fields.Many2one(comodel_name='hr.contract',
                                           string='Contract', help="Employee's "
                                                                   "contract")

    @api.onchange('employee_id')
    def onchange_employee_id(self):
        """ Setting domain for department. """
        department_id = self.employee_id.department_id.id
        domain = [('employee_id', '=', self.employee_id.id)]
        return {'value': {'department_id': department_id}, 'domain': {
            'employee_contract_id': domain,
        }}

    @api.onchange('company_id')
    def onchange_company_id(self):
        """ Setting domain for the journal. """
        company = self.company_id
        domain = [('company_id.id', '=', company.id)]
        result = {
            'domain': {
                'journal_id': domain,
            },
        }
        return result

    def submit_to_manager(self):
        """ Submit action for the advance salary request. """
        self.state = 'submit'

    def cancel(self):
        """ Cancel action for the advance salary request. """
        self.state = 'cancel'

    def reject(self):
        """ Reject action for the advance salary request. """
        self.state = 'reject'

    @api.model
    def create(self, vals):
        """ inheriting create method for adding sequence for the request. """
        vals['name'] = self.env['ir.sequence'].get('salary.advance.seq') or ' '
        res_id = super(SalaryAdvance, self).create(vals)
        return res_id

    def approve_request(self):
        """ This Approves the employee salary advance request. """
        emp_obj = self.env['hr.employee']
        address = emp_obj.browse([self.employee_id.id]).address_id
        if not address.id:
            raise UserError(
                'Define address for the employee. i.e address under work '
                'information of the employee.')
        salary_advance_search = self.search(
            [('employee_id', '=', self.employee_id.id), ('id', '!=', self.id),
             ('state', '=', 'approve')])
        current_month = datetime.strptime(str(self.date),
                                          '%Y-%m-%d').date().month
        for each_advance in salary_advance_search:
            existing_month = datetime.strptime(str(each_advance.date),
                                               '%Y-%m-%d').date().month
            if current_month == existing_month:
                raise UserError('Advance can be requested once in a month')
        if not self.employee_contract_id:
            raise UserError('Define a contract for the employee')
        struct_id = (self.employee_contract_id.structure_type_id.
                     default_struct_id)
        adv = self.advance
        amt = self.employee_contract_id.wage
        if adv > amt and not self.exceed_condition:
            raise UserError('Advance amount is greater than allotted')
        payslip_obj = self.env['hr.payslip'].search(
            [('employee_id', '=', self.employee_id.id),
             ('state', '=', 'done'), ('date_from', '<=', self.date),
             ('date_to', '>=', self.date)])
        if payslip_obj:
            raise UserError("This month salary already calculated")
        for slip in self.env['hr.payslip'].search(
                [('employee_id', '=', self.employee_id.id)]):
            slip_moth = datetime.strptime(str(slip.date_from),
                                          '%Y-%m-%d').date().month
            if current_month == slip_moth + 1:
                slip_day = datetime.strptime(str(slip.date_from),
                                             '%Y-%m-%d').date().day
                current_day = datetime.strptime(str(self.date),
                                                '%Y-%m-%d').date().day
                if current_day - slip_day < struct_id.advance_date:
                    raise exceptions.Warning(
                        _('Request can be done after "%s" Days From '
                          'prevoius month salary') % struct_id.advance_date)
        self.state = 'waiting_approval'

    def approve_request_acc_dept(self):
        """ This Approves the employee salary advance request from
        accounting department. """
        salary_advance_search = self.search(
            [('employee_id', '=', self.employee_id.id), ('id', '!=', self.id),
             ('state', '=', 'approve')])
        current_month = datetime.strptime(str(self.date),
                                          '%Y-%m-%d').date().month
        for each_advance in salary_advance_search:
            existing_month = datetime.strptime(str(each_advance.date),
                                               '%Y-%m-%d').date().month
            if current_month == existing_month:
                raise UserError('Advance can be requested once in a month')
        if not self.debit_id or not self.credit_id or not self.journal_id:
            raise UserError(
                "You must enter Debit & Credit account and journal to approve ")
        if not self.advance:
            raise UserError('You must Enter the Salary Advance amount')
        timenow = time.strftime('%Y-%m-%d')
        for request in self:
            amount = request.advance
            request_name = request.employee_id.name
            reference = request.name
            journal_id = request.journal_id.id
            debit_account_id = request.debit_id.id
            credit_account_id = request.credit_id.id
            debit_line = {
                'name': request_name,
                'account_id': debit_account_id,
                'journal_id': journal_id,
                'date': timenow,
                'debit': amount > 0.0 and amount or 0.0,
                'credit': amount < 0.0 and -amount or 0.0,
            }
            credit_line = {
                'name': request_name,
                'account_id': credit_account_id,
                'journal_id': journal_id,
                'date': timenow,
                'debit': amount < 0.0 and -amount or 0.0,
                'credit': amount > 0.0 and amount or 0.0,
            }
            vals = {
                'name': 'Salary Advance Of ' + ' ' + request_name,
                'narration': request_name,
                'ref': reference,
                'journal_id': journal_id,
                'date': timenow,
                'line_ids': [(0, 0, debit_line), (0, 0, credit_line)]
            }
            move = self.env['account.move'].create(vals)
            move.action_post()
        self.write({'state': 'approve'})
        return True
