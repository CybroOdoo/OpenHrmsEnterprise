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
import babel
from datetime import datetime, time
from odoo import fields, models, tools


class HrPayslip(models.Model):
    """ Class for inheriting hr payslip. """
    _inherit = 'hr.payslip'

    def action_payslip_done(self):
        """
           The function mark the loan as paid and call the action paid amount
           function for creating an invoice.
        """
        for line in self.input_line_ids:
            date_from = self.date_from
            tym = datetime.combine(fields.Date.from_string(date_from),
                                   time.min)
            locale = self.env.context.get('lang') or 'en_US'
            month = tools.ustr(
                babel.dates.format_date(date=tym, format='MMMM-y',
                                        locale=locale))
            if line.loan_line_id:
                line.loan_line_id.action_paid_amount(month)
        return super(HrPayslip, self).action_payslip_done()
