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
from datetime import datetime
from odoo import fields, models, _


class HrEmployee(models.Model):
    """ Inherited model for adding announcement features to employee model. """
    _inherit = 'hr.employee'

    def _compute_announcement_count(self):
        """ Compute announcement count for each employee. """
        now_date = datetime.now().date()
        for obj in self:
            announcement_ids_general = self.env[
                'hr.announcement'].sudo().search(
                [('is_announcement', '=', True),
                 ('state', 'in', ('approved', 'done')),
                 ('date_start', '<=', now_date)])
            announcement_ids_emp = self.env['hr.announcement'].sudo().search(
                [('employee_ids', 'in', self.id),
                 ('state', 'in', ('approved', 'done')),
                 ('date_start', '<=', now_date)])
            announcement_ids_dep = self.env['hr.announcement'].sudo().search(
                [('department_ids', 'in', self.department_id.id),
                 ('state', 'in', ('approved', 'done')),
                 ('date_start', '<=', now_date)])
            announcement_ids_job = self.env['hr.announcement'].sudo().search(
                [('position_ids', 'in', self.job_id.id),
                 ('state', 'in', ('approved', 'done')),
                 ('date_start', '<=', now_date)])

            announcement_ids = (announcement_ids_general.ids +
                                announcement_ids_emp.ids +
                                announcement_ids_dep.ids +
                                announcement_ids_job.ids)
            obj.announcement_count = len(set(announcement_ids))

    def action_announcement_view(self):
        """Announcement view for each employee"""
        now_date = datetime.now().date()
        for obj in self:
            announcement_ids_general = self.env[
                'hr.announcement'].sudo().search(
                [('is_announcement', '=', True),
                 ('state', 'in', ('approved', 'done')),
                 ('date_start', '<=', now_date)])
            announcement_ids_emp = self.env['hr.announcement'].sudo().search(
                [('employee_ids', 'in', self.id),
                 ('state', 'in', ('approved', 'done')),
                 ('date_start', '<=', now_date)])
            announcement_ids_dep = self.env['hr.announcement'].sudo().search(
                [('department_ids', 'in', self.department_id.id),
                 ('state', 'in', ('approved', 'done')),
                 ('date_start', '<=', now_date)])
            announcement_ids_job = self.env['hr.announcement'].sudo().search(
                [('position_ids', 'in', self.job_id.id),
                 ('state', 'in', ('approved', 'done')),
                 ('date_start', '<=', now_date)])
            announcement = (announcement_ids_general.ids +
                            announcement_ids_emp.ids + announcement_ids_job.ids
                            + announcement_ids_dep.ids)
            announcement_ids = []
            for record in announcement:
                announcement_ids.append(record)
            view_id = self.env.ref(
                'ent_hr_reward_warning.hr_announcement_view_form').id
            if announcement_ids:
                if len(announcement_ids) > 1:
                    for announce in announcement_ids:
                        value = {
                            'domain': str([('id', 'in', announcement_ids)]),
                            'view_mode': 'tree,form',
                            'res_model': 'hr.announcement',
                            'view_id': False,
                            'type': 'ir.actions.act_window',
                            'name': _('Announcements'),
                            'res_id': announce
                        }
                else:
                    value = {
                        'view_mode': 'form',
                        'res_model': 'hr.announcement',
                        'view_id': view_id,
                        'type': 'ir.actions.act_window',
                        'name': _('Announcements'),
                        'res_id': announcement_ids and announcement_ids[0]
                    }
                return value
    announcement_count = fields.Integer(compute='_compute_announcement_count',
                                        string='# Announcements',
                                        help="Count of Announcement's")
