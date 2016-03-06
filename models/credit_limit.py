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
from openerp import api
from openerp.tools.translate import _
from datetime import datetime

class creditlimit_request(osv.osv):
    _name='creditlimit.request'
    
    def _make_journal_search(self, cr, uid, ttype, context=None):
        journal_pool = self.pool.get('account.journal')
        return journal_pool.search(cr, uid, [('type', '=', ttype)], limit=1)
    
    
    def _get_journal(self, cr, uid, context=None):
        if context is None: context = {}
        ttype = context.get('type', 'bank')
        if ttype in ('payment', 'receipt'):
            ttype = 'bank'
        res = self._make_journal_search(cr, uid, ttype, context=context)
        return res and res[0] or False
    
    def _get_currency(self, cr, uid, context=None):
        if context is None: context = {}
        journal_pool = self.pool.get('account.journal')
        journal_id = context.get('journal_id', False)
        if journal_id:
            if isinstance(journal_id, (list, tuple)):
                # sometimes journal_id is a pair (id, display_name)
                journal_id = journal_id[0]
            journal = journal_pool.browse(cr, uid, journal_id, context=context)
            if journal.currency:
                return journal.currency.id
        return self.pool.get('res.users').browse(cr, uid, uid, context=context).company_id.currency_id.id
    
    def _get_journal_currency(self, cr, uid, ids, name, args, context=None):
        res = {}
        for voucher in self.browse(cr, uid, ids, context=context):
            res[voucher.id] = voucher.journal_id.currency and voucher.journal_id.currency.id or voucher.company_id.currency_id.id
        return res
    
    def _get_period(self, cr, uid, context=None):
        if context is None: context = {}
        if context.get('period_id', False):
            return context.get('period_id')
        periods = self.pool.get('account.period').find(cr, uid, context=context)
        return periods and periods[0] or False
    _columns={
           'partner_id': fields.many2one('res.partner', 'Partner', ondelete='set null',help="Linked partner (optional). Usually created when converting the lead."),
        'bank_name':fields.selection([('HDFC','HDFC'),('ICICI','ICICI'),('SBI','SBI')],'Bank Name'),
        'payment_date':fields.date('Payment Date'),
        'request_date':fields.date('Request Date'),
        'transection_id':fields.char('Cheque No. / Transection No'),
        'credit_limit':fields.float('Credit Limit Amount'),
        'contact_name': fields.char("Account Holder's Name", size=64),
        'name': fields.char('Remark'),
        'state':fields.selection([('draft','Draft'),('approved','Approved'),('cancel','Cancel')],'State'),
        'user_id':fields.many2one('res.users','User'),
        'journal_id':fields.many2one('account.journal', 'Journal', required=True, readonly=True, states={'draft':[('readonly',False)]}),
        'currency_id': fields.function(_get_journal_currency, type='many2one', relation='res.currency', string='Currency', readonly=True, required=True),
        'company_id':fields.many2one('res.company','Company'),
        'period_id': fields.many2one('account.period', 'Period', required=True, readonly=True, states={'draft':[('readonly',False)]}),
        'voucher_id':fields.many2one('account.voucher','Payment Voucher',readonly=True)

        }
    _defaults={
               'period_id': _get_period,
              'journal_id':_get_journal,
              'state':'draft',
              'request_date':fields.datetime.now,
              'user_id':lambda s, cr, uid, c: uid,
              'currency_id': _get_currency,
              'company_id':lambda self,cr,uid,c: self.pool.get('res.company')._company_default_get(cr, uid, 'creditlimit.request',context=c)
              }

    def approved_by_manager(self,cr,uid,ids,context=None):
        for rec in self.browse(cr,uid,ids,context=None):
            voucher_pool = self.pool.get('account.voucher')
            voucher_id = voucher_pool.create(cr, uid, {
                                                            'type':'receipt', 
                                                            'partner_id':rec.partner_id.id, 
                                                            'amount':rec.credit_limit, 
                                                            'account_id':rec.journal_id.default_credit_account_id.id , 
                                                            'journal_id':rec.journal_id.id,
                                                            'company_id':rec.company_id.id,
                                                            'reference':rec.bank_name+'-'+rec.transection_id +'-'+rec.contact_name,
                                                            }, context=context)
            if voucher_id:
                voucher_pool.proforma_voucher(cr, uid, [voucher_id], context=context)
            rec.write({'state':'approved','voucher_id':voucher_id})
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
    
    