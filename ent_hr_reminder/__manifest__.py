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
    'name': 'Enterprise Open HRMS Reminders Todo',
    'version': '15.0.1.0.0',
    'category': 'Generic Modules/Human Resources',
    'summary': 'HR Reminder For OHRMS',
    'description' : 'To manage reminder',
    'author': 'Cybrosys Techno Solutions,Open HRMS',
    'company': 'Cybrosys Techno Solutions',
    'website': "https://www.openhrms.com",
    'maintainer': 'Cybrosys Techno Solutions',
    'depends': ['base', 'hr'],
    'data': [
        'security/ir.model.access.csv',
        'security/hr_reminder_security.xml',
        'views/hr_reminder_view.xml',
        
    ],
    'assets': {
        'web.assets_backend': [
            'ent_hr_reminder/static/src/scss/reminder.scss',
            'ent_hr_reminder/static/src/js/reminder_topbar.js',
        ],
        'web.assets_qweb': [
            'ent_hr_reminder/static/src/xml/reminder_topbar.xml',
        ],
    },
    'images': ['static/description/banner.png'],
    'license': 'OPL-1',
    'installable': True,
    'auto_install': False,
    'application': False,
}
