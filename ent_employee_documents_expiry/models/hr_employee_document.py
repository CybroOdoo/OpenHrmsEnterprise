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
from datetime import date, timedelta
from odoo import api, fields, models, _
from odoo.exceptions import UserError


class HrEmployeeDocuments(models.Model):
    """Set reminder of employee document expiry"""
    _name = 'hr.employee.document'
    _description = 'HR Employee Documents'

    def mail_reminder(self):
        """Sending document expiry notification to employees."""
        date_now = fields.Date.today()
        for record in self.search([]):
            if record.expiry_date:
                if record.notification_type == 'single':
                    if date_now == record.expiry_date:
                        mail_content = ("  Hello  " + record.employee_ref_id.
                                        name + ",<br>Your Document " +
                                        record.name +
                                        " is expiring today, please renew it")
                        main_content = {
                            'subject': _('Document-%s Expired On %s') % (
                                record.name, record.expiry_date),
                            'author_id': self.env.user.partner_id.id,
                            'body_html': mail_content,
                            'email_to': record.employee_ref_id.work_email,
                        }
                        self.env['mail.mail'].create(main_content).send()
                elif record.notification_type == 'multi':
                    exp_date = fields.Date.from_string(
                        record.expiry_date) - timedelta(days=record.before_days)
                    if date_now == exp_date or date_now == record.expiry_date:
                        mail_content = ("  Hello  " + record.employee_ref_id.
                                        name + ",<br>Your Document " +
                                        record.name + " is going to expire on "
                                        + str(record.expiry_date) +
                                        ". Please renew it before expiry date")
                        main_content = {
                            'subject': _('Document-%s Expiry on %s') % (
                                record.name, record.expiry_date),
                            'author_id': self.env.user.partner_id.id,
                            'body_html': mail_content,
                            'email_to': record.employee_ref_id.work_email,
                        }
                        self.env['mail.mail'].create(main_content).send()
                elif record.notification_type == 'everyday':
                    exp_date = fields.Date.from_string(
                        record.expiry_date) - timedelta(days=record.before_days)
                    if exp_date <= date_now <= record.expiry_date:
                        mail_content = ("  Hello  " +
                                        record.employee_ref_id.name
                                        + ",<br>Your Document " + record.name +
                                        " is going to expire on " +
                                        str(record.expiry_date) +
                                        ". Please renew it before expiry date")
                        main_content = {
                            'subject': _('Document-%s Expiry on %s') % (
                                record.name, record.expiry_date),
                            'author_id': self.env.user.partner_id.id,
                            'body_html': mail_content,
                            'email_to': record.employee_ref_id.work_email,
                        }
                        self.env['mail.mail'].create(main_content).send()
                elif record.notification_type == 'everyday_after':
                    exp_date = fields.Date.from_string(
                        record.expiry_date) + timedelta(days=record.before_days)
                    if record.expiry_date <= date_now <= exp_date:
                        mail_content = ("  Hello  " +
                                        record.employee_ref_id.name +
                                        ",<br>Your Document " + record.name +
                                        " is expired on " +
                                        str(record.expiry_date) +
                                        ". Please renew it ")
                        main_content = {
                            'subject': _('Document-%s Expired On %s') % (
                                record.name, record.expiry_date),
                            'author_id': self.env.user.partner_id.id,
                            'body_html': mail_content,
                            'email_to': record.employee_ref_id.work_email,
                        }
                        self.env['mail.mail'].create(main_content).send()
                else:
                    exp_date = fields.Date.from_string(
                        record.expiry_date) - timedelta(days=7)
                    if date_now == exp_date:
                        mail_content = ("  Hello  " + record.employee_ref_id.
                                        name + ",<br>Your Document " +
                                        record.name + " is going to expire on "
                                        + str(record.expiry_date) +
                                        ". Please renew it before expiry date ")
                        main_content = {
                            'subject': _('Document-%s Expired On %s') % (
                                record.name, record.expiry_date),
                            'author_id': self.env.user.partner_id.id,
                            'body_html': mail_content,
                            'email_to': record.employee_ref_id.work_email,
                        }
                        self.env['mail.mail'].create(main_content).send()

    @api.constrains('expiry_date')
    def check_expr_date(self):
        for each in self:
            if each.expiry_date:
                exp_date = fields.Date.from_string(each.expiry_date)
                if exp_date < date.today():
                    raise UserError(_('Your Document Is Expired.'))

    name = fields.Char(string='Document Number', required=True, copy=False,
                       help='You can give your Document number.')
    description = fields.Text(string='Description', copy=False,
                              help="Description about the document")
    expiry_date = fields.Date(string='Expiry Date', copy=False,
                              help="Date of expiry of documents")
    employee_ref_id = fields.Many2one(comodel_name='hr.employee', invisible=1,
                                      copy=False)
    doc_attachment_ids = fields.Many2many(comodel_name='ir.attachment',
                                          relation='doc_attach_rel_ids',
                                          column1='doc_id',
                                          column2='attach_id3',
                                          string="Attachment",
                                          help='You can attach the copy of your'
                                               'document', copy=False)
    issue_date = fields.Date(string='Issue Date',
                             default=fields.datetime.now(),
                             help="Date of issue of employee documents",
                             copy=False)
    document_type_id = fields.Many2one(comodel_name='document.type',
                                       string="Document Type",
                                       help="Document type of employee")
    before_days = fields.Integer(string="Days",
                                 help="How many number of days before to get "
                                      "the notification email")
    notification_type = fields.Selection([
        ('single', 'Notification on expiry date'),
        ('multi', 'Notification before few days'),
        ('everyday', 'Everyday till expiry date'),
        ('everyday_after', 'Notification on and after expiry')
    ], string='Notification Type',
        help="Notification on expiry date: You will get notification only on "
             "expiry date. Notification before few days: You will get "
             "notification in 2 days.On expiry date and number of days before "
             "date. Everyday till expiry date: You will get notification from "
             "number of days till the expiry date of the document. Notification"
             " on and after expiry: You will get notification on the expiry "
             "date and continues up to Days. If you didn't select any then you "
             "will get notification before 7 days of document expiry.")
