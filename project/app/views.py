from django.shortcuts import render
from lxml import etree
from onelogin.saml2 import utils
import base64
import datetime
import os
# import xmlsec

SAML2_RESPONSE_ISSUER = 'https://dj-sam.aclark.net'
SAML2_RESPONSE_DEST_URL = {
    'absorb': 'https://aclark.myabsorb.com/account/saml',
    'testshib': 'https://sp.testshib.org/Shibboleth.sso/SAML2/POST',
}
SAML2_RESPONSE_PRINCIPAL = 'aclark@aclark.net'

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

PUBLIC_CERT = os.path.join(BASE_DIR, 'certificate.crt')
PRIVATE_KEY = os.path.join(BASE_DIR, 'private.key')

cert = open(PUBLIC_CERT).read()
cert = cert.replace('-----BEGIN CERTIFICATE-----', '')
cert = cert.replace('-----END CERTIFICATE-----', '')
cert = cert.replace('\n', '')
key = open(PRIVATE_KEY).read()

onelogin_saml2_utils = utils.OneLogin_Saml2_Utils()

SAML2_RESPONSE = """
<samlp:Response xmlns:saml="urn:oasis:names:tc:SAML:2.0:assertion" xmlns:samlp="urn:oasis:names:tc:SAML:2.0:protocol" Version="2.0" ID="_979e68dcbc234c9db0067032020f79d9" IssueInstant="2017-05-22T01:25:14Z" Destination="https://aclark.myabsorb.com/account/saml">
  <saml:Issuer>https://dj-sam.aclark.net</saml:Issuer>
  <samlp:Status>
    <samlp:StatusCode Value="urn:oasis:names:tc:SAML:2.0:status:Success"/>
  </samlp:Status>
  <saml:Assertion Version="2.0" ID="_d871123e06e8426e95922b6685af10fc" IssueInstant="2017-05-22T01:25:14Z">
    <saml:Issuer>https://dj-sam.aclark.net</saml:Issuer>
    <Signature xmlns="http://www.w3.org/2000/09/xmldsig#">
<SignedInfo>
<CanonicalizationMethod Algorithm="http://www.w3.org/2001/10/xml-exc-c14n#"/>
<SignatureMethod Algorithm="http://www.w3.org/2000/09/xmldsig#rsa-sha1"/>
<Reference>
<Transforms>
<Transform Algorithm="http://www.w3.org/2000/09/xmldsig#enveloped-signature"/>
</Transforms>
<DigestMethod Algorithm="http://www.w3.org/2000/09/xmldsig#sha1"/>
<DigestValue>sv5e6dir4A+CGEUEKQxUHqDsrO4=</DigestValue>
</Reference>
</SignedInfo>
<SignatureValue>zchFg2oFo0T7FLobbLS1rtBOdxRnaM5z9y2OA6rNRYxhe+744SSkcHsYf8us65ca
QsjOLKT0j1zo/HAn3Ud03b1CI92YBeJ9O4/HMuBPawOYBFE7U7/Yn2wtnU2NVr0m
8ikGMrpZ/2WFaM9lt82k8dco1MPd1REVsFJYg3la6Q8=</SignatureValue>
</Signature>
    <saml:Subject>
      <saml:NameID Format="urn:oasis:names:tc:SAML:2.0:nameid-format:transient">aclark@aclark.net</saml:NameID>
      <saml:SubjectConfirmation Method="urn:oasis:names:tc:SAML:2.0:cm:bearer">
        <saml:SubjectConfirmationData Recipient="https://aclark.myabsorb.com/account/saml"/>
      </saml:SubjectConfirmation>
    </saml:Subject>
    <saml:AuthnStatement AuthnInstant="2017-05-22T01:25:14Z">
      <saml:AuthnContext>
        <saml:AuthnContextClassRef>urn:oasis:names:tc:SAML:2.0:ac:classes:PasswordProtectedTransport</saml:AuthnContextClassRef>
      </saml:AuthnContext>
    </saml:AuthnStatement>
  </saml:Assertion>
</samlp:Response>
"""

def home(request):
    """
    """

    destination = request.GET.get('destination')
    if destination:
        destination = SAML2_RESPONSE_DEST_URL[destination]
    else:
        destination = SAML2_RESPONSE_DEST_URL['absorb']

    response_id = onelogin_saml2_utils.generate_unique_id()
    # https://github.com/jbardin/python-saml/blob/master/saml.py#L101
    issue_instant = datetime.datetime.utcnow().strftime(
        '%Y-%m-%dT%H:%M:%S.%f')[:22]
    assertion_id = onelogin_saml2_utils.generate_unique_id()

#    saml2_response = SAML2_RESPONSE % (response_id, issue_instant,
#                                       assertion_id, issue_instant)
    saml2_response = SAML2_RESPONSE

    # Sign
    root = etree.fromstring(saml2_response)
    # signature_node = xmlsec.tree.find_node(root,
    #                                       xmlsec.constants.NodeSignature)
    # ctx = xmlsec.SignatureContext()
    # key = xmlsec.Key.from_file(PRIVATE_KEY, xmlsec.constants.KeyDataFormatPem)
    # ctx.key = key
    # ctx.sign(signature_node)

    # Pretty, http://stackoverflow.com/a/3974112
    saml2_response = etree.tostring(root, pretty_print=True)

    context = {
        'base64_encoded_saml_response': base64.b64encode(saml2_response),
#        'base64_encoded_saml_response': saml2_response,
#        'base64_encoded_saml_response': onelogin_saml2_utils.deflate_and_base64_encode(saml2_response),
        'saml_response': saml2_response,
        'saml2_response_destination': destination,
    }
    return render(request, 'home.html', context)
