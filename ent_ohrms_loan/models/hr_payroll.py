# -*- coding: utf-8 -*-
###################################################################################
#    A part of Open HRMS Project <https://www.openhrms.com>
#
#    Cybrosys Technologies Pvt. Ltd.
#    Copyright (C) 2021-TODAY Cybrosys Technologies(<https://www.cybrosys.com>).
#    Author: Cybrosys Techno solutions, Open HRMS (<https://www.cybrosys.com>)

#    This program is free software: you can modify
#    it under the terms of the GNU Affero General Public License (AGPL) as
#    published by the Free Software Foundation, either version 3 of the
#    License, or (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU Affero General Public License for more details.
#
#    You should have received a copy of the GNU Affero General Public License
#    along with this program.  If not, see <https://www.gnu.org/licenses/>.
#
###################################################################################
import time
import babel
from odoo import models, fields, api, tools, _
from datetime import datetime


class HrPayslipInput(models.Model):
    _inherit = 'hr.payslip.input'

    loan_line_id = fields.Many2one('hr.loan.line', string="Loan Installment", help="Loan installment")


class HrPayslip(models.Model):
    _inherit = 'hr.payslip'


    @api.onchange('struct_id', 'date_from', 'date_to', 'employee_id')
    def onchange_employee_loan(self):
        for data in self:
            print("Data:", data)
            if (not data.employee_id) or (not data.date_from) or (not data.date_to):
                return
            if data.input_line_ids.input_type_id:
                data.input_line_ids = [(5, 0, 0)]
            print("Employee:", data)
            loan_line = data.struct_id.rule_ids.filtered(
                lambda x: x.code == 'LO')
            print("Data2213:")
            # loan_line = self.env.ref('ent_ohrms_loan.hr_rule_input_loan')
            if loan_line:
                get_amount = self.env['hr.loan'].search([
                    ('employee_id', '=', data.employee_id.id),
                    ('state', '=', 'approve')
                ], limit=1)
                print(get_amount,'get_amount')

                if get_amount:
                    for lines in get_amount:
                        for line in lines.loan_lines:
                            if data.date_from <= line.date <= data.date_to:
                                if not line.paid:
                                    amount = line.amount
                                    name = loan_line.id
                                    # loan_line.input_id.struct_id = data.struct_id
                                    loan = line.id
                                    self.input_data_line(name, amount, loan)

    def action_payslip_done(self):
        for line in self.input_line_ids:
            if line.loan_line_id:
                line.loan_line_id.paid = True
                line.loan_line_id.loan_id._compute_loan_amount()
        return super(HrPayslip, self).action_payslip_done()

    def input_data_line(self, name, amount, loan):
        for data in self:
            check_lines = []
            new_name = self.env['hr.payslip.input.type'].search([
                ('input_id', '=', name)])
            line = (0, 0, {
                'input_type_id': new_name,
                'amount': amount,
                'name': 'LO',
                'loan_line_id': loan
            })
            check_lines.append(line)
            data.input_line_ids = check_lines


class HrPayslipInputType(models.Model):
    _inherit = 'hr.payslip.input.type'

    input_id = fields.Many2one('hr.salary.rule')


class HrSalaryRule(models.Model):
    _inherit = 'hr.salary.rule'

    company_id = fields.Many2one('res.company', 'Company', copy=False, readonly=True, help="Comapny",
                                 default=lambda self: self.env.user.company_id)


class HrPayrollStructure(models.Model):
    _inherit = 'hr.payroll.structure'

    company_id = fields.Many2one('res.company', 'Company', copy=False, readonly=True, help="Comapny",
                                 default=lambda self: self.env.user.company_id)

