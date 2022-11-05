# -*- coding: utf-8 -*-
###################################################################################
#    A part of Open HRMS Project <https://www.openhrms.com>
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
def zkextendfmt(self):
    try:
        test = self.exttrynumber
    except:
        self.exttrynumber = 1
        
    data_seq=[ self.data_recv.encode("hex")[4:6], self.data_recv.encode("hex")[6:8] ]
    if self.exttrynumber == 1:
        plus1 = 0
        plus2 = 0
    else:
        plus1 = -1
        plus2 = +1
        
    
    desc = ": +"+hex( int('99', 16)+plus1 ).lstrip('0x')+", +"+hex(int('b1', 16)+plus2).lstrip("0x")
    self.data_seq1 = hex( int( data_seq[0], 16 ) + int( '99', 16 ) + plus1 ).lstrip("0x")
    self.data_seq2 = hex( int( data_seq[1], 16 ) + int( 'b1', 16 ) + plus2 ).lstrip("0x")
    
    if len(self.data_seq1) >= 3:
        #self.data_seq2 = hex( int( self.data_seq2, 16 ) + int( self.data_seq1[:1], 16) ).lstrip("0x")
        self.data_seq1 = self.data_seq1[-2:]
        
    if len(self.data_seq2) >= 3:
        #self.data_seq1 = hex( int( self.data_seq1, 16 ) + int( self.data_seq2[:1], 16) ).lstrip("0x")
        self.data_seq2 = self.data_seq2[-2:]
        

    if len(self.data_seq1) <= 1:
        self.data_seq1 = "0"+self.data_seq1
        
    if len(self.data_seq2) <= 1:
        self.data_seq2 = "0"+self.data_seq2
    
    
    counter = hex( self.counter ).lstrip("0x")
    if len(counter):
        counter = "0" + counter
    data = "0b00"+self.data_seq1+self.data_seq2+self.id_com+counter+"007e457874656e64466d7400"
    self.zkclient.sendto(data.decode("hex"), self.address)
    try:
        self.data_recv, addr = self.zkclient.recvfrom(1024)
    except:
        if self.exttrynumber == 1:
            self.exttrynumber = 2
            tmp = zkextendfmt(self)
        if len(tmp) < 1:
            self.exttrynumber = 1
    
    self.id_com = self.data_recv.encode("hex")[8:12]
    self.counter = self.counter+1
    return self.data_recv[8:]
