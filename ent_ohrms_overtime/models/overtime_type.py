# -*- coding: utf-8 -*-
######################################################################################
#
#    A part of Open HRMS Project <https://www.openhrms.com>
#
#    Copyright (C) 2026-TODAY Cybrosys Technologies(<https://www.cybrosys.com>).
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
from odoo import api, fields, models


class OvertimeType(models.Model):
    """Model holding the overtime types"""
    _name = 'overtime.type'
    _description = "HR Overtime Type"

    name = fields.Char(string='Name', help='Name of the record')
    type = fields.Selection([('cash', 'Cash'),
                             ('leave', 'Leave ')],
                            string='Type',
                            help='Type of overtime')
    duration_type = fields.Selection([('hours', 'Hour'), ('days', 'Days')],
                                     string="Duration Type",
                                     help='Type of duration',
                                     default="hours",
                                     required=True)
    leave_type_id = fields.Many2one('hr.leave.type',
                                    string='Leave Type',
                                    help='Type of leave',
                                    domain="[('id', 'in', leave_type_ids)]")
    leave_type_ids = fields.Many2many('hr.leave.type',
                                      string='Leave Type',
                                      help='Corresponding leave types',
                                      compute="_compute_leave_type_ids")
    rule_line_ids = fields.One2many('overtime.type.rule',
                                    'type_line_id',
                                    string='Rules',
                                    help='Rules corresponding to this type')

    @api.depends('duration_type')
    def _compute_leave_type_ids(self):
        """Compute leave_type_ids based on duration_type."""
        for record in self:
            dur = 'day' if record.duration_type == 'days' else 'hour'
            record.leave_type_ids = [(6, 0, record.env['hr.leave.type'].search(
                [('request_unit', '=', dur)]).ids)]
