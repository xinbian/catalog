from flask import Flask, render_template, request, redirect, url_for, flash

app = Flask(__name__)

@app.route('/')
@app.route('/categories')
def showCategoreis():
    return render_template(
        'categories.html')

@app.route('/categories/new')
def newCategories():
    return render_template(
        'newCategories.html')

@app.route('/categories/<int:cate_id>/edit')
def editCategories(cate_id):
    return render_template(
        'editCategories.html')

@app.route('/categories/<int:cate_id>/delete')
def deleteCategories(cate_id):
    return render_template(
        'deleteCategories.html')

@app.route('/categories/<int:cate_id>')
@app.route('/categories/<int:cate_id>/items')
def showCategoriesItem(cate_id):
    return render_template(
        'items.html')

@app.route('/categories/<int:cate_id>/new')
def createCategoriesItem(cate_id):
    return render_template(
        'newCategoriesItem.html')

@app.route('/categories/<int:cate_id>/<int:item_id>/edit')
def editCategoriesItem(cate_id,item_id):
    return render_template(
        'editCategoriesItem.html')

@app.route('/categories/<int:cate_id>/<int:item_id>/delete')
def deleteCategoriesItem(cate_id,item_id):
    return render_template(
        'deleteCategoriesItem.html')

if __name__ == '__main__':
    app.debug = True
    app.run(host='0.0.0.0', port=5000)
