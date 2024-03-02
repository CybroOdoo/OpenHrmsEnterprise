# -*- coding: utf-8 -*-
###############################################################################
#
#    A part of Open HRMS Project <https://www.openhrms.com>
#
#    Copyright (C) 2024-TODAY Cybrosys Technologies(<https://www.cybrosys.com>).
#    Author: Cybrosys Techno Solutions (odoo@cybrosys.com)
#
#    This program is under the terms of the Odoo Proprietary
#    License v1.0 (OPL-1)
#    It is forbidden to publish, distribute, sublicense, or sell
#    copies of the Software
#    or modified copies of the Software.
#
#    THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
#    IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
#    FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT.
#    IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM,
#    DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT,
#    TORT OR OTHERWISE,
#    ARISING FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER
#    DEALINGS IN THE SOFTWARE.
#
###############################################################################
from odoo import models, fields, tools


class ReportCustody(models.Model):
    _name = "report.custody"
    _description = "Report Custody"
    _auto = False
    _order = 'name desc'

    name = fields.Char(string='Code', help="Code")
    date_request = fields.Date(string='Requested Date', help="Requested date "
                                                             "of custody")
    employee = fields.Many2one('hr.employee', string='Employee',
                               help="Employee Name")
    purpose = fields.Char(string='Reason', help="Requested Reason")
    custody_name = fields.Many2one('custody.property', string='Property Name',
                                   help="Custody property name")
    return_date = fields.Date(string='Return Date', help="Return date of "
                                                         "property")
    renew_date = fields.Date(string='Renewal Return Date',
                             help="Renewed date of property")
    renew_return_date = fields.Boolean(string='Renewal Return Date',
                                       help="Return date of renewed property")
    state = fields.Selection([('draft', 'Draft'),
                              ('to_approve', 'Waiting For Approval'),
                              ('approved', 'Approved'),
                              ('returned', 'Returned'),
                              ('rejected', 'Refused')],
                             string='Status')

    def _select(self):
        """To select data to report"""
        select_str = """
             SELECT
                    (select 1 ) AS nbr,
                    t.id as id,
                    t.name as name,
                    t.date_request as date_request,
                    t.employee as employee,
                    t.purpose as purpose,
                    t.custody_name as custody_name,
                    t.return_date as return_date,
                    t.renew_date as renew_date,
                    t.renew_return_date as renew_return_date,
                    t.state as state
        """
        return select_str

    def _group_by(self):
        """Group by based on fields"""
        group_by_str = """
                GROUP BY
                    t.id,
                    name,
                    date_request,
                    employee,
                    purpose,
                    custody_name,
                    return_date,
                    renew_date,
                    renew_return_date,
                    state
        """
        return group_by_str

    def init(self):
        """To create report custody"""
        tools.sql.drop_view_if_exists(self._cr, 'report_custody')
        self._cr.execute("""
            CREATE view report_custody as
              %s
              FROM hr_custody t
                %s
        """ % (self._select(), self._group_by()))
