# -*- coding: utf-8 -*-
################################################################################
#
#    A part of OpenHRMS Project <https://www.openhrms.com>
#
#    Copyright (C) 2026-TODAY Cybrosys Technologies(<https://www.cybrosys.com>).
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
{
    'name': "Enterprise Open HRMS - HR Dashboard",
    'version': '19.0.1.0.0',
    'category': 'Generic Modules/Human Resources',
    'summary': """Open HRMS HR dashboard,facilitates with various 
     metrics helping easy to view, understand, and share data. Experience the 
     new kind of responsiveness with Open HRMS Dashboard""",
    'description': """Human Resource Departments have a lot to manage and 
     volume to track with reports ever growing. Fortunately, technologies 
     provide elegant solutions to track and monitor every essential Human 
     Resource activities. Open HRMS HR Dashboard provides a visually engaging
     palate for seamless management of Human Resource functions. It provides
     executives and employees the information they need. Open HRMS Dashboard 
     comes intuitive and interactive connecting every dots of your data like 
     never before. With Open HRMS HR dashboard,facilitates with various 
     metrics helping easy to view, understand, and share data.Experience the 
     new kind of responsiveness with Open HRMS Dashboard""",
    'live_test_url': 'https://youtu.be/XwGGvZbv6sc',
    'author': "Cybrosys Techno Solutions,Open HRMS",
    'company': 'Cybrosys Techno Solutions',
    'maintainer': 'Cybrosys Techno Solutions',
    'website': "https://www.openhrms.com",
    'depends': ['hr', 'hr_holidays', 'hr_timesheet', 'hr_payroll',
                'hr_attendance', 'hr_timesheet_attendance',
                'hr_recruitment', 'ent_hr_resignation', 'event',
                'ent_hr_reward_warning', 'base'],
    'data': [
        'security/ir.model.access.csv',
        'report/hr_employee_broad_factor_views.xml',
        'views/hr_leave_views.xml',
        'views/ent_hrms_dashboard_menus.xml'
    ],
    'assets': {
        'web.assets_backend': [
            'https://cdnjs.cloudflare.com/ajax/libs/Chart.js/4.4.0/chart.umd.min.js',
            'ent_hrms_dashboard/static/src/css/hrms_dashboard.css',
            'ent_hrms_dashboard/static/src/js/hrms_dashboard.js',
            'https://cdn.jsdelivr.net/npm/d3@7.9.0/dist/d3.min.js',
            'ent_hrms_dashboard/static/src/xml/hrms_dashboard_templates.xml',
            'https://cdnjs.cloudflare.com/ajax/libs/moment.js/2.29.4/moment.min.js',
            'https://cdnjs.cloudflare.com/ajax/libs/font-awesome/5.15.3/css/all.min.css',
        ],
    },
    'external_dependencies': {
        'python': ['pandas'],
    },
    'images': ["static/description/banner.jpg"],
    'license': "OPL-1",
    'installable': True,
    'auto_install': False,
    'application': True,
}