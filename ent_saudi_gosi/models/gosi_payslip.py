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
from odoo import api, fields, models, _


class GosiPayslip(models.Model):
    """Creates the model gosi.payslip"""
    _name = 'gosi.payslip'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _description = 'GOSI Payslip'

    employee_id = fields.Many2one('hr.employee', string="Employee",
                                  required=True, help="Choose the employee")
    department = fields.Char(string="Department", required=True,
                             help="Choose the department")
    position = fields.Char(string='Job Position', required=True,
                           help="Choose a job position")
    nationality = fields.Char(string='Nationality', required=True,
                              help="Employee nationality")
    type_gosi = fields.Char(string='Type', required=True,
                            tracking=True,
                            help="Choose a gosi type")
    dob = fields.Char(string='Date Of Birth', required=True,
                      help="Enter Date of Birth")
    gos_numb = fields.Char(string='GOSI Number', required=True,
                           tracking=True,
                           help="Enter Gosi number")
    issued_dat = fields.Char(string='Issued Date', required=True,
                             tracking=True,
                             help="Issued date")
    name = fields.Char(string='Reference', required=True, copy=False,
                       readonly=True,
                       default=lambda self: _('New'), help="Enter reference")

    @api.model_create_multi
    def create(self, vals_list):
        """Supering the create method to add the sequence"""
        for vals in vals_list:
            if vals.get('name', _('New')) == _('New'):
                vals['name'] = self.env['ir.sequence'].next_by_code('gosi.payslip') or _('New')
        return super(GosiPayslip, self).create(vals_list)

    @api.onchange('employee_id')
    def _onchange_employee(self):
        """Check the employee and add value on onchange """
        for rec in self:
            if rec.employee_id:
                department = rec.employee_id
                rec.department = department.department_id.name if (
                    department.department_id) else False
                rec.position = department.job_id.name
                rec.nationality = department.country_id.name
                rec.type_gosi = department.type
                rec.dob = department.birthday
                rec.gos_numb = department.gosi_number
                rec.issued_dat = department.issue_date