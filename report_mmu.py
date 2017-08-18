PREC='.0f' # defines output precision
head={'EN':'', 'FR':'', 'PT':''}
head['EN'] = """
<head>
    <title>IMPACT Report on forest area change and resulting emissions</title>
    <style>
        body{font-family: Arial, sans-serif; font-size:14px; width: 17cm;}
        h1{font-family: Arial, sans-serif; font-size:20px; font-weight:bold}
        h1.mainTitle{font-size:28px;}
        h2{font-family: Arial, sans-serif; font-size:18px; font-weight:bold; margin-top:6px; margin-bottom:0}
        h3{font-family: Arial, sans-serif; font-size:14px; font-weight:bold; margin-bottom:0; margin-top:6px; padding:0}
        p{font-family: Arial, sans-serif; font-size:14px; margin-left:40px; margin-top:0; padding:0}
        ul {list-style-type: none;}
        ul li:before {
            content: '\\2014';
            position: absolute;
            margin-left: -20px;
            }
        table{width:36em;}
        table.large{width:45em}
        table, th, tr, td {
            border: 0px solid black;
            border-collapse: collapse;
            text-align: left;
            font-family: Arial, sans-serif;
            font-size:14px;
            }
        table.center{margin-left:auto; margin-right:auto}
        span.toFill{color:red; font-weight:bold}
        div.result{border: 1px solid black; }
    </style>
</head>
"""
head['FR'] = """
<head>
    <title>IMPACT Rapport sur les changements d'aires de for&ecirc;t et des &eacute;missions r&eacute;sultantes</title>
    <style>
        body{font-family: Arial, sans-serif; font-size:14px; width: 17cm;}
        h1{font-family: Arial, sans-serif; font-size:20px; font-weight:bold}
        h1.mainTitle{font-size:28px;}
        h2{font-family: Arial, sans-serif; font-size:18px; font-weight:bold; margin-top:6px; margin-bottom:0px}
        h3{font-family: Arial, sans-serif; font-size:14px; font-weight:bold; margin-bottom:0; margin-top:6px; padding:0}
        p{font-family: Arial, sans-serif; font-size:14px; margin-left:40px; margin-top:0; padding:0}
        ul {list-style-type: none;}
        ul li:before {
            content: '\\2014';
            position: absolute;
            margin-left: -20px;
            }
        table{width:36em;}
        table.large{width:45em}
        table, th, tr, td {
            border: 0px solid black;
            border-collapse: collapse;
            text-align: left;
            font-family: Arial, sans-serif;
            font-size:14px;
            }
        table.center{margin-left:auto; margin-right:auto}
        span.toFill{color:red; font-weight:bold}
        div.result{border: 1px solid black;}
    </style>
</head>
"""
head['PT'] = head['EN']

# ____________________
report_head = {'EN':'', 'FR':'', 'PT':''}
report_head['EN']='''<h1 class="mainTitle">Report on forest area change and resulting emissions</h1>
<h2>Geographic location</h2>
Country: <span class="toFill">[Country name]</span><br/>
Geographic window: longitude: {11:.3f}&deg; to {13:.3f}&deg;, latitude: {14:.3f}&deg; to {12:.3f}&deg; <br/>
Zone of interest: <span class="toFill">[Zone of interest]</span> <br/>
<h2>Period of analysis and year span</h2>
Historical: {2} ({0} {1})<br/>
Recent: {5} ({3} {4})<br/>
<h2>Forest definitions</h2>
Minimum Mapping Unit (MMU): {7:.2f} ha<br/>
Forest cover threshold: {8} &#37;<br/>
<h2>Activity data</h2>
Source: <span class="toFill">[Please describe source]</span><br/>
File: {9}</br/>
Processing done on {10}.
<h2>Emission factor</h2>
Emission factor for deforestation{6} tC/ha<br/>
Emission factor for degradation: {15}% of the deforestation emission factor.<br/>

<h2>Expert</h2>
<span class="toFill">[Please insert expert name]</span><br/>
'''
report_head['FR'] = '''
<h1 class="mainTitle">Rapport sur l'&eacute;volution des surfaces foresti&egrave;res et les &eacute;missions li&eacute;es</h1>
<h2>Localisation</h2>
Pays : <span class="toFill">[Nom du pays]</span><br/>
Fen&ecirc;tre g&eacute;ographique : longitude: de {11:.3f}&deg; &agrave; {13:.3f}&deg;, latitude: de {14:.3f}&deg; &agrave; {12:.3f}&deg; <br/>
Zone d'int&eacute;r&ecirc;t : <span class="toFill">[Zone d'int&eacute;r&ecirc;t]</span> <br/>
<h2>P&eacute;riodes couvertes par l'analyse</h2>
Historique : {2} ({0} {1})<br/>
R&eacutecente : {5} ({3} {4})<br/>
<h2>D&eacutefinition de la for&ecirct</h2>
Unit&eacute Cartographique Minimale (UCM) : {7:.2f} ha<br/>
Seuil de couvert de for&ecirc;t : {8} &#37;<br/>
<h2>Donn&eacute;es d'activit&eacute</h2>
Source : <span class="toFill">[Veuillez d&eacute;crire la source]</span><br/>
Fichier : {9}</br/>
Traitement effectu&eacute; le {10}.
<h2>Facteur d'&eacute;mission</h2>
Facteur d'&eacute;mission pour la d&eacute;forestation{6} tC/ha<br/>
Facteur d'&eacute;mission pour la d&eacute;gradation: {15}% du facteur d'&eacute;mission pour la d&eacute;forestation.<br/>
<h2>Expert</h2>
<span class="toFill">[Veuillez ins&eacute;rer le nom de l'expert]</span><br/>
'''
report_head['PT'] = report_head['EN']

# ____________________
#report_area_head = {'EN':'', 'FR':'', 'PT':''}
#report_area_head['EN'] = '''
#                     '''
#report_area_head['FR'] = '''
#'''
#report_head['PT'] = report_area_head['EN']
#
# ____________________
report_pixel_table = {'EN':'', 'FR':'', 'PT':''}

report_pixel_table['EN'] = '''
<hr/>
<h1>Annex</h1>
<h1>1/ Forest change at pixel level</h1>
                    This section reports for the total count of pixels, for the different types of trajectories, namely:
                    <ul>
                    <li><b>Forest, unchanged</b>: pixels detected as forest, and remaining unchanged for both periods P1 and P2;</li>
                    <li><b>Non forest, unchanged</b>: pixels detect as non-forest, and remaining unchanged for both periods P1 and P2;</li>
                    <li><b>Forest to non-forest, P1</b>: converted from forest to non forest (degraded or deforested) over periods P1 and P2;</li>
                    <li><b>Forest to non-forest, P2</b>: no data pixels</li>
                    </ul>
<table class="large">
                    <tr>
                        <th></th><th style="border-bottom: 1px solid black">Pixel count</th><th style="border-bottom: 1px solid black">Area</th>
                    </tr>
                    <tr> <td>Forest, unchanged</td><td> {0} </td><td> {1:'''+PREC+'''} ha</td> </tr>
                    <tr> <td>Non forest, unchanged</td><td> {2} </td><td> {3:'''+PREC+'''} ha</td><td></td> </tr>
                    <tr> <td>Forest to non-forest, P1</td><td> {4} </td><td> {5:'''+PREC+'''} ha</td> </tr>
                    <tr> <td>Forest to non-forest, P2</td><td> {6} </td><td> {7:'''+PREC+'''} ha</td> </tr>
                    <tr> <td>No data</td><td> {8} </td><td> {9:'''+PREC+'''} ha</td> </tr>
                    </table>
                    <b>Conversion rates per year</b><br/>
                    Forest to non-forest, P1 = {10:''' + PREC + '''} ha per year<br/>
                    Forest to non-forest, P2 = {11:''' + PREC +'''} ha per year<br/>
                    '''
report_pixel_table['FR']='''
<hr/>
<h1>Annexe</h1>
                    <h1>1/ Compte de pixels dans l'image d'entr&eacute;  e</h1>
                    Cette section indique le compte total de pixels, pour les diff&eacute;rents types de trajectoires, soit&nbsp;:
                    <ul>
                    <li><b>For&ecirc;t, inchang&eacute;e</b>&nbsp;: pixels d&eacute;tect&eacute;s comme for&ecirc;t et demeurant inchang&eacute;s pour les p&eacute;riodes P1 et P2&nbsp;;</li>
                    <li><b>Non forest, inchang&eacute;e</b>&nbsp;: pixels d&eacute;tect&eacute;s comme non-for&ecirc;t et demeurant inchang&eacute;s pour les p&eacute;riodes P1 et P2&nbsp;;</li>
                    <li><b>For&ecirc;t en non-for&ecirc;t, P1</b>&nbsp;: pixels convertis de for&ecirc;t en non for&ecirc;t (degrad&eacute;s ou d&eacute;forest&eacute;s) sur les p&eacute;riodes P1 and P2&nbsp;;</li>
                    <li><b>For&ecirc;t en non-for&ecirc;t, P2</b>&nbsp;: pixels convertis de for&ecirc;t en non for&ecirc;t (degrad&eacute;s ou d&eacute;forest&eacute;s) sur les p&eacute;riodes P1 and P2&nbsp;;</li>
                    <li><b>No-data&nbsp;:</b> pixels sans donn&eacute;es.</li>
                    </ul>
<table class="large">
                    <tr>
                        <th></th><th style="border-bottom: 1px solid black">Pixel count</th><th style="border-bottom: 1px solid black">Area</th>
                    </tr>
                    <tr> <td>For&ecirc;t, inchang&eacute;e</td><td> {0} </td><td> {1} ha</td> </tr>
                    <tr> <td>Non for&ecirc;t, inchang&eacute;e</td><td> {2} </td><td> {3} ha</td><td></td> </tr>
                    <tr> <td>For&ecirc;t &agrave; non-for&ecirc;t, P1</td><td> {4} </td><td> {5} ha</td> </tr>
                    <tr> <td>For&ecirc;t &agrave; non-for&ecirc;t, P2</td><td> {6} </td><td> {7} ha</td> </tr>
                    <tr> <td>No data</td><td> {8} </td><td> {9} ha</td> </tr>
                    </table>
                    <b>Taux annuels de conversion</b>
                    For&ecirc;t en non-for&ecirc;t, P1 = {10:''' + PREC + '''} ha par an<br/>
                    For&ecirc;t en non-for&ecirc;t, P2 = {10:''' + PREC + '''} ha par an<br/>
'''
report_pixel_table['PT']=report_pixel_table['EN']
# ___________________
report_section_per_MMU_pixel = {'EN':'', 'FR':'', 'PT':''}
report_section_per_MMU_pixel['EN'] = '''
<h1>1. Forest conversion and resulting emissions evaluated using the MMU</h1>
These are calculated on the proportion of the reference area boxes (MMU) that changes during the periods of analysis (number of pixels loosing their tree cover inside the reference area boxes).
<div class="result">
Forest area in {8}: {9:'''+PREC+'''} ha<br/>
</div>
<h2>1.1 Forest conversion</h2>
<div class="result">
<h3>Forest conversion &dash; Historical</h3>
<table>
<tr><th>Total</th><th>Annual</th></tr>
<tr><td>Deforestation: {0:'''+PREC+'''} ha</td><td> {2:'''+PREC+'''} ha/y</td></tr>
<tr><td>Degradation: {1:'''+PREC+'''} ha</td><td> {3:'''+PREC+'''} ha/y</td></tr>
</table>
</div>
<br/>
<div class="result">
<h3>Forest conversion &dash; Recent</h3>
<table>
<tr><th>Total</th><th>Annual</th></tr>
<tr><td>Deforestation: {4:'''+PREC+'''} ha</td><td> {6:'''+PREC+'''} ha/y</td></tr>
<tr><td>Degradation: {5:'''+PREC+'''} ha</td><td> {7:'''+PREC+'''} ha/y</td></tr>
</table>
</div>
'''
report_section_per_MMU_pixel['FR'] = '''
<h1>1. Changement du couvert forestier et &eacute;missions r&eacute;sultantes evalu&eacute;es en utilisant les UCM</h1>
Les changements sont calcul&eacute;s sur la base de la proportion de surfaces de r&eacute;f&eacute;rences (UCM) qui changent au cours des p&eacute;riodes d'analyses (nombre de pixels ayant perdu leur couvert arbor&eacute; dans les UCM).
<div class="result">
Surface de for&ecirc;t en {8} : {9:'''+PREC+'''} ha<br/>
</div>
<h2>1.1 Changement au sein des surfaces foresti&egrave;res</h2>
<div class="result">
<h3>Conversion de la for&ecirc;t &dash; Historique</h3>
<table>
<tr><th>Total</th><th>Annuel</th></tr>
<tr><td>D&eacuteforestation : {0:'''+PREC+'''} ha</td><td> {2:'''+PREC+'''} ha/an</td></tr>
<tr><td>D&eacutegradation : {1:'''+PREC+'''} ha</td><td> {3:'''+PREC+'''} ha/an</td></tr>
</table>
</div>
<br/>
<div class="result">
<h3>Conversion de la for&ecirc;t &dash; R&eacute;cente</h3>
<table>
<tr><th>Total</th><th>Annuel</th></tr>
<tr><td>D&eacute;forestation : {4:'''+PREC+'''} ha</td><td> {6:'''+PREC+'''} ha/an</td></tr>
<tr><td>D&eacute;gradation : {5:'''+PREC+'''} ha</td><td> {7:'''+PREC+'''} ha/an</td></tr>
</table>
</div>
'''
report_section_per_MMU_pixel['PT'] = report_section_per_MMU_pixel['EN']

# ___________________
report_section_per_MMU = {'EN':'', 'FR':'', 'PT':''}

report_section_per_MMU['EN']='''
<h2>1.2 Emission per MMU</h2>
<div class="result">
<h3>Emissions &dash; Historical</h3>
<table>
<tr><th>Total</th><th>Annual</th></tr>
<tr><td>Deforestation: {8:'''+PREC+'''} tEqCO<sub>2</sub></td><td> {10:'''+PREC+'''} tEqCO<sub>2</sub>/y</td></tr>
<tr><td>Degradation: {9:'''+PREC+'''} tEqCO<sub>2</sub></td><td> {11:'''+PREC+'''} tEqCO<sub>2</sub>/y</td></tr>
</table>
</div>
<br/>
<div class="result">
<h3>Emissions &dash; Recent</h3>
<table>
<tr><th>Total</th><th>Annual</th></tr>
<tr><td>Deforestation: {12:'''+PREC+'''} tEqCO<sub>2</sub></td><td> {14:'''+PREC+'''} tEqCO<sub>2</sub>/y</td></tr>
<tr><td>Degradation: {13:'''+PREC+'''} tEqCO<sub>2</sub></td><td> {15:'''+PREC+'''} tEqCO<sub>2</sub>/y</td></tr>
</table>
</div>
<br/>
<h1>2. Forest areas affected by deforestation and degradation</h1>
These are calculated on number of the reference area boxes (MMU) that changes during the periods of analysis &dash; they are not suitable for calculating emissions, but give an overview of the trends.
<div class="result">
Forest area in {16}: {17:'''+PREC+'''} ha<br/>
</div>
<br/>
<div class="result">
<h3>Forest areas affected by changes &dash; Historical</h3>
<!--
<table>
<tr><th>Total</th><th>Annual</th></tr>
<tr><td>Deforestation: {0:'''+PREC+'''} ha</td><td> {2:'''+PREC+'''} ha/y</td></tr>
<tr><td>Degradation: {1:'''+PREC+'''} ha</td><td> {3:'''+PREC+'''} ha/y</td></tr>
</table>
-->
<table>
<tr><th>Total</th></tr>
<tr><td>Deforestation: {0:'''+PREC+'''} ha</td></tr>
<tr><td>Degradation: {1:'''+PREC+'''} ha</td></tr>
</table>
</div>
<br/>
<div class="result">
<h3>Forest areas affected by changes &dash; Recent</h3>
<!--
<table>
<tr><th>Total</th><th>Annual</th></tr>
<tr><td>Deforestation: {4:'''+PREC+'''} ha</td><td> {6:'''+PREC+'''} ha/y</td></tr>
<tr><td>Degradation: {5:'''+PREC+'''} ha</td><td> {7:'''+PREC+'''} ha/y</td></tr>
</table>
-->
<table>
<tr><th>Total</th></tr>
<tr><td>Deforestation: {4:'''+PREC+'''} ha</td></tr>
<tr><td>Degradation: {5:'''+PREC+'''} ha</td></tr>
</table>
</div>
<br/>
<div class="result">
<h3>Forest areas affected by changes &dash; Historical and Recent</h3>
Degradation: {18:'''+PREC+'''} ha
</div>
'''
report_section_per_MMU['FR']='''
<h2>1.2 &Eacute;missions par UCM</h2>
<div class="result">
<h3>&Eacute;missions &dash; Historique</h3>
<table>
<tr><th>Total</th><th>Annuel</th></tr>
<tr><td>D&eacute;forestation : {8:'''+PREC+'''} tEqCO<sub>2</sub></td><td> {10:'''+PREC+'''} tEqCO<sub>2</sub>/an</td></tr>
<tr><td>D&eacute;gradation : {9:'''+PREC+'''} tEqCO<sub>2</sub></td><td> {11:'''+PREC+'''} tEqCO<sub>2</sub>/an</td></tr>
</table>
</div>
<br/>
<div class="result">
<h3>&Eacute;missions &dash; R&eacute;cente</h3>
<table>
<tr><th>Total</th><th>Annuel</th></tr>
<tr><td>D&eacute;forestation : {12:'''+PREC+'''} tEqCO<sub>2</sub></td><td> {14:'''+PREC+'''} tEqCO<sub>2</sub>/an</td></tr>
<tr><td>D&eacute;gradation : {13:'''+PREC+'''} tEqCO<sub>2</sub></td><td> {15:'''+PREC+'''} tEqCO<sub>2</sub>/an</td></tr>
</table>
</div>
<br/>
<h1>2. Surfaces de for&ecirc;t affect&eacute;es par la d&eacute;forestation et la d&eacute;gradation</h1>
Ces surfaces sont calcul&eacute;es sur la base du nombre de UCM qui changent au cours des p&eacute;riodes d'analyses &dash; Ces donn&eacute;es ne doivent pas &ecirc;tre utilis&eacute;es pour calculer les &eacute;missions, mais fournissent une vue d'ensemble sur les tendances.
<div class="result">
Aires de for&ecirc;t pour {16} : {17:'''+PREC+'''} ha<br/>
</div>
<br/>
<div class="result">
<h3>Surfaces de for&ecirc;t affect&eacute;es par le changement  &dash; Historique</h3>
<!--
<table>
<tr><th>Total</th><th>Annuel</th></tr>
<tr><td>D&eacirc;forestation : {0:'''+PREC+'''} ha</td><td> {2:'''+PREC+'''} ha/an</td></tr>
<tr><td>D&eacirc;gradation : {1:'''+PREC+'''} ha</td><td> {3:'''+PREC+'''} ha/an</td></tr>
</table>
-->
<table>
<tr><th>Total</th></tr>
<tr><td>D&eacute;forestation : {0:'''+PREC+'''} ha</td></tr>
<tr><td>D&eacute;gradation : {1:'''+PREC+'''} ha</td></tr>
</table>
</div>
<br/>
<div class="result">
<h3>Surfaces de for&ecirc;t affect&eacute;es par le changement &dash; R&eacute;cente</h3>
<!--
<table>
<tr><th>Total</th><th>Annual</th></tr>
<tr><td>D&eacute;forestation : {4:'''+PREC+'''} ha</td><td> {6:'''+PREC+'''} ha/an</td></tr>
<tr><td>D&eacute;gradation : {5:'''+PREC+'''} ha</td><td> {7:'''+PREC+'''} ha/an</td></tr>
</table>
-->
<table>
<tr><th>Total</th></tr>
<tr><td>D&eacute;forestation : {4:'''+PREC+'''} ha</td></tr>
<tr><td>D&eacute;gradation : {5:'''+PREC+'''} ha</td></tr>
</table>
</div>
<br/>
<div class="result">
<h3>Surfaces de for&ecirc;t affect&eacute;es par le changement &dash; Historique et R&eacute;cente</h3>
D&eacute;gradation: {18:'''+PREC+'''} ha
</div>
'''
report_section_per_MMU['PT']=report_section_per_MMU['EN']

# ____________________
report_conversion_px_mmu = {'EN':'', 'FR':'', 'PT':''}
report_conversion_px_mmu['EN']='''
<h2>Forest conversion at pixel level, per MMU</h2>
This section accounts for MMU classified as degraded or deforested. For those MMU, the total areas of deforested or degraded pixels are reported.<br/>
<h3>Deforestation</h3>
<p>Deforestation pixels, period P1 = {0:'''+PREC+'''} ha<br/> Deforestation pixels, period P2 = {1:'''+PREC+'''} ha<br/> </p>
<h3>Degradation</h3>
<p>Degradation pixels, period P1 = {2:'''+PREC+'''} ha<br/> Degradation pixels, period P2 = {3:'''+PREC+'''}  ha<br/> </p>
<h3>No changes</h3>
<p>Forest to Forest = {4:'''+PREC+'''} ha<br/>Non-forest to non-forest = {5:'''+PREC+'''} ha<br/>No data = {6:'''+PREC+'''} ha</p>
'''
report_conversion_px_mmu['FR']=''
report_conversion_px_mmu['PT']=report_conversion_px_mmu['EN']
#______________________
report_rates_px_mmu = {'EN':'', 'FR':'', 'PT':''}
report_rates_px_mmu['EN']='''
<h2>Annual rates of forest conversion, at pixel level, per MMU</h2>
<h3>Deforestation</h3>
<p>Rate deforestation pixels, P1 = {0:'''+PREC+'''} ha/year<br/>Rate deforestation pixels, P2 = {1:'''+PREC+'''} ha/year</p>
<h3>Degradation</h3>
<p>Rate degradation pixels, P1 = {2:'''+PREC+'''} ha/year<br/>
Rate degradation pixels, P2 = {3:'''+PREC+'''} ha/year<br/></p>
'''
report_rates_px_mmu['FR']='''
'''
report_rates_px_mmu['PT']=['EN']

#_________________________
report_conversion_mmu = {'EN':'', 'FR':'', 'PT':''}
report_conversion_mmu['EN']='''
<h2>Forest conversion per MMU</h2>
This section lists the count of MMU classified either as deforested or as degraded. For each class, the whole MMU area is used.
<h3>Deforestation</h3>
<p>Deforestation, period P1 = {0:'''+PREC+'''} ha<br/>Deforestation, period P2 = {1:'''+PREC+'''} ha</p>
<h3>Degradation</h3>
<p>Degradation, period P1 = {2:'''+PREC+'''} ha<br/>Degradation, period P2 = {3:.'''+PREC+'''} ha <br/>Degradation, period P1 and P2 = {4:'''+PREC+'''} ha</p>
<h3>No changes</h3>
<p>Forest to forest = {5:'''+PREC+'''} ha<br/>Non-forest to non-forest = {6:'''+PREC+'''} ha</p>
'''
report_conversion_mmu['FR']='''
'''
report_conversion_mmu['PT']=report_conversion_mmu['PT']

#____________________________
report_rates_conversion_mmu = {'EN':'', 'FR':'', 'PT':''}
report_rates_conversion_mmu['EN']='''
<h2>Annual rates of forest conversion per MMU</h2>
<h3>Deforestation</h3>
<p>Annual rate of deforestation, period P1 = {0:'''+PREC+'''}  tons per year<br/>
Annual rate of deforestation, period P2 = {1:'''+PREC+'''} tons per year</p>
<h3>Degradation</h3>
<p>Annual rate of degradation, period P1 = {2:'''+PREC+'''} tons per year<br/>
Annual rate of degradation, period P2 = {3:'''+PREC+'''} tons per year</p>
'''
report_rates_conversion_mmu['FR']='''
'''
report_rates_conversion_mmu['PT']=report_rates_conversion_mmu['EN']
#_____________________________
report_emission_mmu = {'EN':'', 'FR':'', 'PT':''}
report_emission_mmu['EN']='''
<h2>Emissions per MMU</h2>
The emissions of deforestation and degradation are calculated with the number of pixels identified as changed in the MMU boxes
labelled as Deforestation or Degradation and the emission factor (tons of Carbon per hectares) indicated in the input data<br/>
<h3>Deforestation</h3>
<p>Emission from deforestation, Period P1 = {0:'''+PREC+'''} tons</br>Emission from deforestation, period P2 = {1:'''+PREC+'''} tons<p/>
<h3>Degradation</h3>
<p>Emission from degradation, Period P1 = {2:'''+PREC+'''} tons<br/>Emission from degradation, period P2 = {3:'''+PREC+'''} tons</p>
'''
report_emission_mmu['FR']='''
'''
report_emission_mmu['PT']=report_emission_mmu['EN']
#_____________________________
report_annual_emission_rates = {'EN':'', 'FR':'', 'PT':''}
report_annual_emission_rates['EN'] = '''
<h2>Annual emission rates</h2>
<p><b>Deforestation</b></p>
<p>Emission rates from deforestation, period P1 = {0:'''+PREC+'''} tons per year<br/>Emission rates from deforestation, P2 = {1:'''+PREC+'''} tons per year</p>
<p><b>Degradation</b></p>
<p>Emission rates from degradation, period P1 = {2:'''+PREC+'''} tons per year<br/>Emission rates from degradatation, period P2 = {3:'''+PREC+'''} tons per year</p>
'''
report_annual_emission_rates['FR']='''
'''
report_annual_emission_rates['PT']=report_annual_emission_rates['EN']

# ---- formatting functions
def disagString(LANG, EMDisag, toEqCo2):
    tabHead = {'EN':'','FR':'','PT':''}
    tabHead['EN'] = 'Forest Conversion per Strata'
    tabHead['PT'] = tabHead['EN']
    tabHead['FR'] = 'Conversion de for&ecirc;t par strate'
    degP1Title = {'EN': 'Degradation (historical)','FR':'D&eacute;gradation (historique)','PT':'Degradation (historical)'}
    degP2Title = {'EN': 'Degradation (recent)', 'FR': 'D&eacute;gradation (r&eacute;cent)',
                  'PT': 'Degradation (recent)'}
    defP1Title = {'EN': 'deforestation (historical)', 'FR': 'D&eacute;forestation (historique)',
                  'PT': 'deforestation (historical)'}
    defP2Title = {'EN': 'Deforestation (recent)', 'FR': 'D&eacute;forestation (r&eacute;cent)',
                  'PT': 'Deforestation (recent)'}

    headerRow = {'EN': '<tr><th>Strata</th><th>Area (ha)</th><th>Emissions (tEqCO<sub>2</sub>/ha)</th></tr>',
                 'FR': '<tr><th>Strata</th><th>Aire (ha)</th><th>&Eacute;missions (tEqCO<sub>2</sub>/ha)</th></tr>',
                 'PT': '<tr><th>Strata</th><th>Area (ha)</th><th>Emissions (tEqCO<sub>2</sub>/ha)</th></tr>'}

    rowsDefP1 = ''
    rowsDefP2 = ''
    rowsDegP1 = ''
    rowsDegP2 = ''
    for ii in EMDisag['disagElements']:
        thisClass = EMDisag['disagElements'][ii]
        rowsDefP1 += '<tr><td>{}</td><td>{}</td><td>{}</td></tr>'.format(thisClass, int(EMDisag['ArDefP1'][thisClass]),
                                                                         int(toEqCo2 * EMDisag['EmDefP1'][thisClass]))
        rowsDefP2 += '<tr><td>{}</td><td>{}</td><td>{}</td></tr>'.format(thisClass, int(EMDisag['ArDefP2'][thisClass]),
                                                                         int(toEqCo2 * EMDisag['EmDefP2'][thisClass]))
        rowsDegP1 += '<tr><td>{}</td><td>{}</td><td>{}</td></tr>'.format(thisClass, int(EMDisag['ArDegP1'][thisClass]),
                                                                        int(toEqCo2 * EMDisag['EmDegP1'][thisClass]))
        rowsDegP2 += '<tr><td>{}</td><td>{}</td><td>{}</td></tr>'.format(thisClass, int(EMDisag['ArDegP2'][thisClass]),
                                                                       int(toEqCo2 * EMDisag['EmDegP2'][thisClass]))
    finalString = '''
    <h1>{}</h1>
    <h2>{}<h2>
    <div class="result">
        <table>
        {}
        {}
        </table>
    </div>
    <h2>{}</h2>
    <div class="result">
        <table>
        {}
        {}
        </table>
    </div>
    <h2>{}</h2>
    <div class="result">
        <table>
        {}
        {}
        </table>
    </div>
    <br/> 
    <h2>{}</h2>
    <div class="result">
        <table>
        {}
        {}
        </table>
    </div>
    <br/> 
    </div>
    '''.format(tabHead[LANG],
               defP1Title[LANG], headerRow[LANG], rowsDefP1,
               defP2Title[LANG], headerRow[LANG], rowsDefP2,
               degP1Title[LANG], headerRow[LANG], rowsDegP1,
               degP2Title[LANG], headerRow[LANG], rowsDegP2)

    return finalString

def exceptString(LANG, uniqExceptCount):
    tabHead = {'EN': '', 'FR': '', 'PT': ''}
    tabHead['EN'] = 'Exceptions'
    tabHead['PT'] = tabHead['EN']
    tabHead['FR'] = 'Exceptions'
    exceptName = {'EN': 'Exception', 'FR': 'Exception', 'PT': 'Exception'}
    areaName = {'EN': 'area (ha)', 'FR': 'aire (ha)', 'PT': 'aire (ha)'}

    dataString = ''
    for ii in uniqExceptCount:
        dataString += '<tr><td>{}</td><td>{}</td></tr>'.format(ii, uniqExceptCount[ii])

    finalString='''
<h1>{}</h1>
<div class="result">
<table>
<tr><th>{}</th><th>{}</th></tr>
{}
</table>
</div><br/>
    '''.format(tabHead[LANG], exceptName[LANG], areaName[LANG], dataString)

    return finalString
#_________________________________________________________
# ORIGINAL SCRAP
# ________________________________________________________
#'''
#                    <h1>2/ Forest conversion and Emissions per Minimum Mapping Units (MMU) of forest</h1>
#                    <h2>Forest conversion at pixel level, per MMU</h2>
#                    This section accounts for MMU classified as degraded or deforested. For those MMU, the total areas of deforested or degraded pixels are reported.<br/>
#                    <h3>Deforestation</h3>
#                    <p>Deforestation pixels, period P1 = ''' + '{0:.3f}'.format(PXPTOT['Deforest_p1']*sqrps_ha) + ' ha<br/>' + 'Deforestation pixels, period P2 = ' + '{0:.3f}'.format(PXPTOT['Deforest_p2']*sqrps_ha) + ' ha<br/>' + '''</p>
#                    <h3>Degradation</h3>
#                    <p>Degradation pixels, period P1 = ''' + '{0:.3f}'.format(PXPTOT['Degrad_p1']*sqrps_ha) + ' ha<br/>' + 'Degradation pixels, period P2 = ' + '{0:.3f}'.format(PXPTOT['Degrad_p2']*sqrps_ha) + ' ha<br/>' + '''</p>
#                    <h3>No changes</h3>
#                    <p>Forest to Forest = ''' + '{0:.3f}'.format( (PXPTOT['FF_10'] + PXPTOT['FF_2x'] + PXPTOT['FF_3x']) * sqrps_ha) + ' ha<br/>Non-forest to non-forest = '+ '{0:.3f}'.format( (PXPTOT['FF_4x'] + PXPTOT['NF_10'] + PXPTOT['NF_2x'] + PXPTOT['NF_3x'] + PXPTOT['NF_4x'] + PXPTOT['FNF1_4x'] + PXPTOT['FNF2_4x'])*sqrps_ha ) +''' ha</p>
#                    <p>No data = '''+ '{0:.3f}'.format( (PXPTOT['ND_0x'] + PXPTOT['ND_1x']+PXPTOT['ND_2x']+PXPTOT['ND_3x']+PXPTOT['ND_4x'])*sqrps_ha )+ ''' ha</p>

#                    <p>Total pixel count='''+ '{0}'.format(totalPXPTOT) + ''' pixels, '''+ '{0:.6f}'.format(totalPXPTOT * sqrps_ha)+ ''' ha</p>
#                    <h2>Annual rates of forest conversion, at pixel level, per MMU</h2>
#                    <h3>Deforestation</h3>
#                    <p>Rate deforestation pixels, P1 = ''' + '{0:.3f}'.format(PXPTOT['Deforest_p1']*sqrps_ha/deltaYY1) +''' ha/year<br/>
#                    Rate deforestation pixels, P2 = ''' + '{0:.3f}'.format(PXPTOT['Deforest_p2']*sqrps_ha/deltaYY2)+ ''' ha/year<br/></p>
#                    <h3>Degradation</h3>
#                    <p>Rate degradation pixels, P1 = ''' + '{0:.3f}'.format(PXPTOT['Degrad_p1']*sqrps_ha/deltaYY1) +''' ha/year<br/>
#                    Rate degradation pixels, P2 = ''' + '{0:.3f}'.format(PXPTOT['Degrad_p2']*sqrps_ha/deltaYY2) +''' ha/year<br/></p>
#
#                    <h2>Forest conversion per MMU</h2>
#                    This section lists the count of MMU classified either as deforested or as degraded. For each class, the whole MMU area is used.
#                    <h3>Deforestation</h3>
#                    <p>Deforestation, period P1 = ''' + '{0:.3f}'.format( (CLASSTOT['21'] + CLASSTOT['24']) * bxsize_ha ) +' ha<br/>Deforestation, period P2 = '+ '{0:.3f}'.format( (CLASSTOT['22'] + CLASSTOT['23']) * bxsize_ha ) +'''</p>
#                    <h3>Degradation</h3>
#                    <p>Degradation, period P1 = ''' + '{0:.3f}'.format(CLASSTOT['31'] * bxsize_ha) +' ha<br/> Degradation, period P2 = ' + '{0:.3f}'.format( CLASSTOT['32']*bxsize_ha) + ' ha <br/>Degradation, period P1 and P2 = '+ '{0:.3f}'.format(CLASSTOT['33'] * bxsize_ha) +'''</p>
#                    <h3>No changes</h3>
#                    <p>Forest to forest = '''+ '{0:.3f}'.format(CLASSTOT['10'] * bxsize_ha) +'ha<br/>Non-forest to non-forest ='+ '{0:.3f}'.format( (CLASSTOT['41'] + CLASSTOT['42'] + CLASSTOT['43'] + CLASSTOT['44']) *bxsize_ha) +'''ha</p>
#                    <!-- <p>No data =''' + '{0:.3f}'.format( CLASSTOT['0'] *bxsize_ha ) + ''' ha<br/>Unclassified = ''' + '{0:.3f}'.format(CLASSTOT['99'] * bxsize_ha) +'''ha</p>
#                    -->
#                    <h2>Annual rates of forest conversion per MMU</h2>
#                    <h3>Deforestation</h3>
#                    <p>Annual rate of deforestation, period P1 = ''' + '{0:.3f}'.format( (CLASSTOT['21'] + CLASSTOT['24']) * bxsize_ha/deltaYY1 ) + '''<br/>
#                    Annual rate of deforestation, period P2 = ''' + '{0:.3f}'.format( (CLASSTOT['22'] + CLASSTOT['23']) * bxsize_ha/deltaYY2 )+ '''</p>
#                    <h3>Degradation</h3>
#                    <p>Annual rate of degradation, period P1 = ''' + '{0:.3f}'.format(CLASSTOT['31'] * bxsize_ha/deltaYY1)+ '''<br/>
#                    Annual rate of degradation, period P2 = ''' + '{0:.3f}'.format( CLASSTOT['32']*bxsize_ha/deltaYY2)+ '''</p>
#
#                    <h2>Emissions per MMU</h2>
#                    The emissions of deforestation and degradation are calculated with the number of pixels identified as changed in the MMU boxes
#                    labelled as Deforestation or Degradation and the emission factor (tons of Carbon per hectares) indicated in the input data<br/>
#                    <h3>Deforestation</h3>
#                    <p>Emission from deforestation, Period P1 ='''+ '{0:.3f}'.format(PXPTOT['Deforest_p1'] * biomass_valuePx) +' tons</br>Emission from deforestation, period P2 =' + '{0:.3f}'.format(PXPTOT['Deforest_p2'] * biomass_valuePx) +''' tons<p/>
#                    <h3>Degradation</h3>
#                    <p>Emission from degradation, Period P1 = ''' + '{0:.3f}'.format(PXPTOT['Degrad_p1'] *  biomass_valuePx)+''' tons<br/>Emission from degradation, period P2 = '''+ '{0:.3f}'.format( PXPTOT['Degrad_p2']* biomass_valuePx)+''' tons</p>

#<!--
#                    <h1>Rates per year - AREA</h1>
#                    <h2>Pixel based</h2>
#                    <p>Rate Forest to Non-Forest P1  = '''+ '{0:.3f}'.format( (FNF1TOT *sqrps_ha / deltaYY1) )+ ''' ha per year<br/> Rate Forest to Non-Forest P2 = ''' + '{0:.3f}'.format( FNF2TOT *sqrps_ha / deltaYY2 ) + ''' ha per year</p>

#                    <h2>Box based</h2>
#                    <h3>Pixel in the boxes</h3>
#                    <p><b>Deforestation</b></p>
#                    <p>Rate deforestation pixel P1 =''' + '{0:.3f}'.format(PXPTOT['Deforest_p1'] *sqrps_ha /deltaYY1) +''' ha per year<br/>Rate deforestation pixel P2 = ''' + '{0:.3f}'.format(PXPTOT['Deforest_p2'] *sqrps_ha /deltaYY2) +''' ha per year</p>
#                    <p><b/>Degradation</b></p>
#                    <p>Rate degradation pixel P1 =''' + '{0:.3f}'.format(PXPTOT['Degrad_p1'] *sqrps_ha /deltaYY1) +''' ha per year<br/> Rate degradation pixel P2 = ''' + '{0:.3f}'.format(PXPTOT['Degrad_p2'] *sqrps_ha /deltaYY2) +''' ha per year</p>

#                    <h3>Box</h3>
#                    <p><b>Deforestation</b></p>
#                    <p>Rate Deforestation, P1 = ''' + '{0:.3f}'.format(CLASSTOT['21'] *bxsize_ha /deltaYY1) + ''' ha per year<br/>Rate Deforestation, P2 = '''+ '{0:.3f}'.format(CLASSTOT['22'] * bxsize_ha /deltaYY2) +''' ha per year</p>
#                    <p><b>Degradation</b></p>
#                    <p>Rate Degradation, P1 = ''' + '{0:.3f}'.format(CLASSTOT['31'] *bxsize_ha /deltaYY1) + ''' ha per year<br/>Rate Degradation, P2 = '''+ '{0:.3f}'.format( (CLASSTOT['32'] + 0.5*CLASSTOT['33'])*bxsize_ha /deltaYY2) + ''' ha per year</p>
#-->

#                    <h2>Annual emission rates</h2>
#                    <p><b>Deforestation</b></p>
#                    <p>Emission rates from deforestation, period P1 = ''' +'{0:.3f}'.format(PXPTOT['Deforest_p1'] * biomass_valuePx / deltaYY1) +''' tons per year<br/>Emission rates from deforestation, P2 = ''' + '{0:.3f}'.format(PXPTOT['Deforest_p2'] * biomass_valuePx / deltaYY2) +''' tons per year</p>
#                    <p><b>Degradation</b></p>
#                    <p>Emission rates from degradation, period P1 = ''' + '{0:.3f}'.format(PXPTOT['Degrad_p1'] * biomass_valuePx/deltaYY1)+''' tons per year<br/>Emission rates from degradatation, period P2 = '''+ '{0:.3f}'.format( PXPTOT['Degrad_p2']*biomass_valuePx/deltaYY2)+''' tons per year</p>
#'''
