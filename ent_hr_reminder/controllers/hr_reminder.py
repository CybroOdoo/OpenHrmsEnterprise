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
from datetime import timedelta
from odoo import http, fields
from odoo.http import request


class Reminders(http.Controller):
    """Creates the controller to create the controllers for the working of the
    reminders"""

    @http.route('/hr_reminder/all_reminder', type='json', auth="public")
    def all_reminder(self):
        """Method all_reminder returns the records of the all reminders in the
        model HR Reminder."""
        reminders = []
        for reminder in request.env['hr.reminder'].search([]):
            if reminder.search_by == 'today':
                reminders.append({
                    'id': reminder.id,
                    'name': reminder.name
                })
            elif reminder.search_by == 'set_period':
                if (fields.date.today() >=
                        reminder.date_from and fields.date.today()
                        <= reminder.date_to and (
                                not reminder.expiry_date or fields.date.today()
                                <= reminder.expiry_date)):
                    reminders.append({
                        'id': reminder.id,
                        'name': reminder.name
                    })
            else:
                if fields.date.today() >= reminder.date_set - timedelta(
                        days=reminder.days_before) and (
                        not reminder.expiry_date or fields.date.today()
                        <= reminder.expiry_date):
                    reminders.append({
                        'id': reminder.id,
                        'name': reminder.name
                    })
        return reminders

    @http.route('/hr_reminder/reminder_active', type='json', auth="public")
    def reminder_active(self, **kwargs):
        """Method reminder_active returns the current reminder when clicked in
        view button in the systray."""
        value = []
        for reminder in request.env['hr.reminder'].sudo().search([
            ('name', '=', kwargs.get('reminder_name'))]):
            value.append(reminder.model_id.model)
            value.append(reminder.field_id.name)
            value.append(reminder.search_by)
            value.append(reminder.date_set)
            value.append(reminder.date_from)
            value.append(reminder.date_to)
            value.append(reminder.id)
            value.append(fields.Date.today())
            value.append(reminder.field_id.ttype)
            value.append(reminder.days_before)
            if reminder.date_set:
                value.append(reminder.date_set - timedelta(
                    days=reminder.days_before))
        return value
