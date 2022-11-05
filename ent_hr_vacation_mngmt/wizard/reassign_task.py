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

from odoo import models, fields, api, _
from odoo.exceptions import UserError


class ReAssignTask(models.TransientModel):
    _name = 'task.reassign'
    _description = 'Task Reassign'

    pending_tasks = fields.One2many('pending.task', related='leave_req_id.pending_tasks', string='Pending Tasks', readonly=False)
    leave_req_id = fields.Many2one('hr.leave', string='Leave Request')

    def action_approve(self):
        task_pending = False
        e_unavail = False
        emp_unavail = []
        for task in self.pending_tasks:
            if not task.assigned_to:
                task_pending = True
        if task_pending:
            raise UserError(_('Please assign pending task to employees.'))
        for task in self.pending_tasks:
            if task.assigned_to in task.unavailable_employee:
                emp_unavail.append(task.assigned_to.name)
                e_unavail = True
        emp_unavail = set(emp_unavail)
        emp_unavail_count = len(emp_unavail)
        if e_unavail:
            if emp_unavail_count == 1:
                raise UserError(_('Selected employee %s is not available') % (', '.join(emp_unavail),))
            else:
                raise UserError(_('Selected employees %s are not available') % (', '.join(emp_unavail),))

        else:
            manager = self.env['hr.employee'].search([('user_id', '=', self.env.uid)], limit=1)
            holiday = self.leave_req_id
            tasks = self.env['project.task']
            for task in self.pending_tasks:
                vals = {
                    'name': task.name,
                    'user_ids': [(3, task.assigned_to.user_id.id)],
                    'project_id': task.project_id.id,
                    'description': task.description,
                }
                tasks.sudo().create(vals)
            # if holiday.double_validation:
            #     return holiday.write({'state': 'validate1', 'manager_id': manager.id if manager else False})
            # else:
                holiday.action_validate()

    def cancel(self):
        for task in self.pending_tasks:
            task.update({'assigned_to': False})
        return {'type': 'ir.actions.act_window_close'}
