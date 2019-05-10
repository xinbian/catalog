from flask import Flask, render_template, request, redirect, url_for, flash
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from database_setup import Base, Department, DepartmentItem

app = Flask(__name__)

engine = create_engine('sqlite:///supermarketitems.db', 
    connect_args={'check_same_thread': False})
Base.metadata.bind = engine

DBSession = sessionmaker(bind=engine)
session = DBSession()

@app.route('/')
@app.route('/catalogs')
def showCategoreis():
    departments = session.query(Department).all()
    items = session.query(DepartmentItem).all()
    return render_template(
        'catalogs.html',
        catalogs = departments,
        items = items)


@app.route('/catalogs/new')
def newCatalogs():
    return render_template(
        'newCatalogs.html')


@app.route('/catalogs/<int:cata_id>/edit')
def editCatalogs(cata_id):
    return render_template(
        'editCatalogs.html')


@app.route('/catalogs/<int:cata_id>/delete')
def deleteCatalogs(cata_id):
    return render_template(
        'deleteCatalogs.html')


@app.route('/catalogs/<int:cata_id>')
@app.route('/catalogs/<int:cata_id>/items')
def showCatalogsItem(cata_id):
    departments = session.query(Department).all()
    department = session.query(Department).filter_by(id=cata_id).one()
    items = session.query(DepartmentItem).filter_by(department_id=department.id)
    return render_template(
        'cataItem.html',
        catalogs = departments,
        catalog = department,
        items = items)


@app.route('/catalogs/<int:cata_id>/items/new')
def createCatalogsItem(cata_id):
    return render_template(
        'newCatalogsItem.html')


@app.route('/catalogs/<int:cata_id>/items/<int:item_id>/edit')
def editCatalogsItem(cata_id, item_id):
    return render_template(
        'editCatalogsItem.html')


@app.route('/catalogs/<int:cata_id>/items/<int:item_id>/delete')
def deleteCatalogsItem(cata_id, item_id):
    return render_template(
        'deleteCatalogsItem.html')


if __name__ == '__main__':
    app.debug = True
    app.run(host='0.0.0.0', port=5000)
