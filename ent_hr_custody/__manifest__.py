# -*- coding: utf-8 -*-
###################################################################################
#    A part of OpenHrms Project <https://www.openhrms.com>
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
    'name': 'Enterprise Open HRMS Custody',
    'version': '15.0.1.0.0',
    'summary': """Manage the company properties when it is in the custody of an employee""",
    'description': 'Manage the company properties when it is in the custody of an employee',
    'live_test_url': 'https://www.youtube.com/watch?v=keh3ttj9kws&feature=youtu.be',
    'category': 'Generic Modules/Human Resources',
    'author': 'Cybrosys Techno solutions,Open HRMS',
    'company': 'Cybrosys Techno Solutions',
    'maintainer': 'Cybrosys Techno Solutions',
    'website': "https://www.openhrms.com",
    'depends': ['hr', 'mail', 'ent_hr_employee_updation', 'product', 'stock'],
    'data': [
        'security/ir.model.access.csv',
        'security/custody_security.xml',
        'views/wizard_reason_view.xml',
        'views/custody_view.xml',
        'views/hr_custody_notification.xml',
        'views/hr_employee_view.xml',
        'data/mail_template_data.xml',
        'reports/custody_report.xml'
    ],
    'demo': ['data/demo_data.xml'],
    'images': ['static/description/banner.png'],
    'license': 'AGPL-3',
    'installable': True,
    'auto_install': False,
    'application': False,
}
