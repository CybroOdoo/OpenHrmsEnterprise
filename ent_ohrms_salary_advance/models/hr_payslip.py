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
from odoo import models


class HrPayslip(models.Model):
    """ Model for adding advance salary computations in hr_payslip. """
    _inherit = 'hr.payslip'

    def input_data_salary_line(self, name, amount):
        """ Set updated values to other input lines. """
        check_lines = []
        input_type = self.env['hr.payslip.input.type'].search([
            ('input_id', '=', name)])
        line = (0, 0, {
            'input_type_id': input_type.id,
            'amount': amount,
        })
        check_lines.append(line)
        self.input_line_ids = check_lines

    def compute_sheet(self):
        """ Method for inherit and adding advance salary input line in
        payslip lines"""
        salary_line = self.struct_id.rule_ids.filtered(
                        lambda x: x.code == 'SAR')
        if salary_line:
            get_amount = self.env['salary.advance'].search([
                ('employee_id', '=', self.employee_id.id),
                ('state', '=', 'approve')
            ])
            if get_amount:
                if self.date_from <= get_amount.date <= self.date_to:
                    amount = get_amount.advance
                    name = salary_line.id
                    code = salary_line.code
                    if (code not in self.input_line_ids.mapped('input_type_id').
                            mapped('code')):
                        self.input_data_salary_line(name, amount)
        return super(HrPayslip, self).compute_sheet()
