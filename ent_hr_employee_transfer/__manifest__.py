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
    'name': 'Enterprise Open HRMS Branch Transfer',
    'version': '15.0.1.0.1',
    'summary': 'Employee transfer between branches',
    'description' : 'To manage employee transfer between branches',
    'live_test_url': 'https://www.youtube.com/watch?v=gwZ0JpGn-Lw&feature=youtu.be',
    'category': 'Generic Modules/Human Resources',
    'author': 'Cybrosys Techno solutions,Open HRMS',
    'maintainer': 'Cybrosys Techno Solutions',
    'company': 'Cybrosys Techno Solutions',
    'website': 'https://www.openhrms.com',
    'depends': ['base',
                'hr',
                'hr_contract',
                'ent_hr_employee_updation'
                ],
    'data': [
        'views/employee_transfer.xml',
        'security/ir.model.access.csv',
        'security/branch_security.xml',
    ],
    'images': ['static/description/banner.png'],
    'installable': True,
    'application': True,
    'auto_install': False,
    'license': 'AGPL-3',
}
