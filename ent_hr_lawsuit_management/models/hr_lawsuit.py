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


class HrLawsuit(models.Model):
    """Creates the model hr.lawsuit"""
    _name = 'hr.lawsuit'
    _description = 'Hr Lawsuit Management'
    _inherit = ['mail.thread', 'mail.activity.mixin']

    name = fields.Char(string='Code', help="Code of the record", copy=False)
    ref_no = fields.Char(string="Reference Number",
                         help="Reference number of the record")
    company_id = fields.Many2one('res.company', string='Company',
                                 default=lambda self: self.env.company,
                                 help='Name of the company of the user')
    requested_date = fields.Date(string='Date', copy=False,
                                 help='Start Date')
    hearing_date = fields.Date(string='Hearing Date',
                               help='Upcoming hearing date')
    court_name = fields.Char(string='Court Name', tracking=True,
                             help='Name of the Court')
    judge = fields.Char(string='Judge', tracking=True,
                        help='Name of the Judge')
    lawyer_id = fields.Many2one('res.partner', string='Lawyer',
                                tracking=True,
                                help='Choose the contact of Layer from the '
                                     'contact list')
    first_party_id = fields.Many2one('res.company', string='First Party',
                                     required=True,
                                     default=lambda self: self.env.company,
                                     help='Choose the company as first Party', )
    party2 = fields.Selection([('employee', 'Employee'),
                               ('partner', 'Partner'),
                               ('other', 'Others')], default='employee',
                              string='Second Party', required=True,
                              help='Choose the second party in the legal '
                                   'issue.It can be Employee, Contacts or '
                                   'others.', )
    employee_id = fields.Many2one('hr.employee', string='Employee',
                                  copy=False,
                                  help='Choose the Employee')
    partner_id = fields.Many2one('res.partner', string='Partner',
                                 copy=False,
                                 help='Choose the partner')
    other_name = fields.Char(string='Name', help='Enter the details of other '
                                                 'type')
    party2_name = fields.Char(compute='_compute_party2_name', string='Name',
                              store=True, help="Name of the second party")
    case_details = fields.Html(string='Case Details', copy=False,
                               tracking=True,
                               help='More details of the case')
    state = fields.Selection([('draft', 'Draft'),
                              ('running', 'Running'),
                              ('cancel', 'Cancelled'),
                              ('fail', 'Failed'),
                              ('won', 'Won')], string='Status',
                             default='draft', tracking=True,
                             copy=False,
                             help='Status')

    @api.model_create_multi
    def create(self, vals_list):
        """Create a new sequence"""
        for vals in vals_list:
            vals['name'] = self.env['ir.sequence'].next_by_code('hr.lawsuit')
        return super(HrLawsuit, self).create(vals_list)

    def action_won(self):
        """Set lawsuit state to Won"""
        self.state = 'won'

    def action_cancel(self):
        """Set lawsuit state to Cancel"""
        self.state = 'cancel'

    def action_loss(self):
        """Set lawsuit state to loss"""
        self.state = 'fail'

    def action_process(self):
        """Set lawsuit state to running"""
        self.state = 'running'

    @api.depends('party2', 'employee_id')
    def _compute_party2_name(self):
        """Compute the name of the second party name"""
        for rec in self:
            if rec.party2 == 'employee':
                rec.party2_name = rec.employee_id.name
            else:
                rec.party2_name = False
