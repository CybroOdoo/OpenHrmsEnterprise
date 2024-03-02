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
from odoo import api, fields, models, _
from odoo.exceptions import UserError


class HrEmployee(models.Model):
    """Class for inheriting hr employee"""
    _inherit = 'hr.employee'

    @api.onchange('department_id')
    def _onchange_department(self):
        """ Function for creating department history when department changes"""
        vals = {
            'employee_id': self._origin.id,
            'employee_name': self._origin.name,
            'updated_date': fields.Datetime.now(),
            'changed_field': 'Department',
            'current_value': self.department_id.name
        }
        self.env['department.history'].sudo().create(vals)

    @api.onchange('job_id')
    def onchange_job_id(self):
        """ Function for creating department history when job changes"""
        vals = {
            'employee_id': self._origin.id,
            'employee_name': self._origin.name,
            'updated_date': fields.Datetime.today(),
            'changed_field': 'Job Position',
            'current_value': self.job_id.name
        }
        self.env['department.history'].sudo().create(vals)

    @api.onchange('hourly_cost')
    def _onchange_timesheet_cost(self):
        """ Function for creating timesheet cost when hourly cost changes"""
        vals = {
            'employee_id': self._origin.id,
            'employee_name': self._origin.name,
            'updated_date': fields.Datetime.now(),
            'current_value': self.hourly_cost
        }
        self.env['timesheet.cost'].sudo().create(vals)

    def department_details(self):
        """ Function for show department details"""
        res_user = self.env['res.users'].browse(self._uid)
        if res_user.has_group('hr.group_hr_manager'):
            return {
                'name': _("Job/Department History"),
                'view_mode': 'tree',
                'res_model': 'department.history',
                'type': 'ir.actions.act_window',
                'target': 'new',
                'domain': [('employee_id', '=', self.id)],
            }
        elif self.id == self.env.user.employee_id.id:
            return {
                'name': _("Job/Department History"),
                'view_mode': 'tree',
                'res_model': 'department.history',
                'type': 'ir.actions.act_window',
                'target': 'new',
            }
        else:
            raise UserError('You cannot access this field!!!!')

    def time_sheet(self):
        """ Function to show timesheet history"""
        res_user = self.env['res.users'].browse(self._uid)
        if res_user.has_group('hr.group_hr_manager'):
            return {
                'name': _("Timesheet Cost Details"),
                'view_mode': 'tree',
                'res_model': 'timesheet.cost',
                'type': 'ir.actions.act_window',
                'target': 'new',
                'domain': [('employee_id', '=', self.id)]
            }
        elif self.id == self.env.user.employee_id.id:
            return {
                'name': _("Timesheet Cost Details"),
                'view_mode': 'tree',
                'res_model': 'timesheet.cost',
                'type': 'ir.actions.act_window',
                'target': 'new'
            }
        else:
            raise UserError('You cannot access this field!!!!')

    def salary_history(self):
        """ Function to show salary history"""
        res_user = self.env['res.users'].browse(self._uid)
        if res_user.has_group('hr.group_hr_manager'):
            return {
                'name': _("Salary History"),
                'view_mode': 'tree',
                'res_model': 'salary.history',
                'type': 'ir.actions.act_window',
                'target': 'new',
                'domain': [('employee_id', '=', self.id)]
            }
        elif self.id == self.env.user.employee_id.id:
            return {
                'name': _("Salary History"),
                'view_mode': 'tree',
                'res_model': 'salary.history',
                'type': 'ir.actions.act_window',
                'target': 'new'
            }
        else:
            raise UserError('You cannot access this field!!!!')

    def contract_history(self):
        """Function to show contract history"""
        res_user = self.env['res.users'].browse(self._uid)
        if res_user.has_group('hr.group_hr_manager'):
            return {
                'name': _("Contract History"),
                'view_mode': 'tree',
                'res_model': 'contract.history',
                'type': 'ir.actions.act_window',
                'target': 'new',
                'domain': [('employee_id', '=', self.id)]
            }
        if self.id == self.env.user.employee_id.id:
            return {
                'name': _("Contract History"),
                'view_mode': 'tree',
                'res_model': 'contract.history',
                'type': 'ir.actions.act_window',
                'target': 'new'
            }
        else:
            raise UserError('You cannot access this field!!!!')
