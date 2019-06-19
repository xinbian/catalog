# Project: Catalog APP
## Project description
A web application is developed, which provides a list of items within a variety of categories as well as provide a user registration and authentication system. Registered users will have the ability to post, edit and delete their own items.

## How to Run
### Requirements
[Python 2](https://www.python.org), [Vagrant](https://www.vagrantup.com/), [VirtualBox](https://www.virtualbox.org/)
### Run the code
1. install the above software/environment
2. clone the repo
3. download vagrant configurations [VMsetting](https://d17h27t6h515a5.cloudfront.net/topher/2017/August/59822701_fsnd-virtual-machine/fsnd-virtual-machine.zip)
4. lancuh virtual machine back online (with `vagrant up`) and log into it with `vagrant ssh`.
5. initlize database by `python database_setup.py`
6. fill initial data by `python initItems.py`
7. start the sever by `python application.py`
8. open the  [web page](http://localhost:5000/)
### JSON API
JSON API is provided at:
http://localhost:5000/catalogs/JSON
http://localhost:5000/catalogs/<int:cata_id>/items/JSON
http://localhost:5000/catalogs/<int:cata_id>/items/<int:item_id>/JSON