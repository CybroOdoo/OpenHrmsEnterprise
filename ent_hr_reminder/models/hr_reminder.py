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
from odoo import models, fields


class HrReminder(models.Model):
    """Creates the model Hr Reminder to create the reminders."""
    _name = 'hr.reminder'
    _description = "HR Reminder"

    name = fields.Char(string='Title', required=True,
                       help="Title of the reminder")
    model_id = fields.Many2one(comodel_name='ir.model', help="Choose the model name",
                               string="Model", required=True,
                               ondelete='cascade',
                               domain="[('model', 'like','hr')]")
    field_id = fields.Many2one(comodel_name='ir.model.fields', string='Field',
                               help="Choose the field",
                               domain="[('model_id', '=',model_id),"
                                      "('ttype', 'in', ['datetime','date'])]"
                               , required=True, ondelete='cascade')
    search_by = fields.Selection([('today', 'Today'),
                                  ('set_period', 'Set Period'),
                                  ('set_date', 'Set Date'), ],
                                 required=True, string="Search By",
                                 help="Search by the given field")
    days_before = fields.Integer(string='Reminder before',
                                 help="Number of days before the reminder "
                                      "should show")
    date_set = fields.Date(string='Select Date',
                           help="Select the reminder set date")
    date_from = fields.Date(string="Start Date",
                            help="Start date to show the reminder")
    date_to = fields.Date(string="End Date",
                          help="End date to not show the reminder")
    expiry_date = fields.Date(string="Reminder Expiry Date",
                              help="Expiry date to expires out the reminder")
    company_id = fields.Many2one(comodel_name='res.company', string='Company',
                                 required=True, help="Company of the record",
                                 default=lambda self: self.env.user.company_id)
