# -*- coding: utf-8 -*-
######################################################################################
#
#    A part of Open HRMS Project <https://www.openhrms.com>
#
#    Copyright (C) 2026-TODAY Cybrosys Technologies(<https://www.cybrosys.com>).
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
    'name': 'Enterprise OpenHRMS Overtime',
    'version': '18.0.1.0.0',
    'category': 'Generic Modules/Human Resources',
    'summary': """This module effectively oversees employee overtime 
     management.""",
    'description': """This module effectively oversees employee overtime 
     management, including tracking overtime hours, facilitating approval 
     workflows, and calculating compensation. It ensures compliance with labor 
     regulations and enhances overall operational efficiency.""",
    'author': 'Cybrosys Techno Solutions, Open HRMS',
    'company': 'Cybrosys Techno Solutions',
    'maintainer': 'Cybrosys Techno Solutions',
    'website': "https://www.openhrms.com",
    'depends': [
        'hr_contract', 'hr_attendance', 'hr_holidays', 'project', 'hr_payroll',
    ],
    'data': [
        'security/ir.model.access.csv',
        'data/ir_sequence_data.xml',
        'views/hr_contract_views.xml',
        'views/hr_overtime_views.xml',
        'views/hr_payroll_views.xml',
        'views/overtime_type_views.xml',
    ],
    'demo':[
        'demo/hr_payroll_structure_type_demo.xml',
        'demo/hr_payslip_input_type_demo.xml',
        'demo/hr_payroll_structure_demo.xml',
        'demo/overtime_type_demo.xml',
        'demo/overtime_type_rule_demo.xml',
        'demo/hr_salary_rule_demo.xml',
    ],
    'external_dependencies': {
        'python': ['pandas'],
    },
    'live_test_url': 'https://youtu.be/lOQCTCxrUKs',
    'images': ['static/description/banner.jpg'],
    'license': 'OPL-1',
    'installable': True,
    'auto_install': False,
    'application': True,
}
