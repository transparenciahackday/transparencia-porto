import couchdbkit
from urllib import urlopen
from BeautifulSoup import BeautifulSoup

db=couchdbkit.Server()['parlamento']

page_formatter='http://www.parlamento.pt/DeputadoGP/Paginas/RegistoInteresses.aspx?BID=%s'


id_NomeCompleto='ctl00_ctl13_g_d22c802e_0a80_4ab1_b44e_335a72b3cc14_ctl00_lblNomeCompleto'
id_ActividadePrincipal='ctl00_ctl13_g_d22c802e_0a80_4ab1_b44e_335a72b3cc14_ctl00_lblActividadePrincipal'
id_EstadoCivil='ctl00_ctl13_g_d22c802e_0a80_4ab1_b44e_335a72b3cc14_ctl00_lblEstadoCivil'
id_NomeConjugue='ctl00_ctl13_g_d22c802e_0a80_4ab1_b44e_335a72b3cc14_ctl00_lblNomeConjuge'
id_RegimeBens='ctl00_ctl13_g_d22c802e_0a80_4ab1_b44e_335a72b3cc14_ctl00_lblRegimeBens'


for each in db.all_docs():
    doc=db.get(each['id'])
    page=urlopen(page_formatter % doc['ar_id']).read()
    soup=BeautifulSoup(page)
    
    print soup.find('span', dict(id=id_ActividadePrincipal)).string,
    print ' - ',
    print doc['profession']
