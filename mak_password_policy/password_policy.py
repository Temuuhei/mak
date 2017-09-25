# -*- coding: utf-8 -*-
##############################################################################
#
#    Asterisk Technologies LLC, Enterprise Management Solution    
#    Copyright (C) 2013-2015 Asterisk Technologies LLC (<http://www.erp.mn>). All Rights Reserved
#
#    Email : chuluunbor@asterisk-tech.mn
#    Phone : 976 + 89057220
#
##############################################################################
import time
from datetime import datetime, timedelta
from functools import partial
from docutils.nodes import field
from openerp.osv import osv, fields
from openerp.osv import osv, fields,orm
import openerp.pooler
from openerp.tools.translate import _
from dateutil.relativedelta import relativedelta
import openerp.addons.decimal_precision as dp
from openerp.http import request
from openerp import SUPERUSER_ID
from __builtin__ import all
from email import _name
import re
from openerp import http
import operator
import logging
_logger = logging.getLogger(__name__)
from openerp.addons.auth_signup.res_users import SignupError

class res_users(osv.osv):
    _inherit = 'res.users'
    
    def write(self, cr, uid, ids, values, context=None):
        if not hasattr(ids, '__iter__'):
            ids = [ids]
        if ids == [uid]:
            for key in values.keys():
                if not (key in self.SELF_WRITEABLE_FIELDS or key.startswith('context_')):
                    break
            else:
                if 'company_id' in values:
                    if not (values['company_id'] in self.read(cr, SUPERUSER_ID, uid, ['company_ids'], context=context)['company_ids']):
                        del values['company_id']
                uid = 1 # safe fields only, so we write as super-user to bypass access rights

        res = super(res_users, self).write(cr, uid, ids, values, context=context)
        if 'company_id' in values:
            for user in self.browse(cr, uid, ids, context=context):
                # if partner is global we keep it that way
                if user.partner_id.company_id and user.partner_id.company_id.id != values['company_id']: 
                    user.partner_id.write({'company_id': user.company_id.id})
        # clear caches linked to the users
        self.pool['ir.model.access'].call_cache_clearing_methods(cr)
        clear = partial(self.pool['ir.rule'].clear_cache, cr)
        map(clear, ids)
        db = cr.dbname
        if db in self.__uid_cache:
            for id in ids:
                if id in self.__uid_cache[db]:
                    del self.__uid_cache[db][id]
        self._context_get.clear_cache(self)
        if 'password' in values:
            print'Temka all right\n\n'
            if re.match(r'[A-Za-z0-9@#$%^&+=]{8,}', values['password']):
                if re.search(r'[A-Z]', values['password']) and re.search(r'[a-z]', values['password']) and re.search(r'[0-9]', values['password']):
                    res=super(res_users, self).write(cr, uid, ids, values, context)  
                else :
                    raise osv.except_osv(_('Error'),
                        _(u'Нууц үгийн урт 8-аас дээш тэмдэгтээс бүтсэн, үсэг, тоо, тусгай тэмдэгт ашигласан байх шаардлагатай.'))
            else :
                raise osv.except_osv(_('Error'),
                        _('Нууц үгийн урт 8-аас дээш тэмдэгтээс бүтсэн, үсэг, тоо, тусгай тэмдэгт ашигласан байх шаардлагатай.'))
        return res
    
    def password_policy (self , cr, uid, new_passwd):  
        users = self.pool.get('user.password.policy')
        user_obj = self.browse(cr, uid, uid)
        if re.match(r'[A-Za-z0-9@#$%^&+=]{8,}', new_passwd):
            user=users.search(cr, SUPERUSER_ID,[('user_id','=',uid)])
            split_new_pass = re.split(r'[0-9@#$%^&+=.]',new_passwd)
            split_username = re.split(r'[0-9@#$%^&+=.]',str(user_obj.login))
            for split in split_new_pass :
                if split.lower() ==split_username[0].lower():
                     raise SignupError(_(u'Нууц үгийн урт 8-аас дээш тэмдэгтээс бүтсэн, үсэг, тоо, тусгай тэмдэгт ашигласан байх шаардлагатай.'))
            if user:
                users.check_password(cr , uid, user[0], new_passwd )
            else :
                users.create(cr, SUPERUSER_ID,{'sequence':'1','user_id':uid,'first_password':new_passwd})    
            return
        else:
            raise SignupError(_(u'Нууц үгийн урт 8-аас дээш тэмдэгтээс бүтсэн, үсэг, тоо, тусгай тэмдэгт ашигласан байх шаардлагатай.'))
        
    def change_password(self, cr, uid, old_passwd, new_passwd, context=None):
        """Change current user password. Old password must be provided explicitly
        to prevent hijacking an existing user session, or for cases where the cleartext
        password is not used to authenticate requests.

        :return: True
        :raise: openerp.exceptions.AccessDenied when old password is wrong
        :raise: except_osv when new password is not set or empty
        """
        self.check(cr.dbname, uid, old_passwd)
        self.password_policy(cr, uid, new_passwd)
        if new_passwd:
            return self.write(cr, uid, uid, {'password': new_passwd})
        raise SignupError(_(u'Нууц үгийн урт 8-аас дээш тэмдэгтээс бүтсэн, үсэг, тоо, тусгай тэмдэгт ашигласан байх шаардлагатай.'))    
        
res_users()

class user_password_policy(osv.osv):
    _name = 'user.password.policy'
    
    _columns = {
                'user_id':fields.many2one('res.users','User'),
                'first_password':fields.char('First Password'),
                'second_password':fields.char('Second Password'),
                'third_password':fields.char('Third Password'),
                'sequence':fields.char('Sequence')
               }
    

    
    def check_password(self, cr, uid, ids,new_passwd):
        user_obj =self.browse(cr, SUPERUSER_ID,ids)
        if new_passwd == user_obj.first_password or new_passwd == user_obj.second_password or new_passwd == user_obj.third_password:
                raise osv.except_osv(_(u'Анхааруулга!'), _(u'Энэ нууц үг өмнө нь хэрэглэгдсэн байна.'))
        elif user_obj.sequence=='3':
            if user_obj.third_password :
                self.write(cr, SUPERUSER_ID, ids, {'first_password':new_passwd,'sequence':'1'})
        elif user_obj.sequence=='1' :
            if user_obj.first_password:
                self.write(cr, SUPERUSER_ID, ids, {'second_password':new_passwd,'sequence':'2'})    
        elif  user_obj.sequence=='2':    
            if user_obj.second_password : 
                self.write(cr, SUPERUSER_ID, ids, {'third_password':new_passwd,'sequence':'3'})
              
        return

    def _password_alarm(self, cr, uid):
        self.send_password_alarm(cr, uid,)
        
    def send_password_alarm(self, cr, uid,):
        model_obj = openerp.pooler.get_pool(cr.dbname).get('ir.model.data')
#         notify_groups = model_obj.get_object_reference(cr, uid, 'l10n_mn_contract_management',group)
        date = datetime.strptime(time.strftime('%Y-%m-%d'), "%Y-%m-%d")
        date_end = date+timedelta(days=7)
        # date_end = date+timedelta(hours=0.06)
        query = "select res.signature as name,p.user_id as user,p.write_date as date from user_password_policy p,res_users res  where res.id=p.user_id ";
        cr.execute(query)
  
        user_ids=[]   
        records = cr.dictfetchall()
        if records:
            template_id = self.pool.get('ir.model.data').get_object_reference(cr, uid, 'mak_password_policy', 'password_policy_reset')[1]
            for record in records:
                my_date = datetime.strptime(record['date'][0:19], "%`Y-%m-%d %H:%M:%S")
                send_date = my_date+timedelta(days=90)
                if date < send_date < date_end:
                    # if date < date_end:
                    data = {
                        'name': record['name'],
                        'base_url': self.pool.get('ir.config_parameter').get_param(cr, uid, 'web.base.url'),
                    }
                    self.pool.get('email.template').send_mail(cr, uid, template_id, record['user'], force_send=True, context=data)
        
        
user_password_policy()
