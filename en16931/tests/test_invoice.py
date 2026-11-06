# Fichier modifié par Siadeo (2026) par rapport à python-en16931 (Invinet Sistemes, Apache-2.0). Voir en16931/NOTICE.
import os
import pytest
from datetime import datetime
from decimal import Decimal

from en16931.entity import Entity
from en16931.invoice import Invoice
from en16931.invoice_line import InvoiceLine
from en16931.tax import Tax
from facturx import get_level, xml_check_schematron, xml_check_xsd
from lxml import etree
from models.facture import Facture


class TestInvoiceAttributes:

    def test_default_id_number(self):
        i = Invoice()
        assert i.invoice_id == '1'

    def test_id_number(self):
        i = Invoice(invoice_id="1-2018")
        assert i.invoice_id == "1-2018"

    def test_set_issue_date(self):
        dts = {
            "2018-09-11": "%Y-%m-%d",
            "20180911": "%Y%m%d",
            "21-06-2018": "%d-%m-%Y",
            "2018/12/12": "%Y/%m/%d",
            "12/12/2018": "%d/%m/%Y",
        }
        i = Invoice()
        for date, fmt in dts.items():
            i.issue_date = date
            assert i.issue_date.strftime(fmt) == date

    def test_set_dates_none(self):
        i = Invoice()
        i.issue_date = None
        assert i.issue_date is None
        i.due_date = None
        assert i.due_date is None

    def test_set_dates_datetime(self):
        i = Invoice()
        i.issue_date = datetime(2018, 7, 10)
        assert i.issue_date == datetime(2018, 7, 10).strftime("%Y%m%d")
        i.due_date = datetime(2018, 9, 10)
        assert i.due_date == datetime(2018, 9, 10).strftime("%Y%m%d")

    def test_wrong_issue_date(self):
        with pytest.raises(ValueError):
            i = Invoice()
            i.issue_date = "asdef"
        with pytest.raises(ValueError):
            i = Invoice()
            i.issue_date = 123

    def test_set_due_date(self):
        dts = {
            "2018-09-11": "%Y-%m-%d",
            "20180911": "%Y%m%d",
            "21-06-2018": "%d-%m-%Y",
            "2018/12/12": "%Y/%m/%d",
            "12/12/2018": "%d/%m/%Y",
        }
        i = Invoice()
        for date, fmt in dts.items():
            i.due_date = date
            assert i.due_date.strftime(fmt) == date

    def test_wrong_due_date(self):
        with pytest.raises(ValueError):
            i = Invoice()
            i.due_date = "asdef"
        with pytest.raises(ValueError):
            i = Invoice()
            i.due_date = 123

    def test_invalid_currency(self):
        with pytest.raises(KeyError):
            i = Invoice()
            i.currency = "asdef"

    def test_wrong_seller_entity(self):
        with pytest.raises(TypeError):
            i = Invoice()
            i.seller_party = 123
        with pytest.raises(ValueError):
            i = Invoice()
            i.seller_party = Entity()

    def test_wrong_buyer_entity(self):
        with pytest.raises(TypeError):
            i = Invoice()
            i.buyer_party = 123
        with pytest.raises(ValueError):
            i = Invoice()
            i.buyer_party = Entity()

    def test_invalid_payment_code(self):
        with pytest.raises(ValueError):
            i = Invoice()
            i.payment_means_code = "asdef"

    def test_payment_code(self):
            i = Invoice()
            i.payment_means_code = "10"
            assert i.payment_means_code == "10"


class TestInvoiceOperations:

    def test_unique_taxes(self, invoice1, tax1, tax2):
        assert len(invoice1.unique_taxes) == 2
        assert invoice1.unique_taxes == {tax1, tax2}

    def test_lines_with_taxes(self, invoice1, tax1, tax2):
        assert len(list(invoice1.lines_with_taxes(tax_type=tax1))) == 2
        assert len(list(invoice1.lines_with_taxes(tax_type=tax2))) == 1

    def test_tax_amount(self, invoice1, tax1, tax2):
        assert str(invoice1.tax_amount()) == '16.62'
        assert str(invoice1.tax_amount(tax_type=tax1)) == '15.12'
        assert str(invoice1.tax_amount(tax_type=tax2)) == '1.50'

    def test_taxable_base(self, invoice1, tax1, tax2):
        assert str(invoice1.taxable_base()) == '87.00'
        assert str(invoice1.taxable_base(tax_type=tax1)) == '72.00'
        assert str(invoice1.taxable_base(tax_type=tax2)) == '15.00'

    def test_gross_subtotal(self, invoice1):
        assert str(invoice1.gross_subtotal()) == '87.00'

    def test_subtotal(self, invoice1):
        assert str(invoice1.gross_subtotal()) == '87.00'

    def test_total(self, invoice1):
        assert str(invoice1.total()) == '103.62'

    def test_line_extension_amount(self, invoice1):
        assert str(invoice1.line_extension_amount) == '87.00'

    def test_tax_exclusive_amount(self, invoice1):
        assert str(invoice1.tax_exclusive_amount) == '87.00'

    def test_tax_inclusive_amount(self, invoice1):
        assert str(invoice1.tax_inclusive_amount) == '103.62'

    def test_payable_amount(self, invoice1):
        assert str(invoice1.payable_amount) == '103.62'

    def test_charge_amount(self, invoice1):
        assert str(invoice1.charge_amount) == '0.00'
        invoice1.charge_amount = 10
        assert str(invoice1.charge_amount) == '10.00'
        assert str(invoice1.subtotal()) == '97.00'

    def test_discount_amount(self, invoice1):
        assert str(invoice1.discount_amount) == '0.00'
        invoice1.discount_amount = 10
        assert str(invoice1.discount_amount) == '10.00'
        assert str(invoice1.subtotal()) == '77.00'

    def test_charge_percent(self, invoice1):
        invoice1.charge_percent = 10
        assert str(invoice1.charge_percent) == '0.1'
        assert str(invoice1.charge_amount) == '8.70'
        assert str(invoice1.subtotal()) == '95.70'

    def test_discount_percent(self, invoice1):
        invoice1.discount_percent = 10
        assert str(invoice1.discount_percent) == '0.1'
        assert str(invoice1.discount_amount) == '8.70'
        assert str(invoice1.subtotal()) == '78.30'



class TestInvoiceXMLGeneration:

    def test_generates_xml_invoice1(self, invoice1):
        out = invoice1.to_xml()
        assert len(out) > 0

    def test_generates_xml_invoice2(self, invoice2):
        out = invoice2.to_xml()
        assert len(out) > 0

    def test_generates_xml_invoice3(self, invoice3):
        out = invoice3.to_xml()
        assert len(out) > 0

    def test_generates_xml_custom_invoice(self, custom_invoice):
        out = custom_invoice.to_xml()
        assert len(out) > 0

    def test_writes_xml_file_invoice1(self, invoice1):
        path = '/tmp/invoice1.xml'
        invoice1.save(path)
        assert os.path.exists(path)

    def test_writes_xml_file_invoice2_with_discount_and_charge(self, invoice2):
        path = '/tmp/invoice2.xml'
        invoice2.save(path)
        assert os.path.exists(path)

    def test_writes_xml_file_invoice3_with_payment_means(self, invoice3):
        path = '/tmp/invoice3.xml'
        invoice3.save(path)
        assert os.path.exists(path)

    def test_writes_xml_file_custom_invoice(self, custom_invoice):
        path = '/tmp/custom_invoice.xml'
        custom_invoice.save(path)
        assert os.path.exists(path)


def _party(name, siret, vat, country="FR"):
    return Entity(name=name, tax_scheme="VAT", tax_scheme_id=vat, country=country,
                  party_legal_entity_id=siret, registration_name=name,
                  mail="contact@example.com", address="1 rue de la Paix",
                  postalzone="75001", city="Paris")


def _facture(discount=None, buyer=None):
    facture = Facture(invoice_id="FAC-1", invoice_type_code="380", profile_id="B4")
    facture.seller_party = _party("Vendeur", "53800624800016", "FR60538006248")
    facture.buyer_party = buyer or _party("Acheteur", "82539508000021", "FR01825395080")
    date = datetime(2026, 11, 6)
    facture.issue_date = facture.delivery_date = facture.due_date = date
    facture.add_lines_from([InvoiceLine(
        quantity=2, unit_code="EA", price=490, item_name="Article", currency="EUR",
        tax_category="S", tax_percent=0.055, tax_name="S0.055", discount=discount)])
    facture.paid_amount = 0
    facture.payable_amount = str(facture.tax_inclusive_amount)
    facture.notes = [{"code": code, "content": f"Mention {code}"}
                     for code in ("PMD", "PMT", "AAB", "REG", "ABL")]
    return facture


class TestFacturxXml:

    def test_profile_en16931(self):
        xml = _facture().to_xml()
        assert "<ram:ID>urn:cen.eu:en16931:2017</ram:ID>" in xml
        assert "urn:factur-x.eu:1p0:basic" not in xml

    def test_electronic_address_uses_siren(self):
        xml = _facture().to_xml()
        assert '<ram:URIID schemeID="0225">538006248</ram:URIID>' in xml
        assert '<ram:URIID schemeID="0225">825395080</ram:URIID>' in xml
        assert 'schemeID="EM"' not in xml

    def test_foreign_buyer_keeps_mail(self):
        buyer = _party("Buyer", "ES34626691F", "ES34626691F", country="ES")
        buyer.party_legal_entity_id = "123456789012"
        xml = _facture(buyer=buyer).to_xml()
        assert '<ram:URIID schemeID="EM">contact@example.com</ram:URIID>' in xml
        assert '<ram:URIID schemeID="0225">123456789</ram:URIID>' not in xml

    def test_discount_reason_code(self):
        xml = _facture(discount=10).to_xml()
        assert "<ram:ReasonCode>95</ram:ReasonCode>" in xml

    @pytest.mark.parametrize("discount", [None, 10])
    def test_valid_against_xsd_and_schematrons(self, discount):
        xml = _facture(discount=discount).to_xml().encode("utf-8")
        assert get_level(etree.fromstring(xml), "factur-x") == "en16931"
        assert xml_check_xsd(xml)
        assert xml_check_schematron(xml, check_option="fr-ctc")
