#
#    ICRAR - International Centre for Radio Astronomy Research
#    (c) UWA - The University of Western Australia, 2016
#    Copyright by UWA (in the framework of the ICRAR)
#    All rights reserved
#
#    This library is free software; you can redistribute it and/or
#    modify it under the terms of the GNU Lesser General Public
#    License as published by the Free Software Foundation; either
#    version 2.1 of the License, or (at your option) any later version.
#
#    This library is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the GNU
#    Lesser General Public License for more details.
#
#    You should have received a copy of the GNU Lesser General Public
#    License along with this library; if not, write to the Free Software
#    Foundation, Inc., 59 Temple Place, Suite 330, Boston,
#    MA 02111-1307  USA
#
"""
Main module where application-specific tasks are carried out, like copying its
sources, installing it and making sure it works after starting it.

NOTE: This requires modifications for the specific application where this
fabfile is used. Please make sure not to use it without those modifications.
"""
import os, sys
from fabric.state import env
from fabric.colors import red
from fabric.operations import local, put
from fabric.decorators import task, parallel
from fabric.context_managers import settings, cd
from fabric.contrib.files import exists, sed
from fabric.utils import abort
from fabric.contrib.console import confirm
# import urllib2

# >>> All the settings below are kept in the special fabric environment
# >>> dictionary called env. Don't change the names, only adjust the
# >>> values if necessary. The most important one is env.APP.

# The following variable will define the Application name as well as directory
# structure and a number of other application specific names.
env.APP_NAME = 'NGAS_PORTAL'

# The username to use by default on remote hosts where APP is being installed
# This user might be different from the initial username used to connect to the
# remote host, in which case it will be created first
env.APP_USER = env.APP_NAME.lower()

# Name of the directory where APP sources will be expanded on the target host
# This is relative to the APP_USER home directory
env.APP_SRC_DIR_NAME = env.APP_NAME.lower() + '_src'

# Name of the directory where APP root directory will be created
# This is relative to the APP_USER home directory
env.APP_ROOT_DIR_NAME = env.APP_NAME.upper()

# Name of the directory where a virtualenv will be created to host the APP
# software installation, plus the installation of all its related software
# This is relative to the APP_USER home directory
env.APP_INSTALL_DIR_NAME = env.APP_NAME.lower() + '_rt'

# Version of Python required for the Application
env.APP_PYTHON_VERSION = '2.7'

# URL to download the correct Python version
env.APP_PYTHON_URL = 'https://www.python.org/ftp/python/2.7.14/Python-2.7.14.tgz'

env.APP_DATAFILES = []
# >>> The following settings are only used within this APPspecific file, but may be
# >>> passed in through the fab command line as well, which will overwrite the 
# >>> defaults below.

defaults = {}

### >>> The following settings need to reflect your AWS environment settings.
### >>> Please refer to the AWS API documentation to see how this is working
### >>> 
## AWS user specific settings
env.AWS_PROFILE = 'NGAS'
env.AWS_KEY_NAME = 'icrar_{0}'.format(env.APP_USER)

# These AWS settings are generic and should work for any user, but please make
# sure that the instance_type is appropriate.
env.AWS_INSTANCE_TYPE = 't1.micro'
env.AWS_REGION = 'us-east-1'
env.AWS_AMI_NAME = 'Amazon'
env.AWS_INSTANCES = 1
env.AWS_SEC_GROUP = env.APP_NAME.upper() # Security group allows SSH and other ports
env.AWS_SEC_GROUP_PORTS = [22, 80, 7777, 8888] # ports to open
env.AWS_SUDO_USER = 'ec2-user' # required to install init scripts.

ZOPE_URL = 'https://zopefoundation.github.io/Zope/releases/2.13.27/requirements.txt'


# Alpha-sorted packages per package manager
env.pkgs = {
            'YUM_PACKAGES': [
                'autoconf',
                'python27-devel',
                'git',
                'readline-devel',
                'sqlite-devel',
                'make',
                'wget.x86_64',
                'gcc',
                'patch',
                'postgresql9-devel.x86_64',
                      ],
            'APT_PACKAGES': [
                    'tar',
                    'wget',
                    'gcc',
                    ],
            'SLES_PACKAGES': [
                    'wget',
                    'gcc',
                    ],
            'BREW_PACKAGES': [
                    'wget',
                    'gcc',
                    ],
            'PORT_PACKAGES': [
                    'wget',
                    'gcc',
                    ],
            'APP_EXTRA_PYTHON_PACKAGES': [
                    ],
        }

# Don't re-export the tasks imported from other modules, only the ones defined
# here
__all__ = [
    'cleanup',
]

# Set the rpository root to be relative to the location of this file.
env.APP_repo_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))

# >>> The following lines need to be after the definitions above!!!
from fabfileTemplate.utils import sudo, info, success, default_if_empty, home, run
from fabfileTemplate.utils import overwrite_defaults, failure
from fabfileTemplate.system import check_command, get_linux_flavor, MACPORT_DIR
from fabfileTemplate.APPcommon import virtualenv, APP_doc_dependencies, APP_source_dir, APP_install_dir
from fabfileTemplate.APPcommon import APP_root_dir, extra_python_packages, APP_user, build
from fabfileTemplate.pkgmgr import check_brew_port, check_brew_cellar

# get the settings from the fab environment if set on command line
settings = overwrite_defaults(defaults)

def start_APP_and_check_status():
    """
    Starts the APP daemon process and checks that the server is up and running
    then it shuts down the server
    """
    ###>>> 
    # Provide the actual implementation here if required.
    ###<<<
    success('{0} help is working...'.format(env.APP_NAME))

def sysinitstart_APP_and_check_status():
    """
    Starts the APP daemon process and checks that the server is up and running
    then it shuts down the server
    """
    ###>>> 
    # Provide the actual implementation here if required.
    ###<<<
    pass

def APP_build_cmd():

    # The installation of the bsddb package (needed by ngamsCore) is in
    # particular difficult because it requires some flags to be passed on
    # (particularly if using MacOSX's port
    # >>>> NOTE: This function potentially needs heavy customisation <<<<<<
    build_cmd = []
    # linux_flavor = get_linux_flavor()

    ###>>> 
    # Provide the actual implementation here if required.
    ###<<<

    return ' '.join(build_cmd)


def build_APP():
    """
    Builds and installs APP into the target virtualenv.
    """
    with cd(APP_source_dir()):
        develop = False
        no_doc_dependencies = APP_doc_dependencies()
        build_cmd = APP_build_cmd()
        print(build_cmd)
        if build_cmd != '':
            virtualenv(build_cmd)

    with cd(APP_install_dir()):
        virtualenv('pip install --no-binary zc.recipe.egg -r {0}'.format(ZOPE_URL))
        # virtualenv('pip install -U zope.interface')
        virtualenv('pip install Products.ExternalMethod')
        virtualenv('pip install Products.PythonScripts')
        virtualenv('pip install Products.ZSQLMethods==2.13.5')
#        virtualenv('easy_install Products.SQLAlchemyDA')
        virtualenv('pip install psycopg2-binary')
        virtualenv('mkzopeinstance -d {0}/ngas -u {1}:{2}'.format(APP_install_dir(), 'admin','admin4zope'))
        with cd('/tmp'):
            virtualenv('git clone https://github.com/zopefoundation/Products.SQLAlchemyDA.git SQLAlchemyDA')
            virtualenv('cd SQLAlchemyDA; python setup.py install')


def prepare_APP_data_dir():
    """Creates a new APP root directory"""
    """
    Install the content of the NGAS portal
    """
    if not exists('{0}/ngas/import/'.format(APP_install_dir())):
        run('mkdir {0}/ngas/import/'.format(APP_install_dir()),
            warn_only=True)
    put('data/*.zexp', '{0}/ngas/import/'.format(APP_install_dir()))
    if not exists('{0}/../NGAS'.format(APP_install_dir())):
        run('mkdir NGAS', warn_only=True)
    if not exists('{0}/../NGAS/ngas.sqlite'.format(APP_install_dir())):
        put('data/ngas.sqlite', '{0}/../NGAS/'.format(APP_install_dir()))

def install_sysv_init_script(nsd, nuser, cfgfile):
    """
    Install the APP init script for an operational deployment.
    The init script is an old System V init system.
    In the presence of a systemd-enabled system we use the update-rc.d tool
    to enable the script as part of systemd (instead of the System V chkconfig
    tool which we use instead). The script is prepared to deal with both tools.
    """
    ###>>> 
    # Provide the actual implementation here if required.
    ###<<<

    success("{0} init script installed".format(env.APP_NAME))

@task
@parallel
def cleanup():
    ###>>> 
    # Provide the actual implementation here if required.
    ###<<<
    pass

def extra_sudo():
    ###>>> 
    # Provide the actual implementation here if required.
    ###<<<
    pass

def install_docker_compose():
    pass

env.build_cmd = APP_build_cmd
env.build_function = build_APP
env.APP_init_install_function = install_sysv_init_script
env.APP_start_check_function = start_APP_and_check_status
env.sysinitAPP_start_check_function = sysinitstart_APP_and_check_status
env.prepare_APP_data_dir = prepare_APP_data_dir
env.APP_extra_sudo_function = install_docker_compose
