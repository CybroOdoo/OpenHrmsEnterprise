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
import re
from datetime import datetime
from odoo import api, models
from odoo.tools import email_split


class HrLeave(models.Model):
    """Inherited hr leave to inherit the message_new function"""
    _inherit = 'hr.leave'

    @api.model
    def message_new(self, msg_dict, custom_values=None):
        """This function extracts required fields of hr. holidays from incoming
         mail then creating records"""
        if custom_values is None:
            custom_values = {}
        msg_subject = msg_dict.get('subject', '')
        mail_from = msg_dict.get('email_from', '')
        subject = re.search(self.env['ir.config_parameter'].sudo(
        ).get_param('hr_holidays.alias_prefix'), msg_subject)
        from_mail = re.search(self.env['ir.config_parameter'].sudo(
        ).get_param('hr_holidays.alias_domain'), mail_from)
        if subject and from_mail:
            email_address = email_split(msg_dict.get('email_from', False))[0]
            employee = self.env['hr.employee'].sudo().search(
                ['|', ('work_email', 'ilike', email_address),
                 ('user_id.email', 'ilike', email_address)], limit=1)
            msg_body = msg_dict.get('body', '')
            cleaner = re.compile('<.*?>')
            clean_msg_body = re.sub(cleaner, '', msg_body)
            date_list = re.findall(r'\d{2}/\d{2}/\d{4}', clean_msg_body)
            if len(date_list) > 0:
                start_date = datetime.strptime(
                    date_list[0], '%d/%m/%Y')
                if len(date_list) == 1:
                    date_to = start_date
                else:
                    date_to = datetime.strptime(
                        date_list[1], '%d/%m/%Y')
                no_of_days_temp = (
                        datetime.strptime(str(date_to),
                                          "%Y-%m-%d %H:%M:%S") -
                        datetime.strptime(str(start_date),
                                          '%Y-%m-%d %H:%M:%S')).days
                custom_values.update({
                    'name': msg_subject.strip(),
                    'employee_id': employee.id,
                    'holiday_status_id': self.env[
                        'hr.leave.type'].search([('requires_allocation',
                                                  '=', 'no')])[0].id,
                    'request_date_from': start_date,
                    'request_date_to': date_to,
                    'number_of_days_display': no_of_days_temp + 1
                })
        return super().message_new(msg_dict, custom_values)
