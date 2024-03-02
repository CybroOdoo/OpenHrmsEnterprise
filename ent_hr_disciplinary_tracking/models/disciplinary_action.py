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
from odoo import fields, models, api, _
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
        ('cancel', 'Cancelled')], default='draft', track_visibility='onchange',
        help="Disciplinary action record states")
    name = fields.Char(string='Reference', required=True, copy=False,
                       readonly=True,
                       default=lambda self: _('New'))
    employee_name = fields.Many2one('hr.employee',
                                    string='Employee',
                                    required=True, help="Employee name")
    department_name = fields.Many2one('hr.department',
                                      string='Department', required=True,
                                      help="Department name")
    discipline_reason = fields.Many2one('discipline.category',
                                        string='Reason', required=True,
                                        help="Choose a disciplinary reason")
    explanation = fields.Text(string="Explanation by Employee",
                              help='Employee have to give Explanation'
                                   'to manager about the violation '
                                   'of discipline')
    action = fields.Many2one('discipline.category',
                             string="Action", help="Choose an action for "
                                                   "this disciplinary action")
    read_only = fields.Boolean(compute="get_user", default=True)
    warning = fields.Boolean(default=False)
    action_details = fields.Text(string="Action Details",
                                 help="Give the details for this action")
    attachment_ids = fields.Many2many('ir.attachment',
                                      string="Attachments",
                                      help="Employee can submit any documents "
                                           "which supports their explanation")
    note = fields.Text(string="Internal Note")
    joined_date = fields.Date(string="Joined Date",
                              help="Employee joining date")

    # assigning the sequence for the record
    @api.model
    def create(self, vals):
        """Super create to add sequence"""
        vals['name'] = self.env['ir.sequence'].next_by_code(
            'disciplinary.action')
        return super(DisciplinaryAction, self).create(vals)

    # Check the user is a manager or employee
    @api.depends('read_only')
    def get_user(self):
        """Dynamically Enable read_only field"""
        if self.env.user.has_group('hr.group_hr_manager'):
            self.read_only = True
        else:
            self.read_only = False

    @api.onchange('employee_name')
    def onchange_employee_name(self):
        """Restrict edit the employee after validating the action"""
        department = self.env['hr.employee'].search(
            [('name', '=', self.employee_name.name)])
        self.department_name = department.department_id.id
        if self.state == 'action':
            raise ValidationError(_('You Can not edit a Validated Action !!'))

    @api.onchange('discipline_reason')
    def onchange_reason(self):
        """Check discipline_reason"""
        if self.state == 'action':
            raise ValidationError(_('You Can not edit a Validated Action !!'))

    def assign_function(self):
        """Proceed button action"""
        for rec in self:
            rec.state = 'explain'

    def cancel_function(self):
        """Cancel button action"""
        for rec in self:
            rec.state = 'cancel'

    def set_to_function(self):
        """Set to draft button action"""
        for rec in self:
            rec.state = 'draft'

    def action_function(self):
        """Validate button action"""
        for rec in self:
            if not rec.action:
                raise ValidationError(_('You have to select an Action !!'))

            if not rec.action_details or rec.action_details == '<p><br></p>':
                raise ValidationError(
                    _('You have to fill up the Action Details in Action '
                      'Information !!'))
            rec.state = 'action'

    def explanation_function(self):
        """Restrict to add explanation"""
        for rec in self:
            if not rec.explanation:
                raise ValidationError(_('You must give an explanation !!'))
        self.write({
            'state': 'submitted'
        })
