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
from odoo.exceptions import UserError


class GratuityConfiguration(models.Model):
    """ Model for gratuity duration configuration details """
    _name = 'gratuity.configuration'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _description = "Gratuity Configuration"
    _rec_name = "name"

    gratuity_accounting_configuration_id = fields.Many2one(
        'hr.gratuity.accounting.configuration',
        help="Hr_gratuity relation")
    name = fields.Char(string="Name", required=True, help="Add gratuity name")
    active = fields.Boolean(default=True, help="Active the record")
    from_year = fields.Float(string="From Year", help="Starting date")
    to_year = fields.Float(string="To Year", help="End date")
    yr_from_flag = fields.Boolean(compute="_compute_yr_field_required",
                                  store=True, help="Ensure the from date")
    yr_to_flag = fields.Boolean(compute="_compute_yr_field_required",
                                store=True, help="Ensure the end date")
    company_id = fields.Many2one('res.company', 'Company',
                                 required=True, help="Company",
                                 index=True,
                                 default=lambda self: self.env.company)
    employee_daily_wage_days = fields.Integer(default=30, help="Total number "
                                                               "of employee "
                                                               "wage days")
    employee_working_days = fields.Integer(string='Working Days', default=21,
                                           help='Number of working days per '
                                                'month')
    percentage = fields.Float(default=1, help="Gratuity payment percentage")

    @api.onchange('from_year', 'to_year')
    def onchange_year(self):
        """ Function to check year configuration """
        if self.from_year and self.to_year:
            if not self.from_year < self.to_year:
                raise UserError(_("Invalid year configuration!"))

    @api.depends('from_year', 'to_year')
    def _compute_yr_field_required(self):
        """ Compute year from and to required """
        for rec in self:
            rec.yr_from_flag = True if not rec.to_year else False
            rec.yr_to_flag = True if not rec.from_year else False
