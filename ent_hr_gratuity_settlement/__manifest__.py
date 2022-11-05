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
#    along with this program. ent_hr_ If not, see <https://www.gnu.org/licenses/>.
#
###################################################################################
{
    'name': 'Enterprise Open HRMS Gratuity Settlement',
    'version': '15.0.1.0.0',
    'summary': """Employee Gratuity Settlement""",
    'description' : 'To manage gratuity settlement for employees',
    'live_test_url': """https://youtu.be/NITjRN6a6Jc""",
    'author': 'Cybrosys Techno solutions,Open HRMS',
    'company': 'Cybrosys Techno Solutions',
    'maintainer': 'Cybrosys Techno Solutions',
    'category': 'Generic Modules/Human Resources',
    'website': "https://www.openhrms.com",
    'depends': ['base', 'hr', 'hr_payroll', 'account_accountant', 'hr_holidays'],
    'data': [
        'data/sequence.xml',
        'views/hr_gratuity_view.xml',
        'views/hr_gratuity_accounting_configuration.xml',
        'views/gratuity_configuration_view.xml',
        'views/hr_contract_views.xml',
        'views/hr_training_view.xml',
        'security/ir.model.access.csv',
    ],
    'images': ['static/description/banner.png'],
    'license': 'AGPL-3',
    'installable': True,
    'auto_install': False,
    'application': False,
}
