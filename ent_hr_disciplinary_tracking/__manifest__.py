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

    'name': 'Enterprise Open HRMS Disciplinary Tracking',
    'version': '15.0.1.0.0',
    'summary': """Employee Disciplinary Tracking Management""",
    'description': 'To manage employee disciplinary tracking',
    'live_test_url': 'https://youtu.be/LFuw2iY4Deg',
    'author': 'Cybrosys Techno Solutions, Open HRMS',
    'company': 'Cybrosys Techno Solutions',
    'maintainer': 'Cybrosys Techno Solutions',
    'category': 'Generic Modules/Human Resources',
    'website': "https://www.openhrms.com",
    'depends': ['base', 'mail', 'hr',],
    'data': ['views/disciplinary_action.xml',
             'views/disciplinary_sequence.xml',
             'views/category_view.xml',
             'security/ir.model.access.csv',
             'security/security.xml'],
    'demo': ['data/demo_data.xml'],
    'images': ['static/description/banner.png'],
    'license': 'OPL-1',
    'installable': True,
    'auto_install': False,
    'application': False,
}
