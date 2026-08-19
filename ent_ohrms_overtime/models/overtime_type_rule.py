# -*- coding: utf-8 -*-
######################################################################################
#
#    A part of Open HRMS Project <https://www.openhrms.com>
#
#    Copyright (C) 2026-TODAY Cybrosys Technologies(<https://www.cybrosys.com>).
#    Author: Cybrosys Techno Solutions, (odoo@cybrosys.com)
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
from odoo import fields, models


class OvertimeTypeRule(models.Model):
    """Model holding overtime type rules"""
    _name = 'overtime.type.rule'
    _description = "HR Overtime Type Rule"

    type_line_id = fields.Many2one('overtime.type', string='Over Time Type',
                                   help='Overtime types corresponding to the '
                                        'rule')
    name = fields.Char(string='Name', help='Name of the record', required=True)
    from_hrs = fields.Float(string='From',
                            help='Time from', required=True)
    to_hrs = fields.Float(string='To', help='Time to', required=True)
    hrs_amount = fields.Float(string='Rate', help='Total amount', required=True)
