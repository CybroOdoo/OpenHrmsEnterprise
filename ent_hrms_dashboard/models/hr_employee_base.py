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
from datetime import timedelta
from odoo import models, fields


class HrEmployeeBase(models.Model):
    """Inherits the model hr.employee to override the
     method _compute_newly_hired"""
    _inherit = 'hr.employee'

    def _compute_newly_hired(self):
        """
            Compute the 'newly_hired' field for employees based on the new hire
            date. This method calculates the 'newly_hired' field value for each
            employee by comparing their new hire date with a threshold date
            (90 days ago).

            v18 -> v19 migration note:
            In v19 the method signature is unchanged but we guard against
            employees that may not have a 'newly_hired' field defined (e.g.
            if the hr_contract module is not installed).
        :return: None
        """
        new_hire_field = self._get_new_hire_field()
        new_hire_date = (fields.Datetime.now() - timedelta(days=90)).date()
        for employee in self:
            if not hasattr(employee, 'newly_hired'):
                continue
            emp_date = employee[new_hire_field]
            if hasattr(emp_date, 'date'):
                emp_date = emp_date.date()
            employee.newly_hired = bool(emp_date and emp_date > new_hire_date)