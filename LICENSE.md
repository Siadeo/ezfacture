# Licence

Copyright (c) 2026 Siadeo

Distribué sous licence Apache, version 2.0 (la « Licence ») ; vous ne pouvez utiliser ce fichier que dans le respect des conditions de la Licence. Le texte intégral de la Licence se trouve dans le fichier [LICENSE](LICENSE) et à l'adresse

   https://www.apache.org/licenses/LICENSE-2.0

Sauf disposition légale applicable ou accord écrit, le logiciel distribué sous la Licence est fourni « EN L'ÉTAT », SANS GARANTIE NI CONDITION D'AUCUNE SORTE, expresse ou implicite. Consultez la Licence pour connaître les termes régissant les autorisations et les limitations qui en découlent.

---

## Code tiers intégré au dépôt

| Composant | Emplacement | Licence |
|---|---|---|
| [python-en16931](https://github.com/invinet/python-en16931), Copyright (C) 2018 Invinet Sistemes, **version modifiée** | [en16931/](en16931/) | Apache-2.0, voir [en16931/LICENSE.txt](en16931/LICENSE.txt) ; modifications listées dans [en16931/NOTICE](en16931/NOTICE) |
| [Règles de validation EN 16931](https://github.com/ConnectingEurope/eInvoicing-EN16931), non modifiées | [validate/EN16931-UBL-validation.xslt](validate/EN16931-UBL-validation.xslt) | EUPL-1.2, voir [validate/LICENSE-EUPL-1.2.txt](validate/LICENSE-EUPL-1.2.txt) |

Ce fichier XSLT reste sous EUPL-1.2 ; la licence Apache du projet ne s'y applique pas. Il n'est pas inclus dans l'exécutable.

## Licences tierces

Ce projet utilise les composants tiers suivants, chacun distribué sous sa propre licence.

Les textes de licence des composants inclus dans l'exécutable sont réunis dans [THIRD_PARTY_LICENSES.txt](THIRD_PARTY_LICENSES.txt), fourni avec le dépôt et avec l'exécutable. La liste complète s'y trouve.

| Composant | Licence |
|---|---|
| [CustomTkinter](https://github.com/TomSchimansky/CustomTkinter) | MIT |
| [packaging](https://github.com/pypa/packaging) | Apache-2.0 OU BSD-2-Clause |
| [pywin32](https://github.com/mhammond/pywin32) | Licence Python Software Foundation (PSF) |
| [xlwings](https://github.com/xlwings/xlwings) | BSD-3-Clause (hors sous-paquet `xlwings.pro`, exclu de l'exécutable) |
| [Requests](https://github.com/psf/requests) | Apache-2.0 |
| [lxml](https://github.com/lxml/lxml) | BSD-3-Clause |
| [saxonche (SaxonC-HE)](https://www.saxonica.com/saxon-c/index.xml) | Édition open source de Saxonica ; le paquet n'indique pas de licence. Saxon-HE est sous MPL-2.0 |
| [Jinja2](https://github.com/pallets/jinja) | BSD-3-Clause |
| [py-money](https://github.com/vimeo/py-money) | MIT |
| [factur-x](https://github.com/akretion/factur-x) | BSD-3-Clause |
| [pikepdf](https://github.com/pikepdf/pikepdf) | MPL-2.0 |
| [pypdf](https://github.com/py-pdf/pypdf) | BSD-3-Clause |
| [python-stdnum](https://github.com/arthurdejong/python-stdnum) | LGPL-2.1-or-later |
| [certifi](https://github.com/certifi/python-certifi) | MPL-2.0 |
| [pandas](https://github.com/pandas-dev/pandas) | BSD-3-Clause |
| [NumPy](https://github.com/numpy/numpy) | BSD-3-Clause et licences de ses composants |
| [Pillow](https://github.com/python-pillow/Pillow) | MIT-CMU |
| [openpyxl](https://foss.heptapod.net/openpyxl/openpyxl) | MIT |
| [Babel](https://github.com/python-babel/babel) | BSD-3-Clause |
| [Python](https://www.python.org/) et Tcl/Tk | Licence PSF et licences de ses composants |
| Polices Roboto (fournies avec CustomTkinter) | Apache-2.0 |
| Schémas et règles fournis avec factur-x | Selon les fichiers : notices UN/CEFACT, OASIS et W3C, EUPL-1.2 |
| [PyInstaller](https://github.com/pyinstaller/pyinstaller) | GPL-2.0-or-later avec exception pour l'exécutable généré (outil de compilation) |

## Code source des composants sous licence à réciprocité

pikepdf, certifi (MPL-2.0) et python-stdnum (LGPL) sont inclus dans l'exécutable sans modification. Leur code source est disponible aux adresses indiquées ci-dessus.

Le code source d'EzFacture étant public, vous pouvez recompiler l'exécutable avec une version modifiée de ces composants en suivant les instructions de compilation du [readme](readme.md).
