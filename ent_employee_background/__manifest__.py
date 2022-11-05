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
    'name': 'Enterprise  HRMS Employee Background Verification',
    'version': '15.0.1.0.0',
    'summary': """Verify the background details of an Employee """,
    'live_test_url': 'https://youtu.be/Fv2yGCNQJIA',
    'category': 'Generic Modules/Human Resources',
    'description': 'Manage the employees background verification Process employee verification ',
    'author': 'Cybrosys Techno solutions, Open HRMS',
    'company': 'Cybrosys Techno Solutions',
    'maintainer': 'Cybrosys Techno Solutions',
    'website': "https://www.cybrosys.com",
    'depends': ['base', 'hr', 'hr_recruitment', 'mail',
                'ent_hr_employee_updation', 'contacts', 'portal', 'website'],
    'data': [
        'security/ir.model.access.csv',
        'views/view_verification.xml',
        'views/res_partner_agent_view.xml',
        'views/agent_portal_templates.xml',
        'data/default_mail.xml',
    ],
    'demo': ['data/demo_data.xml'],
    'images': ['static/description/banner.png'],
    'license': 'AGPL-3',
    'installable': True,
    'auto_install': False,
    'application': False,
}
