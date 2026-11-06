# Fichier modifié par Siadeo (2026) par rapport à python-en16931 (Invinet Sistemes, Apache-2.0). Voir en16931/NOTICE.
import pytest

from en16931.bank_info import BankInfo
from en16931.entity import Entity
from en16931.postal_address import PostalAddress


class TestEntity:

    def test_initialization(self):
        e = Entity(name="Acme Inc.", tax_scheme="VAT",
                   tax_scheme_id="ES34626691F", country="ES",
                   party_legal_entity_id="ES34626691F",
                   registration_name="Acme INc.", mail="acme@acme.io",
                   endpoint="ES76281415Y", endpoint_scheme="ES:VAT",
                   address="easy street", address2="3rd floor", postalzone="08080",
                   city="Barcelona", province="Barcelona")
        assert e.is_valid()
        assert e.tax_scheme == "VAT"
        assert e.tax_scheme_id == "ES34626691F"
        assert e.endpoint == "ES76281415Y"
        assert e.registration_name == "Acme INc."

    def test_unsuported_tax_scheme(self):
        e = Entity()
        with pytest.raises(ValueError):
            e.tax_scheme = "ASF"

    def test_not_apostal_address(self):
        e = Entity()
        with pytest.raises(TypeError):
            e.postal_address = "some address"

    def test_invalid_entity(self):
        e = Entity(name="Asdf Inc.")
        assert not e.is_valid()

    def test_valid_entity(self):
        e = Entity()
        e.name = "Acme Inc."
        e.tax_scheme = "VAT"
        e.tax_scheme_id = "ES34626691F"
        e.country = "ES"
        e.party_legal_entity_id = "ES34626691F"
        e.registration_name = "Acme INc."
        e.endpoint = "ES76281415Y"
        e.endpoint_scheme = "ES:VAT"
        p = PostalAddress(address="easy street", address2="3rd floor", city_name="Barcelona",
                          postal_zone="08080", country="ES", province="Barcelona")
        e.postal_address = p
        assert e.is_valid()
        assert e.tax_scheme == "VAT"
        assert e.tax_scheme_id == "ES34626691F"
        assert e.endpoint == "ES76281415Y"
        assert e.registration_name == "Acme INc."

    def test_bank_info(self):
        seller = Entity(name="Acme Inc.", tax_scheme="VAT",
                        tax_scheme_id="ES34626691F", country="ES",
                        party_legal_entity_id="ES34626691F",
                        registration_name="Acme INc.", mail="acme@acme.io",
                        endpoint="ES76281415Y", endpoint_scheme="ES:VAT",
                        address="easy street", address2="3rd floor", postalzone="08080",
                        city="Barcelona", province="Barcelona")
        bank_info_seller = BankInfo(iban="ES661234563156", bic="AAAABBCCDDD")
        seller.bank_info = bank_info_seller
        assert seller.is_valid()
        assert seller.bank_info.iban == "ES661234563156"
        assert seller.bank_info.bic == "AAAABBCCDDD"

    def test_invalid_bank_info(self):
        e = Entity()
        with pytest.raises(ValueError):
            e.bank_info = BankInfo()

    def test_wrong_bank_info(self):
        e = Entity()
        with pytest.raises(TypeError):
            e.bank_info = "asdf"


class TestEntityVat:

    @pytest.mark.parametrize("siret, expected", [
        ("82539508000021", "FR01825395080"),
        ("53800624800016", "FR60538006248"),
    ])
    def test_expected_vat(self, siret, expected):
        assert Entity(party_legal_entity_id=siret).expected_vat == expected

    def test_expected_vat_without_siren(self):
        assert Entity().expected_vat is None

    @pytest.mark.parametrize("vat, siret, matches", [
        ("FR01825395080", "82539508000021", True),
        ("FR32123456789", "82539508000021", False),
        ("FR60538006248", "53800624800016", True),
        ("FR01 825 395 080", "82539508000021", True),
        ("fr01825395080", "82539508000021", True),
        ("FR02825395080", "82539508000021", False),
        ("FRAB825395080", "82539508000021", True),
        ("FRAB123456789", "82539508000021", False),
        ("ES34626691F", "ES34626691F", True),
        ("FR01825395080", None, True),
        (None, "82539508000021", True),
    ])
    def test_vat_matches_siren(self, vat, siret, matches):
        e = Entity(tax_scheme_id=vat, party_legal_entity_id=siret)
        assert e.vat_matches_siren() is matches
