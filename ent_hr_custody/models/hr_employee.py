# -*- coding: utf-8 -*-
###############################################################################
#
#    A part of Open HRMS Project <https://www.openhrms.com>
#
#    Copyright (C) 2024-TODAY Cybrosys Technologies(<https://www.cybrosys.com>)
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
from odoo import models, fields, _


class HrEmployee(models.Model):
    _inherit = 'hr.employee'

    custody_count = fields.Integer(compute='_custody_count',
                                   string='# Custody',
                                   help="Count of custody")
    equipment_count = fields.Integer(compute='_equipment_count',
                                     string='# Equipments')

    def _custody_count(self):
        """To count of all custody contracts"""
        for each in self:
            custody_ids = self.env['hr.custody'].search([('employee', '=',
                                                          each.id)])
            each.custody_count = len(custody_ids)

    def _equipment_count(self):
        """To count of all custody contracts that are in approved state"""
        for each in self:
            equipment_obj = self.env['hr.custody'].search(
                [('employee', '=', each.id), ('state', '=', 'approved')])
            equipment_ids = []
            for each1 in equipment_obj:
                if each1.custody_name.id not in equipment_ids:
                    equipment_ids.append(each1.custody_name.id)
            each.equipment_count = len(equipment_ids)

    def custody_view(self):
        """Smart button action for returning the view of all custody
        contracts related to the current employee"""
        for each1 in self:
            custody_obj = self.env['hr.custody'].\
                search([('employee', '=', each1.id)])
            custody_ids = []
            for each in custody_obj:
                custody_ids.append(each.id)
            view_id = self.env.ref('ent_hr_custody.hr_custody_view_form').id
            if custody_ids:
                if len(custody_ids) <= 1:
                    value = {
                        'view_mode': 'form',
                        'res_model': 'hr.custody',
                        'view_id': view_id,
                        'type': 'ir.actions.act_window',
                        'name': _('Custody'),
                        'res_id': custody_ids and custody_ids[0]
                    }
                else:
                    value = {
                        'domain': str([('id', 'in', custody_ids)]),
                        'view_mode': 'tree,form',
                        'res_model': 'hr.custody',
                        'view_id': False,
                        'type': 'ir.actions.act_window',
                        'name': _('Custody'),
                        'res_id': custody_ids
                    }
                return value

    def equipment_view(self):
        """Smart button action for returning the view of all custody
        contracts that are in approved state, related to the current
        employee"""
        for each1 in self:
            equipment_obj = self.env['hr.custody'].\
                search([('employee', '=', each1.id),
                        ('state', '=', 'approved')])
            equipment_ids = []
            for each in equipment_obj:
                if each.custody_name.id not in equipment_ids:
                    equipment_ids.append(each.custody_name.id)
            view_id = self.env.\
                ref('ent_hr_custody.custody_property_view_form').id
            if equipment_ids:
                if len(equipment_ids) <= 1:
                    value = {
                        'view_mode': 'form',
                        'res_model': 'custody.property',
                        'view_id': view_id,
                        'type': 'ir.actions.act_window',
                        'name': _('Equipments'),
                        'res_id': equipment_ids and equipment_ids[0]
                    }
                else:
                    value = {
                        'domain': str([('id', 'in', equipment_ids)]),
                        'view_mode': 'tree,form',
                        'res_model': 'custody.property',
                        'view_id': False,
                        'type': 'ir.actions.act_window',
                        'name': _('Equipments'),
                        'res_id': equipment_ids
                    }
                return value
