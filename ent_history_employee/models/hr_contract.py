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
from datetime import datetime
from odoo import api, fields, models


class HrContract(models.Model):
    """ Class for inheriting hr contract"""
    _inherit = 'hr.contract'

    @api.onchange('wage')
    def onchange_wage(self):
        """ Function for create salary history when wage changes"""
        vals = {
            'employee_id': self.employee_id.id,
            'employee_name': self.employee_id,
            'updated_date': fields.Datetime.today(),
            'current_value': self.wage,
        }
        self.env['salary.history'].sudo().create(vals)

    @api.onchange('name')
    def onchange_name(self):
        """ Function for crete contract history when contract name changes"""
        vals = {
            'employee_id': self.employee_id.id,
            'employee_name': self.employee_id,
            'updated_date': fields.Datetime.today(),
            'changed_field': 'Contract Reference',
            'current_value': self.name,
        }
        self.env['contract.history'].create(vals)

    @api.onchange('date_start')
    def onchange_datestart(self):
        """Function for create contract history when contract start date
        changes"""
        vals = {
            'employee_id': self.employee_id.id,
            'employee_name': self.employee_id,
            'updated_date': fields.Datetime.today(),
            'changed_field': 'Start Date',
            'current_value': self.date_start,
        }
        self.env['contract.history'].create(vals)

    @api.onchange('date_end')
    def onchange_dateend(self):
        """ Function for create contract history when contract end date
        changes"""
        vals = {
            'employee_id': self.employee_id.id,
            'employee_name': self.employee_id,
            'updated_date': fields.Datetime.today(),
            'changed_field': 'End Date',
            'current_value': self.date_end,
        }
        self.env['contract.history'].create(vals)
