# -*- coding: utf-8 -*-
###################################################################################
#    A part of Open HRMS Project <https://www.openhrms.com>
#
#    Cybrosys Technologies Pvt. Ltd.
#    Copyright (C) 2021-TODAY Cybrosys Technologies(<https://www.cybrosys.com>).
#    Author: Cybrosys Techno solutions, Open HRMS (<https://www.cybrosys.com>)

#    This program is free software: you can modify
#    it under the terms of the GNU Affero General Public License (AGPL) as
#    published by the Free Software Foundation, either version 3 of the
#    License, or (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU Affero General Public License for more details.
#
#    You should have received a copy of the GNU Affero General Public License
#    along with this program.  If not, see <https://www.gnu.org/licenses/>.
#
###################################################################################
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
    'license': 'AGPL-3',
    'installable': True,
    'auto_install': False,
    'application': False,
}
