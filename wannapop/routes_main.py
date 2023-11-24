from flask import Blueprint, render_template, redirect, url_for, flash, current_app
from flask_login import current_user, login_required
from .models import Product, Category
from .forms import ProductForm, DeleteForm
from . import db_manager as db
from werkzeug.utils import secure_filename
import uuid
import os
from .helper_role import require_view_permission, require_create_permission, require_edit_permission, require_delete_permission, require_wanner_role

main_bp = Blueprint(
    "main_bp", __name__, template_folder="templates", static_folder="static"
)

@main_bp.route('/')
def init():
    if current_user.is_authenticated:
        return redirect(url_for('main_bp.product_list'))
    else:
        return redirect(url_for("auth_bp.login"))



@main_bp.route('/products/list')
@login_required
@require_view_permission.require(http_exception=403)
def product_list():
    products_with_category = db.session.query(Product, Category).join(Category).order_by(Product.id.asc()).all()
    return render_template('products/list.html', products_with_category = products_with_category)



@main_bp.route('/products/create', methods = ['POST', 'GET'])
@login_required
@require_create_permission.require(http_exception=403)
def product_create(): 
    categories = db.session.query(Category).order_by(Category.id.asc()).all()
    form = ProductForm()
    form.category_id.choices = [(category.id, category.name) for category in categories]
    if form.validate_on_submit():
        new_product = Product()
        new_product.seller_id = None
        form.populate_obj(new_product)
        filename = __manage_photo_file(form.photo_file)
        if filename:
            new_product.photo = filename
        else:
            new_product.photo = "no_image.png"
        db.session.add(new_product)
        db.session.commit()
        flash("Nou producte creat", "success")
        return redirect(url_for('main_bp.product_list'))
    else:
        return render_template('products/create.html', form = form)


@main_bp.route('/products/read/<int:product_id>')
@login_required
@require_view_permission.require(http_exception=403)
def product_read(product_id):
    (product, category) = db.session.query(Product, Category).join(Category).filter(Product.id == product_id).one()
    return render_template('products/read.html', product = product, category = category)



@main_bp.route('/products/update/<int:product_id>', methods=['POST', 'GET'])
@login_required
@require_edit_permission.require(http_exception=403)
def product_update(product_id):
    product = db.session.query(Product).filter(Product.id == product_id).one()
    
    flash(f"current_user.id: {current_user.id}", "info")
    flash(f"product.seller_id: {product.seller_id}", "info")

    # Verificar si el usuario actual es el propietario del producto
    if current_user.id != product.seller_id:
        flash("No tienes permisos para editar este producto.", "error")
        return redirect(url_for('main_bp.product_read', product_id=product_id))

    categories = db.session.query(Category).order_by(Category.id.asc()).all()
    form = ProductForm(obj=product)
    form.category_id.choices = [(category.id, category.name) for category in categories]

    if form.validate_on_submit():
        form.populate_obj(product)
        filename = __manage_photo_file(form.photo_file)
        if filename:
            product.photo = filename
        db.session.add(product)
        db.session.commit()
        flash("Producto actualizado", "success")
        return redirect(url_for('main_bp.product_read', product_id=product_id))

    return render_template('products/update.html', product_id=product_id, form=form)




@main_bp.route('/products/delete/<int:product_id>',methods = ['GET', 'POST'])
@login_required
@require_delete_permission.require(http_exception=403)
def product_delete(product_id):
    product = db.session.query(Product).filter(Product.id == product_id).one()
    form = DeleteForm()
    if form.validate_on_submit():
        db.session.delete(product)
        db.session.commit()
        flash("Producte esborrat", "success")
        return redirect(url_for('main_bp.product_list'))
    else:
        return render_template('products/delete.html', form = form, product = product)

def __manage_photo_file(photo_file):
    if photo_file.data:
        filename = photo_file.data.filename.lower()
        ALLOWED_EXTENSIONS = set(os.getenv('ALLOWED_EXTENSIONS'))
        if any(filename.endswith(ext) for ext in ALLOWED_EXTENSIONS):
            unique_filename = str(uuid.uuid4()) + "-" + secure_filename(filename)
            uploads_folder = current_app.config.get('UPLOAD_FOLDER')
            file_path = os.path.join(uploads_folder, unique_filename)
            photo_file.data.save(file_path)
            return unique_filename
    return None