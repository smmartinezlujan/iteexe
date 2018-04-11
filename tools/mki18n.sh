#!/bin/bash

# ===========================================================================
# eXe
# Copyright 2012-2013, Pedro Peña Pérez, Open Phoenix IT
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 2 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program; if not, write to the Free Software
# Foundation, Inc., 51 Franklin Street, Fifth Floor, Boston, MA  02110-1301, USA.
#
# Help
#-----
# Pybabel doc http://babel.pocoo.org/en/latest/cmdline.html
# Pybabel source https://github.com/python-babel/babel
# Transecma (py2json.py) https://github.com/nandoflorestan/bag/tree/master/bag/web
#
#
# Changes
# -------
# 2013-10:
#     * Usage of Babel1.3 (Pedro Peña)
#         Uses python Babel 1.3 patched to include 'Language' header
#        (https://dl.dropboxusercontent.com/s/k1i7ph2m2g4s7kx/Babel-1.3.tar.gz)
#        as discussed here:
#        https://forja.cenatic.es/tracker/index.php?func=detail&aid=1905&group_id=197&atid=883
#
#    * Changed --version from '1.04.1' to '2.0' (JRF)
#
# 2014-03-17:
#    * Changed options of pybabel update (JRF)
#         trying to fix the duplicate msgstr problem
#         comment the -N option out
#            Option -N, --no-fuzzy-matching: "do not use fuzzy matching" (default False)
#         add --ignore-obsolete
#    * Pybabel compile (JRF)
#         documented that we've never used option -f ("also include fuzzy translations") ¿?
#
# 2015-02-26:
#    * Version 2.0.2 (JRF)
#
# 2015-03-10:
#    * Preparing version 2.1 (JRF)
#
# 2016-05-22
#    * Preparing version 2.1.1 (JRF)
#    * Babel v.2.3.4 (the 'Language' header bug has been fixed and our fork is no longer necessary)
#
# 2017-03-18
#    * Preparing version 2.1.2 (JRF)
#
# 2017-06-24
#    * Preparing version 2.1.3 (JRF)
#    * Babel 2.4.0
#
# 2018-03-04
#    * Preparing version 2.1.4 (JRF)
#
# 2018-04-04
#    * Add template string extraction (Sdweb)
#
#===========================================================================


export PYTHONPATH=.
project="eXeLearning"
version="2.1.4"
tmp=$(mktemp -d)

# 1.- eXe - Extract content templates' files to a .py dummy file
echo -e " *** Extracting messages from content templates ***\n"
python exe/get_template_strings.py --standalone

# 2.- pyBabel - Extraction of strings from *.py and *.js into new POT
echo -e "\n\n\n *** Extracting messages from python exe files, jsui javascript and html template files ***\n"
# pybabel extract --keyword=x_ --keyword=c_ --project "$project" --version "$version" -F pybabel.conf --sort-by-file . > exe/locale/messages.pot
pybabel extract --keyword=x_ --keyword=c_ --project "$project" --version "$version" -F pybabel.conf --sort-by-file . --output="exe/locale/messages.pot"
# tools/nevow-xmlgettext exe/jsui/templates/mainpage.html exe/webui/templates/about.html | msgcat exe/locale/messages.pot.tmp - -o exe/locale/messages.pot
# rm exe/locale/messages.pot.tmp
# Removal of fuzzy comments from the POT file
sed -i "s/^#, fuzzy\$//" exe/locale/messages.pot

# 3.- pyBabel - Updating the PO files of the different languages
echo -e "\n\n\n *** Updating *.po files ***\n"
# JRF's question: is --ignore-obsolete necessary?
# 2018-03-05: parameter removed, let's check the consequences
# pybabel update -D exe -i exe/locale/messages.pot -d exe/locale/ --ignore-obsolete
pybabel update -D exe -i exe/locale/messages.pot -d exe/locale/
# Set correct Project-Id-Version
find exe -name exe.po | xargs sed -i 's/Project-Id-Version:.*/Project-Id-Version: '"$project $version"'\\n"/'

# 4 .- eXe - Update temp locale files with templates translations
echo -e "\n\n\n *** Adding template strings to generated *.po files ***\n"
cp -r exe/locale $tmp
python exe/put_template_strings.py --standalone $tmp/locale

# pybabel bugs fixing
find exe -name exe.po | xargs sed -i 'N;N;/#~ msgid ""\n#~ msgstr ""/d' # Clean wrong commented msgids
find $tmp -name exe.po | xargs sed -i 'N;N;/#~ msgid ""\n#~ msgstr ""/d' # Clean wrong commented msgids
find exe -name exe.po | xargs sed -i '1!N;1!N;/#~ msgid ""\n#~ msgstr ""/d' # Clean wrong commented msgids
find $tmp -name exe.po | xargs sed -i '1!N;1!N;/#~ msgid ""\n#~ msgstr ""/d' # Clean wrong commented msgids

# 5.- pyBabel - Compiling the MO files
echo -e "\n\n\n *** Compiling *.mo files ***\n"
pybabel compile -D exe -d $tmp/locale --statistics
find exe/locale -name exe.mo -delete
cp -r $tmp/locale exe -n -v

# 6.- Transecma - Generating the translated JS files for the different languages
echo -e "\n\n\n *** Compiling javascript for jsui files ***\n"
python tools/po2json.py --domain exe --directory exe/locale --output-dir exe/jsui/scripts/i18n

# Remove temp dir
rm -r $tmp
