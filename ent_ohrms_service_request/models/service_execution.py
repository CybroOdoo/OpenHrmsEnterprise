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
from odoo import fields, models


class ServiceExecution(models.Model):
    """Model to create records for executing the service"""
    _name = 'service.execution'
    _rec_name = 'issue'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _description = 'issue'

    client_id = fields.Many2one('hr.employee',
                                string="Client", help="Client")
    executer_id = fields.Many2one('hr.employee',
                                  string='Executer', help="Executer")
    issue = fields.Char(string="Issue", help="Issue")
    execute_date = fields.Datetime(string="Date Of Reporting",
                                   help="Date of reporting")
    state_execute = fields.Selection(
        [('draft', 'Draft'), ('requested', 'Requested'),
         ('assign', 'Assigned'), ('check', 'Checked'), ('reject', 'Rejected'),
         ('approved', 'Approved')], tracking=True, )
    test_id = fields.Many2one('service.request', string='test',
                              help="Test")
    notes = fields.Text(string="Internal notes", help="Internal Notes")
    executer_product = fields.Char(string='Service Item', help="service item")
    type_service = fields.Char(string='Service Type', help="Service type")

    def action_service_check(self):
        """Button Checked"""
        self.test_id.sudo().state = 'check'
        self.write({
            'state_execute': 'check'
        })
        return
