# -*- coding: utf-8 -*-
###############################################################################
#
#    Cybrosys Technologies Pvt. Ltd.
#
#    Copyright (C) 2024-TODAY Cybrosys Technologies(<https://www.cybrosys.com>)
#    Author: Vyshnav AR (odoo@cybrosys.com)
#
#   This program is under the terms of the Odoo Proprietary License v1.0 (OPL-1)
#    It is forbidden to publish, distribute, sublicense, or sell copies of the
#    Software or modified copies of the Software.
#
#    THE SOFTWARE IS PROVIDED “AS IS”, WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
#    IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
#    FITNESS FOR A PARTICULAR PURPOSE AND NON INFRINGEMENT. IN NO EVENT SHALL
#    THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM,DAMAGES OR OTHER
#    LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE,ARISING
#    FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER
#    DEALINGS IN THE SOFTWARE.
#
###############################################################################
from struct import unpack
from .zkconst import *


def zkconnect(self):
    """Start a connection with the time clock"""
    command = CMD_CONNECT
    command_string = ''
    chksum = 0
    session_id = 0
    reply_id = -1 + USHRT_MAX
    buf = self.createHeader(command, chksum, session_id,
                            reply_id, command_string)
    self.zkclient.sendto(buf, self.address)
    try:
        self.data_recv, addr = self.zkclient.recvfrom(1024)
        self.session_id = unpack('HHHH', self.data_recv[:8])[2]
        return self.checkValid(self.data_recv)
    except:
        return False
    

def zkdisconnect(self):
    """Disconnect from the clock"""
    command = CMD_EXIT
    command_string = ''
    chksum = 0
    session_id = self.session_id
    reply_id = unpack('HHHH', self.data_recv[:8])[3]
    buf = self.createHeader(command, chksum, session_id,
                            reply_id, command_string)
    self.zkclient.sendto(buf, self.address)
    self.data_recv, addr = self.zkclient.recvfrom(1024)
    return self.checkValid(self.data_recv)
