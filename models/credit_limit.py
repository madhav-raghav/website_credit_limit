# -*- coding: utf-8 -*-
##############################################################################
#
#    OpenERP, Open Source Management Solution
#    Copyright (C) 2004-2010 Tiny SPRL (<http://tiny.be>).
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU Affero General Public License as
#    published by the Free Software Foundation, either version 3 of the
#    License, or (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU Affero General Public License for more details.
#
#    You should have received a copy of the GNU Affero General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
##############################################################################

from openerp.osv import fields,osv
from openerp.tools.translate import _
from datetime import datetime

class creditlimit_request(osv.osv):
    _name='creditlimit.request'
    
    _columns={
           'partner_id': fields.many2one('res.partner', 'Partner', ondelete='set null',help="Linked partner (optional). Usually created when converting the lead."),
        'credit_limit':fields.float('Credit Limit Amount'),
        'partner_name': fields.char("Customer Name", size=64,help='The name of the future partner company that will be created while converting the lead into opportunity', select=1),
        'phone': fields.char("Phone", size=64),
        'contact_name': fields.char('Contact Name', size=64),
        'email_from': fields.char('Email', size=128, help="Email address of the contact"),
        'name': fields.char('Subject'),
        'state':fields.selection([('draft','Draft'),('approved','Approved'),('cancel','Cancel')],'State'),
        'create_date':fields.datetime('Date'),
         'description': fields.text('Notes'),
         'user_id': fields.many2one('res.users', 'Salesperson'),
        'street': fields.char('Street'),
        'street2': fields.char('Street2'),
        'zip': fields.char('Zip', size=24),
        'city': fields.char('City'),
        'state_id': fields.many2one("res.country.state", 'State'),
        'country_id': fields.many2one('res.country', 'Country'),
        'phone': fields.char('Phone'),
        'fax': fields.char('Fax'),
        'mobile': fields.char('Mobile'),
        'function': fields.char('Function'),
        'title': fields.many2one('res.partner.title', 'Title'),
        'company_id': fields.many2one('res.company', 'Company'),
        }
    _defauls={
              'state':'draft',
              'create_date':fields.datetime.now,
              'user_id':lambda s, cr, uid, c: uid,
              }
    
    def approved_by_manager(self,cr,uid,ids,context=None):
        for rec in self.browse(cr,uid,ids,context=None):
            credit_deatail_values = {}
            credit_details_pool = self.pool.get('credit.details')
            partner_pool = self.pool.get('res.partner')
            parnter_id = partner_pool.search(cr,uid,[('email','=',rec.email_from)])
            if not parnter_id:
                raise osv.except_osv(_('Warning'), _(" %s Email Id customer not found.Please configure the customer Email address") % (rec.email_from))
            credit_details_id = credit_details_pool.search(cr,uid,[('partner_id','in',parnter_id)])
            import time
            credit_deatail_values={
                                   'name':parnter_id and parnter_id[0],
                                   
                                   }
            if not credit_details_id:
                credit_details_id = credit_details_pool.create(cr,uid,ids,credit_deatail_values,context=None)
            credit_line_values={
                                'credit_limit':rec.credit_limit or 0.0,
                                'credit_details_id':credit_details_id and credit_details_id[0],
                                'cl_applicable_date':str(time.strftime("%Y-%m-%d %H:%M:%S"))
                                }    
            self.pool.get('credit.limit.details').create(cr,uid,credit_line_values,context=None)
            self.write(cr,uid,ids,{'state':'approved'})
            return True

    def cancel_state(self,cr,uid,ids,context=None):
        self.write(cr,uid,ids,{'state':'cancel'})
        return True


    
    def onchange_partner_id(self, cr, uid, ids, partner, context=None):
        """ This function returns value of partner email address based on partner
            :param part: Partner's id
        """
        result = {}
        if partner:
            partner = self.pool['res.partner'].browse(cr, uid, partner, context)
            result['email_from'] = partner.email
            result['street'] = partner.street
            result['street2'] = partner.street2
            result['city'] = partner.city
            result['state_id'] = partner.state_id and partner.state_id.id or False
            result['zip'] = partner.zip
            result['country_id'] = partner.country_id and partner.country_id.id or False
            result['title'] = partner.title and partner.title.id or False
            result['phone'] = partner.phone
            result['mobile'] = partner.mobile
            result['fax'] = partner.fax
        return {'value': result}
    
    