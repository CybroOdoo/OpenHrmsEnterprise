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
    'name': "Enterprise Open HRMS Employee Shift",
    'version': '16.0.1.0.0',
    'summary': """Easily create, manage, and track employee shift schedules.""",
    'description': """Easily create, manage, and track employee shift schedules.""",
    'live_test_url': 'https://youtu.be/o580wqD9Nig',
    'category': 'Human Resource',
    'author': "Cybrosys Techno Solutions,Open HRMS",
    'company': 'Cybrosys Techno Solutions',
    'maintainer': 'Cybrosys Techno Solutions',
    'website': "https://www.openhrms.com",
    'depends': ['hr', 'hr_payroll', 'resource', 'hr_contract'],
    'data': [
        'security/ir.model.access.csv',
        'security/hr_employee_shift_security.xml',
        'views/hr_employee_shift_view.xml',
        'views/hr_employee_contract_view.xml',
        'views/hr_generate_shift_view.xml',
    ],
    'demo': [
        'demo/shift_schedule_data.xml',
    ],
    'images': ["static/description/banner.png"],
    'license': 'OPL-1',
    'installable': True,
    'application': True,
}
