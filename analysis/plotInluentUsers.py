import sys
from collections import Counter
import matplotlib
import matplotlib.cm as cm
matplotlib.use('Agg')
import numpy as np
import matplotlib.pyplot as plt

c11 = Counter({'michaelskolnik': 25, 'antoniofrench': 12, 'pzfeed': 4, 'pdpj': 4, 'youranonnews': 3, 'khaledbeydoun': 1, 'womenonthemove1': 1, 'robertdedwards': 1, 'stlabubadu': 1, 'ericwolfson': 1, 'marmel': 1, 'ribriguy': 1, 'djwitz': 1, 'professorcrunk': 1, 'jasiri_x': 1, 'dtsteele': 1, 'dierdrelewis': 1, 'stevegiegerich': 1, 'holzmantweed': 1, 'stjamesstjames': 1, 'blistpundit': 1, 'thebloggess': 1, 'so_lo_travels': 1, 'coryprovost': 1, 'kerrywashington': 1, 'therealbanner': 1, '2chainzlyrics': 1, 'mmmphoenix': 1, 'kirbyoneal': 1, 'rolandsmartin': 1, 'peacebang': 1, 'negrointellect': 1, 'kiash__': 1, 'iamnatejames': 1, 'rt_com': 1, 'breakinthebank': 1, 'breakingnews': 1, 'auragasmic': 1, 'ksdknews': 1, 'so_treu': 1, 'brennamuncy': 1, 'sunnyhostin': 1, 'breevive': 1, 'theinventher': 1, 'mmgterrick24': 1, 'kirkman': 1, 'caseyjaldridge': 1, 'untoldmysteries': 1, 'syndicalisms': 1, 'marcusjulienlee': 1, 'shugnice': 1, 'politibunny': 1, 'lolitasaywhat': 1, 'chrislhayes': 1, 'locsofpassion': 1, 'moundcity': 1, 'lisabolekaja': 1})
c12 = Counter({'antoniofrench': 10, 'fox2now': 6, 'juliebosman': 5, 'pdpj': 4, 'wesleylowery': 3, 'nettaaaaaaaa': 3, 'michaelskolnik': 3, 'raydowns': 2, 'luvliteracy': 2, 'maureenjohnson': 2, 'youranonnews': 2, 'mvpgo': 2, 'nateog91': 2, 'devincf': 2, 'lizpeinadostl': 1, 'pzfeed': 1, 'erinpeep': 1, 'cnnbrk': 1, 'matthewpa_to': 1, 'bonedog84': 1, 'talibkweli': 1, 'davidjlynch': 1, 'patrickrothfuss': 1, 'jonswaine': 1, 'tradethetradepr': 1, 'rogersparkjon': 1, 'mattdpearce': 1, 'jamalhbryant': 1, 'bartongellman': 1, 'caleb_orion': 1, 'aishas': 1, 'groovesdc': 1, 'asvpxrocky': 1, 'brianstelter': 1, 'rolandsmartin': 1, 'thecoolnoodle': 1, 'mattfredstl': 1, 'nycjim': 1, 'suntimes': 1, 'fordm': 1, 'ksdknews': 1, 'stevehuff': 1, 'brennamuncy': 1, 'raniakhalek': 1, 'mollycrabapple': 1, 'tusk81': 1, 'youranonlive': 1, 'hollywoodjuan': 1, 'ajmeadows': 1, 'sarahkendzior': 1, 'mikelellcessor': 1, 'ap': 1, 'menphyel7': 1, 'wilw': 1, 'unclerush': 1, 'sorahyam': 1, 'wkamaubell': 1, 'ositanwanevu': 1, 'juliacarriew': 1, 'sarahgaydos': 1, 'brookeobie': 1, 'milftasticjjc': 1, 'dloesch': 1, 'kristyt': 1, 'blanketboat': 1, 'johnlegend': 1})
c14 = Counter({'youranonnews': 8, 'antoniofrench': 5, 'pzfeed': 3, 'tallyannae': 3, 'evanchill': 2, 'wesleylowery': 2, 'occupythemob': 2, 'pdpj': 2, 'elonjames': 2, 'crypt0nymous': 2, 'bvgamble': 1, 'david_ehg': 1, 'ay_e_iou': 1, 'damn_vandal': 1, 'adamweinstein': 1, 'youranonglobal': 1, 'nicholsuprising': 1, 'dan_bernstein': 1, 'cnnbrk': 1, 'mariambarghouti': 1, 'infinite_me': 1, 'mattmurph24': 1, 'jasiri_x': 1, 'tuxcedocat': 1, 'fluorescentgrey': 1, 'bucci2028': 1, 'thesource': 1, 'matthewkeyslive': 1, 'occupyoakland': 1, 'juliacarriew': 1, 'jennhoffman': 1, 'abeaujon': 1, 'the_blackness48': 1, 'lpolgreen': 1, 'linc0lnpark': 1, 'joey_powell': 1, 'alicesperi': 1, 'max_fisher': 1, 'ynpierce': 1, 'elikmbc': 1, 'tim_sweetiepies': 1, 'hayesbrown': 1, 'blackink12': 1, 'rajaiabukhalil': 1, 'bencasselman': 1, 'slate': 1, 'notthefakesvp': 1, 'miafarrow': 1, 'nycjim': 1, 'repjustinamash': 1, 'jackfrombkln': 1, 'isaiahjturner': 1, 'michaelianblack': 1, 'syndicalisms': 1, 'jemelehill': 1, 'huffpostpol': 1, 'kingsleyyy': 1, 'gerardway': 1, 'mkhill': 1, 'jamilsmith': 1, 'bendoernberg': 1, 'briankoppelman': 1, 'vanaman': 1, 'jrocklaguins': 1, 'breakingnews': 1, 'al3x': 1, 'michaelskolnik': 1, 'guerrillascribe': 1, 'wilw': 1, 'christinaksdk': 1, 'yamiche': 1, 'fox2now': 1, 'kodacohen': 1, 'jaymills': 1, 'taylordobbs': 1, 'manofsteele': 1, 'anonypress': 1, 'bet': 1, 'charlesmblow': 1})
c15 = Counter({'antoniofrench': 10, 'wesleylowery': 3, 'ryanjreilly': 3, 'pzfeed': 2, 'ocongress': 2, 'youranonnews': 2, 'anonymouspress': 2, 'ariannahuff': 1, 'myfoxla': 1, 'ballininhd': 1, 'mcmuckraker': 1, 'anarchoanon': 1, 'youranonglobal': 1, 'durrieb': 1, 'cnnbrk': 1, 'beaconreader': 1, 'ladyy_rhe': 1, 'mashable': 1, 'isweariainthit': 1, 'theleong': 1, 'cnntonight': 1, 'chicagoreporter': 1, 'occupywallstnyc': 1, 'cnni': 1, 'newsweek': 1, 'jonswaine': 1, 'op_israel': 1, 'yamiche': 1, 'hrw': 1, 'the_blackness48': 1, 'cheathamkmov': 1, 'brianrokuscnn': 1, 'arizzle314': 1, 'bdsams': 1, 'lynnhb': 1, '140elect': 1, 'janetmock': 1, 'jamesfallows': 1, 'nbcnews': 1, 'cnn': 1, 'antheabutler': 1, 'sucls': 1, 'freetopher': 1, 'chadgarrison': 1, 'jrehling': 1, 'nytimes': 1, 'charlesjaco1': 1, 'jfreewright': 1, 'devincf': 1, 'jackfrombkln': 1, 'ajenglish': 1, 'nickconfessore': 1, 'rt_com': 1, 'amyknelson': 1, 'sftovarishch': 1, 'sunnyhostin': 1, 'ericcnnbelief': 1, 'harvardblsa': 1, 'jamilsmith': 1, 'zerlinamaxwell': 1, 'caseynolen': 1, 'kellimaxx': 1, 'weberkristen': 1, 'plzkeepit100': 1, 'nickbilton': 1, 'michaelskolnik': 1, 'rt_america': 1, 'elonjames': 1, 'tannercurtis': 1, 'unclerush': 1, 'jeffersonobama': 1, 'mantoniebyrd': 1, 'mrpooni': 1, 'lordbape': 1, 'seanhannity': 1, 'michaelcalhoun': 1, 'clairecmc': 1, 'mattdpearce': 1, 'mspackyetti': 1, 'johnpiper': 1, 'j_hancock': 1, '1marchella': 1, 'markos': 1})
c16 = Counter({'antoniofrench': 9, 'koranaddo': 5, 'phampel': 4, 'ryanjreilly': 4, 'michaelcalhoun': 4, 'cnnbrk': 3, 'occupyoakland': 3, 'blackink12': 3, 'yamiche': 3, 'bkesling': 2, 'youranonnews': 2, 'awkward_duck': 2, 'freetopher': 2, 'rustymk2': 1, 'bmoreconetta': 1, 'vicenews': 1, 'youranonglobal': 1, 'buzzfeednews': 1, 'drbasselabuward': 1, 'propublica': 1, 'reallucasneff': 1, 'wesleylowery': 1, 'ap': 1, 'ladyy_rhe': 1, 'kodacohen': 1, 'stevenjhsieh': 1, 'matt_maisel': 1, 'martinotx': 1, 'timcast': 1, 'specialdallas': 1, 'the_blackness48': 1, 'goldietaylor': 1, 'alicesperi': 1, 'assholeofday': 1, 'aclu': 1, 'therealbanner': 1, 'crypt0nymous': 1, 'cnn': 1, 'candacetx': 1, 'actualidadrt': 1, 'jackfrombkln': 1, 'scottbix': 1, 'larryelder': 1, 'theapjournalist': 1, 'nbcnews': 1, 'slate': 1, 'k_psi': 1, 'americatonight': 1, 'rt_com': 1, 'amyknelson': 1, 'dafnalinzer': 1, 'blowticious': 1, 'jack': 1, 'lisamcintire': 1, 'c_a_nicegirl': 1, 'wendellpierce': 1, 'jacobshall': 1, 'bobby_griffith': 1, 'wsj': 1, 'williamcander': 1, 'toluseo': 1, 'brennanator': 1, 'fox2now': 1, 'iameddiebaker': 1, 'manofsteele': 1, '1marchella': 1, 'joyannreid': 1})
c17 = Counter({'ryanjreilly': 11, 'youranonnews': 10, 'antoniofrench': 8, 'yamiche': 3, 'jonswaine': 3, 'bbcbreaking': 2, 'pdpj': 2, 'alicesperi': 2, 'jrehling': 2, 'starforcehh': 2, 'blackink12': 2, 'bradhutchings': 1, 'youranonlive': 1, 'aaltman82': 1, 'charlieleduff': 1, 'jabuchanan': 1, 'cnnbrk': 1, 'ijessewilliams': 1, 'jessicajannee': 1, 'ap': 1, 'ladyy_rhe': 1, 'mashable': 1, 'astroehlein': 1, 'ank_wobl': 1, 'trymainelee': 1, 'fightfortheftr': 1, 'stephlecci': 1, 'tomscherschel': 1, 'timcast': 1, 'reignofapril': 1, 'opferguson': 1, 'samuelaadams': 1, 'prisonculture': 1, 'aclu': 1, 'geeknstereo': 1, 'kerrywashington': 1, 'mtracey': 1, 'actualidadrt': 1, 'will_bunch': 1, 'scottbix': 1, 'matthewkick': 1, 'organizemo': 1, 'hollisjames': 1, 'fordm': 1, 'jeremyclagett': 1, 'amyknelson': 1, 'mrdaveyd': 1, 'huffingtonpost': 1, 'awkward_duck': 1, 'jersey_jinx': 1, 'paigelav': 1, 'ellehoneybee': 1, 'thedronalisa': 1, 'liquidego': 1, 'brokenhegemony': 1, 'ciselytycoon': 1, 'oadamo': 1, 'kmov': 1, 'socarolinesays': 1, 'green_footballs': 1, 'anonycrypt': 1, 'vinceperritano': 1, 'sistatofunky': 1, 'dibhakanfidan': 1})


c11 = dict(c11.most_common(10))
print(c11)
c12 = dict(c12.most_common(10))
print(c12)
c14 = dict(c14.most_common(10))
print(c14)
c15 = dict(c15.most_common(10))
print(c15)
c16 = dict(c16.most_common(10))
print(c16)
c17 = dict(c17.most_common(10))
print(c17)

print(" ")

cs = [c11,c12,c14,c15,c16,c17]

#keys = set(c11.keys() + c12.keys() + c14.keys() + c15.keys() + c16.keys() + c17.keys())
keys = set(c17.keys())

colors = ["#CCCCCC","#862B59","#0A6308","#A10000","#123677","#ff8100","#F28686","#6adf4f","#58ccdd","#3a3536"]

ys = {}
for k in keys :
  ys[k] = []

for c in cs :
  for k in keys :
	if k in c :
	  ys[k].append(c[k])
	else :
	  ys[k].append(0)

print(ys)

xticks = ["11/08","12/08","14/08","15/08","16/08","17/08"]
x = range(len(xticks))
print(x)

plt.clf()
ax = plt.figure(figsize=[7,7])
plt.xticks(x, xticks)

ax = plt.subplot(111)
for y,c in zip(ys,colors) :
    line, = ax.plot(x,ys[y], label=y,c=c)

# Shrink current axis's height by 10% on the bottom
box = ax.get_position()
ax.set_position([box.x0, box.y0 + box.height * 0.1,
                 box.width, box.height * 0.9])

# Put a legend below current axis
ax.legend(loc='upper center', bbox_to_anchor=(0.5, -0.05),
          fancybox=True, shadow=True, ncol=5,prop={'size':8})
plt.savefig("freqInfluentUsers.png",dpi = 200)
