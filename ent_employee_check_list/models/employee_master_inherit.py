# -*- coding: utf-8 -*-
######################################################################################
#
#    A part of Open HRMS Project <https://www.openhrms.com>
#
#    Copyright (C) 2022-TODAY Cybrosys Technologies(<https://www.cybrosys.com>).
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

from odoo import models, fields, api


class EmployeeMasterInherit(models.Model):
    _inherit = 'hr.employee'

    @api.depends('exit_checklist')
    def exit_progress(self):
        for each in self:
            total_len = self.env['employee.checklist'].search_count([('document_type', '=', 'exit')])
            entry_len = len(each.exit_checklist)
            if total_len != 0:
                each.exit_progress = (entry_len * 100) / total_len

    @api.depends('entry_checklist')
    def entry_progress(self):
        for each in self:
            total_len = self.env['employee.checklist'].search_count([('document_type', '=', 'entry')])
            entry_len = len(each.entry_checklist)
            if total_len != 0:
                each.entry_progress = (entry_len * 100) / total_len

    entry_checklist = fields.Many2many('employee.checklist', 'entry_obj', 'check_hr_rel', 'hr_check_rel',
                                       string='Entry Process',
                                       domain=[('document_type', '=', 'entry')], help="Entry Checklist's")
    exit_checklist = fields.Many2many('employee.checklist', 'exit_obj', 'exit_hr_rel', 'hr_exit_rel',
                                      string='Exit Process',
                                      domain=[('document_type', '=', 'exit')], help="Exit Checklists")
    entry_progress = fields.Float(compute=entry_progress, string='Entry Progress', store=True, default=0.0,
                                  help="Percentage of Entry Checklists's")
    exit_progress = fields.Float(compute=exit_progress, string='Exit Progress', store=True, default=0.0,
                                 help="Percentage of Exit Checklists's")
    maximum_rate = fields.Integer(default=100)
    check_list_enable = fields.Boolean(invisible=True, copy=False)


class EmployeeDocumentInherit(models.Model):
    _inherit = 'hr.employee.document'

    @api.model
    def create(self, vals):
        result = super(EmployeeDocumentInherit, self).create(vals)
        if result.document_name.document_type == 'entry':
            result.employee_ref.write({'entry_checklist': [(4, result.document_name.id)]})
        if result.document_name.document_type == 'exit':
            result.employee_ref.write({'exit_checklist': [(4, result.document_name.id)]})
        return result

    def unlink(self):
        for result in self:
            if result.document_name.document_type == 'entry':
                result.employee_ref.write({'entry_checklist': [(5, result.document_name.id)]})
            if result.document_name.document_type == 'exit':
                result.employee_ref.write({'exit_checklist': [(5, result.document_name.id)]})
        res = super(EmployeeDocumentInherit, self).unlink()
        return res


class EmployeeChecklistInherit(models.Model):
    _inherit = 'employee.checklist'

    entry_obj = fields.Many2many('hr.employee', 'entry_checklist', 'hr_check_rel', 'check_hr_rel',
                                 invisible=1)
    exit_obj = fields.Many2many('hr.employee', 'exit_checklist', 'hr_exit_rel', 'exit_hr_rel',
                                invisible=1)
