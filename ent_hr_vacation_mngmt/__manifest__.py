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
{
    'name': " Enterprise Open HRMS Vacation Management",
    'version': '15.0.1.0.0',
    'summary': """Vacation Management,manages employee vacation""",
    'description': """HR Vacation management""",
    'live_test_url': 'https://youtu.be/Pf7zf-PkdfA',
    'author': 'Cybrosys Techno solutions,Open HRMS',
    'company': 'Cybrosys Techno Solutions',
    'website': 'https://www.openhrms.com',
    'category': 'Generic Modules/Human Resources',
    'maintainer': 'Cybrosys Techno Solutions',
    # 'depends': ['project', 'hr_payroll', 'account',
    #              'hr_holidays', 'ent_hr_payroll_extension', ],

    'depends': ['ent_hr_leave_request_aliasing', 'project', 'hr_payroll', 'account_accountant', 'ent_hr_payroll_extension','hr_holidays'],
    'data': [
        'security/hr_vacation_security.xml',
        'security/ir.model.access.csv',
        'data/hr_payslip_data.xml',
        'views/hr_reminder.xml',
        'data/hr_vacation_data.xml',
        'wizard/reassign_task.xml',
        'views/hr_employee_ticket.xml',
        'views/hr_vacation.xml',
        'views/hr_payslip.xml',
    ],
    'images': ['static/description/banner.png'],
    'license': 'OPL-1',
    'installable': True,
    'auto_install': False,
    'application': False,
}
