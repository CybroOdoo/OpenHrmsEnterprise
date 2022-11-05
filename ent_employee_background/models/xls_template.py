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
import logging
from odoo import models


class DefaultTemplateXls(models.AbstractModel):
    _name = 'report.ent_employee_background.default_verification_details'
    # _inherit = 'report.report_xlsx.abstract'

    _logger = logging.getLogger(__name__)

    try:
        _inherit = 'report.report_xlsx.abstract'
    except ImportError:
        _logger.debug('Cannot find report_xlsx module for version 11')

    def generate_xlsx_report(self, workbook, data, obj):
        sheet = workbook.add_worksheet()
        format1 = workbook.add_format({'font_size': 16, 'align': 'center', 'bg_color': '#D3D3D3', 'bold': True})
        format2 = workbook.add_format({'font_size': 10, 'bold': True})
        format3 = workbook.add_format({'font_size': 10})

        sheet.merge_range('B1:E1', 'Required Details', format1)
        sheet.merge_range('A2:B2', 'Applicant Name:', format3)
        sheet.merge_range('A3:C3', 'Information Required', format2)
        sheet.merge_range('D3:F3', 'Details Given', format2)
        sheet.merge_range('G3:I3', 'Details(Correct/Wrong)', format2)
        sheet.merge_range('A5:C5', 'Education Details', format3)
        sheet.merge_range('B6:C6', 'Graduation', format3)
        sheet.merge_range('D6:F6', '', format3)
        sheet.merge_range('G6:I6', '', format3)
        sheet.merge_range('B7:C7', 'Plus Two', format3)
        sheet.merge_range('D7:F7', '', format3)
        sheet.merge_range('G7:I7', '', format3)
        sheet.merge_range('A9:C9', 'Work Details', format3)
        sheet.merge_range('D9:F9', '', format3)
        sheet.merge_range('G9:I9', '', format3)
        sheet.merge_range('A11:C11', 'Criminal Background', format3)
        sheet.merge_range('D11:F11', '', format3)
        sheet.merge_range('G11:I11', '', format3)
        sheet.merge_range('A13:C13', 'Disciplinary Allegation in Previous Work Locations', format3)
        sheet.merge_range('D13:F13', '', format3)
        sheet.merge_range('G13:I13', '', format3)
