# -*- coding: utf-8 -*-
##############################################################################
#    
#    OpenERP, Open Source Management Solution
#    Copyright (C) 2015-Today Synconics Technologies Pvt. Ltd.
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

import openerp
from openerp.http import request
from openerp.osv import osv, fields
from openerp import SUPERUSER_ID

class im_chat_message(osv.Model):
	_inherit = "im_chat.message"

	_columns = {
        'attachment_id': fields.many2one('ir.attachment', 'Attachment')
    }

	def download_attachment(self, cr, uid, id_message=None, attachment_id=None, context=None):
		""" Return the content of chat attachments. """
		attachment = self.pool.get('ir.attachment').browse(cr, SUPERUSER_ID, attachment_id, context=context)
		if attachment.datas and attachment.datas_fname:
			return {
				'base64': attachment.datas,
				'filename': attachment.datas_fname,
			}
		return False

	# def post(self, cr, uid, from_uid, uuid, message_type, message_content, attachment=None, context=None):
	# 	if attachment:
	# 		message_id = False
	# 		Session = self.pool['im_chat.session']
	# 		session_ids = Session.search(cr, uid, [('uuid','=',uuid)], context=context)
	# 		notifications = []
	# 		for session in Session.browse(cr, uid, session_ids, context=context):
	# 			# build the new message
	# 			vals = {
	# 				"from_id": from_uid,
	# 				"to_id": session.id,
	# 				"type": message_type,
	# 				"message": message_content,
	# 				"attachment_id": attachment
	# 			}
	# 			# save it
	# 			message_id = self.create(cr, uid, vals, context=context)
	# 			# broadcast it to channel (anonymous users) and users_ids
	# 			data = self.read(cr, uid, [message_id], ['from_id','to_id','create_date','type','message'], context=context)[0]
	# 			notifications.append([uuid, data])
	# 			for user in session.user_ids:
	# 				notifications.append([(cr.dbname, 'im_chat.session', user.id), data])
	# 			self.pool['bus.bus'].sendmany(cr, uid, notifications)
	# 		return message_id
	# 	else:
	# 		return super(im_chat_message, self).post(cr, uid, from_uid, uuid, message_type, message_content, context=context)

# #----------------------------------------------------------
# # Controllers
# #----------------------------------------------------------
# class Controller(openerp.addons.bus.bus.Controller):

#     @openerp.http.route('/im_chat/post', type="json", auth="none")
#     def post(self, uuid, message_type, message_content, attachment=None):
#         registry, cr, uid, context = request.registry, request.cr, request.session.uid, request.context
#         # execute the post method as SUPERUSER_ID
#         message_id = registry["im_chat.message"].post(cr, openerp.SUPERUSER_ID, uid, uuid, message_type, message_content, attachment=attachment, context=context)
#         return message_id

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
