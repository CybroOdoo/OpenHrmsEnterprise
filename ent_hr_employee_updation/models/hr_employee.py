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
from odoo import api, fields, models, _


class HrEmployee(models.Model):
    """ Method for adding private information of employee. """
    _inherit = 'hr.employee'

    def mail_reminder(self):
        """Sending expiry date notification for ID and Passport"""

        current_date = fields.Date.context_today(self) + timedelta(days=1)
        employee_ids = self.search(['|', ('id_expiry_date', '!=', False),
                                    ('passport_expiry_date', '!=', False)])
        for emp in employee_ids:
            if emp.id_expiry_date:
                exp_date = fields.Date.from_string(
                    emp.id_expiry_date) - timedelta(days=14)
                if current_date >= exp_date:
                    mail_content = ("  Hello  " + emp.name + ",<br>Your ID "
                                    + emp.identification_id +
                                    "is going to expire on " +
                                    str(emp.id_expiry_date) +
                                    ". Please renew it before expiry date")
                    main_content = {
                        'subject': _('ID-%s Expired On %s') % (
                            emp.identification_id, emp.id_expiry_date),
                        'author_id': self.env.user.partner_id.id,
                        'body_html': mail_content,
                        'email_to': emp.work_email,
                    }
                    self.env['mail.mail'].sudo().create(main_content).send()
            if emp.passport_expiry_date:
                exp_date = fields.Date.from_string(
                    emp.passport_expiry_date) - timedelta(days=180)
                if current_date >= exp_date:
                    mail_content = (" Hello " + emp.name + ",<br>Your Passport"
                                    + emp.passport_id + "is going to expire on"
                                    + str(emp.passport_expiry_date)
                                    + ". Please renew it before expire")
                    main_content = {
                        'subject': _('Passport-%s Expired On %s') % (
                            emp.passport_id, emp.passport_expiry_date),
                        'author_id': self.env.user.partner_id.id,
                        'body_html': mail_content,
                        'email_to': emp.work_email,
                    }
                    self.env['mail.mail'].sudo().create(main_content).send()

    personal_mobile = fields.Char(
        string='Mobile',
        help="Personal mobile number of the employee")
    joining_date = fields.Date(
        string='Joining Date',
        help="Employee joining date computed from the contract start date",
        compute='_compute_joining_date', store=True)
    id_expiry_date = fields.Date(
        string='Expiry Date',
        help='Expiry date of Identification ID')
    passport_expiry_date = fields.Date(
        string='Expiry Date',
        help='Expiry date of Passport ID')
    id_attachment_ids = fields.Many2many(
        comodel_name='ir.attachment', relation='id_attachment_rel',
        column1='id_ref', column2='attach_ref',
        string="Attachment",
        help='You can attach the copy of your Id')
    passport_attachment_ids = fields.Many2many(
        comodel_name='ir.attachment',
        relation='passport_attachment_rel',
        column1='passport_ref', column2='attach_ref1',
        string="Attachment",
        help='You can attach the copy of Passport')
    fam_ids = fields.One2many(
        comodel_name='hr.employee.family', inverse_name='employee_id',
        string='Family', help='Family Information')

    @api.depends('contract_id')
    def _compute_joining_date(self):
        for rec in self:
            rec.joining_date = min(rec.contract_id.mapped('date_start')) \
                if rec.contract_id else False

    @api.onchange('spouse_complete_name', 'spouse_birthdate')
    def _onchange_spouse(self):
        relation = self.env.ref(
            'ent_hr_employee_updation.hr_employee_relation_spouse')
        if self.spouse_complete_name and self.spouse_birthdate:
            self.fam_ids = [(0, 0, {
                'member_name': self.spouse_complete_name,
                'relation_id': relation.id,
                'birth_date': self.spouse_birthdate,
            })]
