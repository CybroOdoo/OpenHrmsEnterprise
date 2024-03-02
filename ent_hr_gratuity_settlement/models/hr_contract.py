# -*- coding: utf-8 -*-
######################################################################################
#
#    A part of Open HRMS Project <https://www.openhrms.com>
#
#    Copyright (C) 2024-TODAY Cybrosys Technologies(<https://www.cybrosys.com>).
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
from odoo import models, fields, api, _
from odoo.exceptions import UserError


class Probation(models.Model):
    """hr_contract record"""
    _inherit = 'hr.contract'

    training_info = fields.Text(string='Probationary Info',
                                help="Explain the training information")
    waiting_for_approval = fields.Boolean(string="Waiting For Approval",
                                          help="Ensure the record state")
    is_approve = fields.Boolean(string="Is Approve",
                                help="Ensure the approval")
    state = fields.Selection(
        selection=[
            ('draft', 'New'),
            ('probation', 'Probation'),
            ('open', 'Running'),
            ('close', 'Expired'),
            ('cancel', 'Cancelled'),
        ],string='Status', help="Ensure the record state"
    )
    probation_id = fields.Many2one('hr.training',
                                   string="Probation",
                                   help="Choose training info")
    half_leave_ids = fields.Many2many('hr.leave',
                                      string="Half Leave", help="Add time-off")
    training_amount = fields.Float(string='Training Amount',
                                   help="amount for the employee during "
                                        "training")

    @api.onchange('trial_date_end')
    def state_probation(self):
        """
        function used for changing state draft to probation
        when the end of trail date setting
        """
        if self.trial_date_end:
            self.state = 'probation'

    @api.onchange('employee_id')
    def change_employee_id(self):
        """
        function for changing employee id of hr.training if changed
        """
        if self.probation_id and self.employee_id:
            self.probation_id.employee_id = self.employee_id.id

    def action_approve(self):
        """
        function used for changing the state probation into
        running when approves a contract
        """
        self.write({'is_approve': True})
        if self.state == 'probation':
            self.write({'state': 'open',
                        'is_approve': False})

    @api.model
    def create(self, vals_list):
        """
        function for create a record based on probation
        details in a model

        """
        if vals_list['trial_date_end'] and vals_list['state'] == 'probation':
            dtl = self.env['hr.training'].create({
                'employee_id': vals_list['employee_id'],
                'start_date': vals_list['date_start'],
                'end_date': vals_list['trial_date_end'],
            })
            vals_list['probation_id'] = dtl.id
        res = super(Probation, self).create(vals_list)
        return res

    def write(self, vals):
        """
        function for checking stage changing and creating probation
        record based on contract stage

        """
        if self.state == 'probation':
            if vals.get('state') == 'open' and not self.is_approve:
                raise UserError(_("You cannot change the "
                                  "status of non-approved Contracts"))
            if (vals.get('state') == 'cancel' or vals.get('state') == 'close' or
                    vals.get('state') == 'draft'):
                raise UserError(_("You cannot change the status of non-approved"
                                  " Contracts"))
        training_dtl = self.env['hr.training'].search([('employee_id', '=',
                                                        self.employee_id.id)])
        if training_dtl:
            return super(Probation, self).write(vals)
        if not training_dtl:
            if self.trial_date_end and self.state == 'probation':
                self.env['hr.training'].create({
                    'employee_id': self.employee_id.id,
                    'start_date': self.date_start,
                    'end_date': self.trial_date_end,
                })
        return super(Probation, self).write(vals)
