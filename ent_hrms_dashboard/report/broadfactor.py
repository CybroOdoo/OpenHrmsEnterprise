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
from datetime import date, datetime

from odoo import tools
from odoo import api, fields, models


class EmployeeBroadFactor(models.Model):
    _name = "hr.employee.broad.factor"
    _description = "Employee Broadfactor"
    _auto = False

    name = fields.Char()
    no_of_occurrence = fields.Integer()
    no_of_days = fields.Integer()
    broad_factor = fields.Integer()

    def init(self):
        tools.drop_view_if_exists(self._cr, 'hr_employee_broad_factor')
        date_today = date.today()
        print("date_today", date_today)
        self._cr.execute("""
            create or replace view hr_employee_broad_factor as (
                select
                    e.id,
                    e.name, 
                    count(h.*) as no_of_occurrence,
                    sum(h.number_of_days) as no_of_days,
                    count(h.*)*count(h.*)*sum(h.number_of_days) as broad_factor
                from hr_employee e
                    full join (select * from hr_leave where state = 'validate' and date_to <= now()::timestamp) h
                    on e.id =h.employee_id
                group by e.id
               )""")


class ReportOverdue(models.AbstractModel):
    _name = 'report.ent_hrms_dashboard.report_broadfactor'

    @api.model
    def get_report_values(self, docids=None, data=None):
        sql = """select * from hr_employee_broad_factor"""
        self.env.cr.execute(sql)
        lines = self.env.cr.dictfetchall()
        return {
            'doc_model': 'hr.employee.broad_factor',
            'lines': lines,
            'Date': fields.date.today(),
        }
