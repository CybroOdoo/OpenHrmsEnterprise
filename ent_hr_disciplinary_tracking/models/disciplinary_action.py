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
from odoo import api, fields, models
from odoo.tools import _
from odoo.exceptions import ValidationError


class DisciplinaryAction(models.Model):
    """Create and record disciplinary_actions"""
    _name = 'disciplinary.action'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _description = "Disciplinary Action"

    state = fields.Selection([
        ('draft', 'Draft'),
        ('explain', 'Waiting Explanation'),
        ('submitted', 'Waiting Action'),
        ('action', 'Action Validated'),
        ('cancel', 'Cancelled')], default='draft', tracking=1,
        string="State",
        help="Disciplinary action record states")
    name = fields.Char(string='Reference', required=True, copy=False,
                       readonly=True, help="Name of the action",
                       default=lambda self: _('New'))
    employee_id = fields.Many2one('hr.employee',
                                    string='Employee',
                                    required=True, help="Employee name")
    department_id = fields.Many2one('hr.department',
                                      string='Department', required=True,
                                      help="Department name")
    discipline_reason_id = fields.Many2one('discipline.category',
                                        string='Reason', required=True,
                                        help="Choose a disciplinary reason")
    explanation = fields.Text(string="Explanation by Employee",
                              help='Employee have to give Explanation'
                                   'to manager about the violation '
                                   'of discipline')
    action_id = fields.Many2one('discipline.category',
                             string="Action", help="Choose an action for "
                                                   "this disciplinary action")
    is_readonly = fields.Boolean(compute="get_user", default=True,
                               string="Read-only", help="True is readonly")
    has_warning = fields.Boolean(string="Warning", help="Warning boolean")
    action_details = fields.Text(string="Action Details",
                                 help="Give the details for this action")
    attachment_ids = fields.Many2many('ir.attachment',
                                      string="Attachments",
                                      help="Employee can submit any documents "
                                           "which supports their explanation")
    note = fields.Text(string="Internal Note",help="Internal Notes")
    joined_date = fields.Date(string="Joined Date",
                              help="Employee joining date")

    @api.model_create_multi
    def create(self, vals_list):
        """Super create to add sequence"""
        for vals in vals_list:
            if vals.get('name', _('New')) == _('New'):
                vals['name'] = self.env['ir.sequence'].next_by_code(
                    'disciplinary.action_id') or _('New')
        return super(DisciplinaryAction, self).create(vals_list)

    @api.depends_context('uid')
    def get_user(self):
        """Dynamically Enable is_readonly field"""
        is_manager = self.env.user.has_group('hr.group_hr_manager')
        for rec in self:
            rec.is_readonly = is_manager

    @api.onchange('employee_id')
    def _onchange_employee_id(self):
        """Restrict edit the employee after validating the action"""
        self.department_id = self.employee_id.department_id
        if self.state == 'action':
            raise ValidationError(_('You Can not edit a Validated Action !!'))

    @api.onchange('discipline_reason_id')
    def _onchange_discipline_reason_id(self):
        """Check discipline_reason"""
        if self.state == 'action':
            raise ValidationError(_('You Can not edit a Validated Action !!'))

    def action_assign(self):
        """Proceed button action"""
        for rec in self:
            rec.state = 'explain'

    def action_cancel(self):
        """Cancel button action"""
        for rec in self:
            rec.state = 'cancel'

    def action_set_to_draft(self):
        """Set to draft button action"""
        for rec in self:
            rec.state = 'draft'

    def action_validate(self):
        """Validate button action"""
        for rec in self:
            if not rec.action_id:
                raise ValidationError(_('You have to select an Action !!'))
            if not rec.action_details or rec.action_details == '<p><br></p>':
                raise ValidationError(
                    _('You have to fill up the Action Details in Action '
                      'Information !!'))
            rec.state = 'action'

    def action_submit(self):
        """Restrict to add explanation"""
        for rec in self:
            if not rec.explanation:
                raise ValidationError(_('You must give an explanation !!'))
        self.write({
            'state': 'submitted'
        })