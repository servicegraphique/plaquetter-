"""Adapt only pages 3, 4, 5, 6 and 7 of the supplied HelloLead PDF.
Run with PyMuPDF installed: python scripts/create_touchscreen_brochure.py
All example companies and contact details below are fictional.
"""
from pathlib import Path
import pymupdf as pdf

ROOT = Path(__file__).resolve().parent.parent
SOURCE = ROOT / 'Plaquette HelloLead - Panneaux solaires - Corrigee (2).pdf'
OUTPUT = ROOT / 'Plaquette HelloLead - Caisses enregistreuses tactiles.pdf'
(ROOT / '.cache').mkdir(exist_ok=True)
DOC = pdf.open(SOURCE)
BLUE = (0.02, 0.34, 1)
BG = (0.957, 0.957, 0.984)
INK = (0.10, 0.17, 0.25)
WHITE = (1, 1, 1)
MUTED = (.40, .45, .52)
LIGHT = (.92, .95, .98)
FONTS = {name: DOC.extract_font(xref)[3] for name, xref in [('reg', 219), ('bold', 225)]}

def setup(p):
    for name, data in FONTS.items():
        p.insert_font(fontname=name, fontbuffer=data)

def rect(p, box, fill, stroke=None, radius=0):
    p.draw_rect(pdf.Rect(box), color=stroke, fill=fill, width=.7, radius=radius or None)

def text(p, x, y, w, value, size=13, bold=False, color=INK, h=None, align=0):
    h = h or (size * 1.6 * (value.count('\n') + 2))
    result = p.insert_textbox(pdf.Rect(x, y, x+w, y+h), value,
                             fontname='bold' if bold else 'reg', fontsize=size,
                             color=color, lineheight=1.28, align=align)
    if result < 0:
        raise ValueError(f'Text does not fit: {value!r}')

def button(p, x, y, w, label, size=12):
    rect(p, (x, y, x+w, y+32), BLUE, radius=.15)
    text(p, x+5, y+6, w-10, label, size, True, WHITE, h=25, align=1)

def field(p, x, y, w, label, value='Sélectionner', size=12):
    text(p, x, y, w, label, size, True)
    rect(p, (x, y+27, x+w, y+60), WHITE, (.80,.84,.89), .1)
    text(p, x+10, y+33, w-20, value, size-1, color=MUTED)

def pos(p, x, y, w, h, scene='commerce'):
    """Place a generated photorealistic asset, center-cropped without distortion."""
    image = ROOT / 'assets' / f'caisse-tactile-{scene}.jpg'
    pix = pdf.Pixmap(str(image))
    source_ratio = pix.width / pix.height
    target_ratio = w / h
    # Fill the frame while preserving the photograph's proportions.
    if source_ratio > target_ratio:
        crop_width = pix.height * target_ratio
        crop = pdf.IRect((pix.width-crop_width)/2, 0,
                         (pix.width+crop_width)/2, pix.height)
    else:
        crop_height = pix.width / target_ratio
        crop = pdf.IRect(0, (pix.height-crop_height)/2,
                         pix.width, (pix.height+crop_height)/2)
    cropped = pdf.Pixmap(pix.colorspace, crop, pix.alpha)
    cropped.copy(pix, crop)
    p.insert_image(pdf.Rect(x,y,x+w,y+h), pixmap=cropped)

def clear(p, boxes):
    for box, color in boxes:
        p.add_redact_annot(pdf.Rect(box), fill=color)
    p.apply_redactions(images=2, graphics=0)
    setup(p)

def lead(p, x, y, w, pairs, company, activity, city, postcode, size=13, gap=5):
    for label, value in pairs:
        text(p,x,y,w,label,size,True,BLUE)
        lines = max(1, int((pdf.Font(fontbuffer=FONTS['bold']).text_length(label, fontsize=size)-1)//w)+1)
        y += size*1.28*lines+3
        text(p,x,y,w,value,size)
        lines = max(1,int((pdf.Font(fontbuffer=FONTS['reg']).text_length(value, fontsize=size)-1)//w)+1)
        y += size*1.28*lines+gap
    y += 15
    contact = f'Entreprise : {company}\nExemple fictif · Siret à qualifier\nActivité : {activity}\nContact : à qualifier\nVille : {city}\nCode postal : {postcode}\nTél. / Mail : à qualifier'
    text(p,x,y,w,contact,size-0.5,h=180)

# PAGE 3 — preserve all channel copy, arrows and CRM screenshot.
p=DOC[2]
clear(p,[((515,139,1043,620),BG),((519,620,765,749),BG),((1095,250,1380,784),BG)])
# Two RCS creatives
for y, title, body, cta in [(141,'Votre caisse tactile,\nsimplement.','Commerce, restaurant :\ncomparez les solutions\nadaptées à votre activité.','Ça m’intéresse !'),(451,'Modernisez votre\nencaissement','Caisse, logiciel et accessoires :\nprécisez votre besoin,\nrecevez des offres.','Comparer les offres')]:
    rect(p,(518,y,761,y+289),WHITE,radius=.04)
    pos(p,518,y,243,128)
    text(p,532,y+139,218,title,17,True)
    text(p,532,y+194,218,body,12,color=MUTED)
    button(p,530,y+251,219,cta,12)
rect(p,(778,157,1031,612),WHITE)
text(p,792,171,225,'CAISSES TACTILES',17,True,BLUE)
pos(p,792,210,225,134)
text(p,795,359,219,'Trouvez la caisse adaptée\nà votre commerce',16,True,align=1)
field(p,795,423,219,'Votre secteur d’activité ?','Commerce de détail')
field(p,795,498,219,'Votre projet ?','Premier équipement')
button(p,795,573,219,'Suivant',12)
lead(p,1099,253,270,[('Type de projet :','Premier équipement'),('Secteur d’activité :','Commerce alimentaire'),('Nombre de caisses souhaité :','2 postes tactiles'),('Fonctionnalités recherchées :','Encaissement, stocks, fidélité'),('Budget envisagé :','2 000 € à 4 000 €'),('Échéance du projet :','Dans 1 à 3 mois')], 'LE COMPTOIR NANTAIS','Épicerie de proximité','Nantes','44000',gap=6)

# PAGE 4 — landing page and qualification form.
p=DOC[3]
clear(p,[((479,85,960,757),BG),((1008,451,1307,777),BG)])
rect(p,(483,89,956,441),WHITE)
pos(p,483,89,473,270)
rect(p,(701,108,940,377),WHITE,radius=.03)
text(p,716,123,209,'Comparez les offres de\ncaisses tactiles',16,True,BLUE)
text(p,716,184,209,'Quel est votre projet ?',12,True)
for yy,lab in [(219,'Premier équipement'),(255,'Remplacement de caisse'),(291,'Ouverture d’un point de vente')]:
    rect(p,(717,yy,728,yy+11),WHITE,(.65,.72,.80))
    text(p,735,yy-3,195,lab,10)
button(p,716,331,209,'Suivant',12)
text(p,498,370,430,'Caisses enregistreuses tactiles',19,True,BLUE)
text(p,498,407,430,'Commerces · Restaurants · Boutiques',12,align=1)
rect(p,(483,452,956,745),LIGHT)
rect(p,(498,465,941,515),INK,radius=.07)
text(p,515,475,410,'Extrait du formulaire',18,True,WHITE)
text(p,515,534,405,'Combien de caisses souhaitez-vous ?',14,True,BLUE)
for yy,lab in [(581,'1 caisse'),(617,'2 à 3 caisses'),(653,'4 caisses et plus')]:
    rect(p,(518,yy,532,yy+14),WHITE,(.63,.71,.80))
    if yy==617:
        p.draw_polyline([(520,yy+7),(524,yy+11),(531,yy+2)], color=BLUE, width=1.5)
    text(p,545,yy-3,350,lab,13)
button(p,805,697,118,'Suivant',12)
lead(p,1012,453,295,[('Type de projet :','Remplacement de caisse'),('Nombre de caisses :','2 à 3 postes tactiles'),('Échéance du projet :','Dans 1 à 3 mois')], 'LE BISTROT DES EMBRUNS','Restauration traditionnelle','Saint-Malo','35400',size=11,gap=5)

# PAGE 5 — social creative and instant lead form.
p=DOC[4]
clear(p,[((406,173,1059,640),BG),((1088,265,1370,749),BG)])
rect(p,(416,210,719,637),WHITE)
text(p,430,222,275,'Solutions Caisses Pro',16,True,BLUE)
text(p,430,250,275,'Sponsorisé · Exemple de création',10,color=MUTED)
text(p,430,281,275,'Une caisse tactile adaptée\nà votre activité.',18,True)
pos(p,430,348,275,190,scene='restaurant')
text(p,430,550,275,'Encaissement • Stocks • Fidélité',12,True)
button(p,430,588,275,'Demander mes devis',13)
rect(p,(736,210,1047,637),WHITE)
text(p,752,225,279,'VOTRE PROJET CAISSE',18,True,BLUE)
text(p,752,264,279,'Recevez des offres adaptées\nà votre point de vente.',13)
field(p,752,329,279,'Votre activité ?','Restauration rapide')
field(p,752,412,279,'Votre besoin ?','Ouverture d’un restaurant')
field(p,752,495,279,'Votre échéance ?','Sous 3 mois')
button(p,752,588,279,'Continuer',13)
lead(p,1091,268,273,[('Type de projet :','Ouverture d’un restaurant'),('Secteur d’activité :','Restauration rapide (B2B)'),('Nombre de caisses :','1 poste tactile'),('Fonctions souhaitées :','Sur place, à emporter, stocks'),('Échéance du projet :','Sous 3 mois'),('Accessoires souhaités :','Imprimante tickets, tiroir-caisse')], 'LE COMPTOIR GOURMAND','Restauration rapide','La Roche-sur-Yon','85000',gap=4)

# PAGE 6 — adapt call qualification; preserve the call-centre photograph.
p=DOC[5]
clear(p,[((410,163,1047,518),BG),((1079,333,1380,785),BG)])
rect(p,(411,169,1039,512),WHITE)
rect(p,(411,169,1039,209),INK)
text(p,429,177,590,'HelloLead · Qualification téléphonique',17,True,WHITE)
text(p,429,224,590,'DEMANDE DE DEVIS · CAISSES ENREGISTREUSES TACTILES',15,True,BLUE)
text(p,429,261,590,'Quel est le besoin du professionnel ?',14,True)
for yy,label in [(303,'Remplacer une caisse existante'),(339,'Équiper un nouveau point de vente'),(375,'Ajouter des postes d’encaissement')]:
    rect(p,(431,yy,444,yy+13),WHITE,(.63,.71,.80))
    if yy==303:
        p.draw_polyline([(433,yy+7),(437,yy+10),(443,yy+2)],color=BLUE,width=1.5)
    text(p,456,yy-3,550,label,13)
text(p,429,419,572,'Secteur : restauration · 2 caisses · Décideur : gérant',12)
button(p,429,463,273,'Projet qualifié · À transmettre',12)
text(p,721,468,293,'Exemple de fiche de qualification',10,color=MUTED)
lead(p,1082,336,280,[('Catégorie CRM du besoin :','Caisses enregistreuses tactiles'),('Type de projet et statut :','Remplacement, professionnel (B2B)'),('Nombre de caisses :','2 postes tactiles'),('Décideur identifié :','Gérant de l’établissement'),('Disponibilité pour un appel :','Demain à 11 h')], 'LA TABLE DES ALPES','Restauration traditionnelle','Annecy','74000',size=12.5,gap=6)

# PAGE 7 — two example email campaigns.
p=DOC[6]
clear(p,[((432,96,1005,794),BG),((1078,292,1380,783),BG)])
rect(p,(440,98,724,790),WHITE)
text(p,457,116,250,'CAISSES PRO',20,True,BLUE)
text(p,457,165,250,'La bonne caisse pour\nvotre point de vente',21,True)
pos(p,440,247,284,179)
text(p,457,445,250,'Simplifiez votre quotidien',15,True)
text(p,457,487,250,'Encaissez vos ventes, suivez\nvos stocks et retrouvez vos\ndonnées dans un même outil.',13)
for yy,label in [(571,'Encaissement tactile'),(611,'Gestion des stocks'),(651,'Suivi de l’activité')]:
    rect(p,(458,yy+4,468,yy+14),BLUE)
    text(p,480,yy,225,label,13)
button(p,456,705,252,'Comparer les solutions',12)
text(p,456,754,252,'Exemple de campagne · Visuel indicatif',8,color=MUTED)
rect(p,(743,105,1001,785),WHITE)
rect(p,(743,105,1001,169),INK)
text(p,758,121,228,'Votre commerce évolue.\nVotre caisse aussi.',16,True,WHITE)
pos(p,743,169,258,168,scene='restaurant')
text(p,759,357,226,'Un projet d’équipement ?',16,True,BLUE)
text(p,759,414,226,'Bonjour,\n\nVous ouvrez un commerce\nou souhaitez remplacer\nvotre caisse actuelle ?\n\nPrécisez votre activité,\nle nombre de postes et\nles fonctions recherchées.\n\nComparez des solutions\nadaptées à votre besoin.',12,h=265)
button(p,758,678,228,'Étudier mon projet',12)
text(p,759,737,226,'Exemple de campagne B2B\nLien de désinscription',9,color=MUTED)
lead(p,1082,295,282,[('Déjà équipé d’une caisse ?','Oui, remplacement souhaité'),('Secteur d’activité :','Commerce de détail'),('Nombre de points de vente :','2 boutiques, 1 caisse par site'),('Budget envisagé :','3 000 € à 5 000 €'),('Fonctions recherchées :','Stocks multi-sites, fidélité'),('Échéance du projet :','Dans 3 à 6 mois')], 'LES BOUTIQUES DE PROVENCE','Prêt-à-porter','Aix-en-Provence','13100',gap=5)

DOC.set_metadata({**DOC.metadata,'title':'HelloLead — Caisses enregistreuses tactiles','subject':'Génération de leads — Caisses enregistreuses tactiles'})
DOC.save(OUTPUT,garbage=4,deflate=True)
print(OUTPUT)
# Pixel-by-pixel guarantee for pages explicitly excluded from the adaptation.
result=pdf.open(OUTPUT)
original=pdf.open(SOURCE)
for i in [0,1,7,8]:
    assert original[i].get_pixmap().samples == result[i].get_pixmap().samples, f'Page {i+1} changed'
for i in [2,3,4,5,6]:
    content=result[i].get_text().lower()
    assert not any(word in content for word in ['solaire','photovolta','toiture','kwh','kwc']), f'Solar reference on page {i+1}'
    result[i].get_pixmap(matrix=pdf.Matrix(.8,.8)).save(ROOT / '.cache' / f'adapted-{i+1}.png')
print('Verified: 9 pages; pages 1, 2, 8, 9 pixel-identical; adapted pages contain no solar text.')
