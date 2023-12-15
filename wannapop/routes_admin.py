from flask import request, redirect, url_for, Blueprint, render_template, flash, current_app 
from .models import User, Blocked_User, Banned_Product, Product
from .helper_role import Role, role_required
from . import db_manager as db

current_app.logger.debug('A value for debugging:')
# Blueprint
admin_bp = Blueprint("admin_bp", __name__)

@admin_bp.route('/admin')
@role_required(Role.admin, Role.moderator)
def admin_index():
    return render_template('admin/index.html')

@admin_bp.route('/admin/users')
@role_required(Role.admin)
def admin_users():
    users = db.session.query(User).all()
    return render_template('admin/users_list.html', users=users)

#---------BLOQUEAR USUARIOS--------------------


@admin_bp.route('/admin/users/block')
@role_required(Role.admin)
def block_user_page():
    block_user = db.session.query(User).all()
    return render_template('admin/form_block_user.html', users=block_user)


@admin_bp.route('/admin/users/block', methods=['POST'])
@role_required(Role.admin)
def block_user():
    # Bloquear usuario
    user_id_blocked = request.form.get('user_id')
    user_blocked =  User.query.filter_by(id=user_id_blocked).first()
    
    if user_blocked:
    
        blocked_user = Blocked_User(user_id=user_blocked.id, message=request.form['message'])

        db.session.add(blocked_user)
        db.session.commit()
        return redirect(url_for('admin_bp.admin_users'))
    
    return "Error: Usuario no encontrado"

#---------DESBLOQUEAR USUARIOS-------------------


@admin_bp.route('/admin/users/unblock')
@role_required(Role.admin)
def unblock_user_page():
    blocked_users= db.session.query(Blocked_User).all()
    return render_template('admin/form_unblock_user.html', blocked_users=blocked_users)



@admin_bp.route('/admin/users/unblock', methods=['POST'])
@role_required(Role.admin)
def unblock_user():
    # Desbloquear usuario
    unblocked_user_id = request.form.get('user_id')
    user_unblocked = Blocked_User.query.filter_by(id=unblocked_user_id).first()
    if user_unblocked:
        db.session.delete(user_unblocked)
        db.session.commit()
    return redirect(url_for('admin_bp.admin_users'))




#############------PRODUCTOS----BANEADOS------
@admin_bp.route('/admin/products/list/ban')
@role_required(Role.moderator)
def product_list():
    products = db.session.query(Product).all()
    return render_template('admin/products_list.html', products=products)



@admin_bp.route('/admin/products/{product_id}/ban',methods = ['POST'])
@role_required(Role.moderator)
def ban_product():

    product_id = request.form.get('product_id')

    # Verifica si el producto ya está en la lista de productos baneados
    banned_product = Banned_Product.query.filter_by(product_id=product_id).first()

    if not banned_product:
        # Si no está baneado, lo agregamos a la lista de productos baneados
        banned_product = Banned_Product(product_id=product_id)
        db.session.add(banned_product)
        db.session.commit()

    return redirect(url_for('product_list'))  # Redirige a alguna vista de la lista de productos

@admin_bp.route('/admin/products/unban', methods=['POST'])
@role_required(Role.moderator)
def unban_product():
    product_id = request.form.get('product_id')

    # Busca el producto en la lista de productos baneados
    banned_product = Banned_Product.query.filter_by(product_id=product_id).first()

    if banned_product:
        # Si está baneado, lo eliminamos de la lista de productos baneados
        db.session.delete(banned_product)
        db.session.commit()

    return redirect(url_for('product_list'))  # Redirige a alguna vista de la lista de productos

