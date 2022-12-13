import re

tds = ['<td rowspan="1" class="k t"><a href="cur_geral.cur_view?pv_curso_id=24082&amp;pv_ano_lectivo=2022">IADP</a></td>',
 '<td rowspan="1" class="n">1</td>',
 '<td rowspan="1" class="t"><a href="cur_geral.cur_planos_estudos_view?pv_plano_id=32144&amp;pv_ano_lectivo=2022">Plano de estudos oficial</a></td>',
 '<td rowspan="1" class="l">1</td>',
 '<td rowspan="1" class="l"> - </td>',
 '<td rowspan="1" class="n">1,5</td>',
 '<td rowspan="1" class="l"> - </td>',
 '<td rowspan="1" class="n">4</td>',
 '<td rowspan="1" class="k t"><a href="cur_geral.cur_view?pv_curso_id=22801&amp;pv_ano_lectivo=2022">L.BIO</a></td>',
 '<td rowspan="1" class="n">2</td>',
 '<td rowspan="1" class="t"><a href="cur_geral.cur_planos_estudos_view?pv_plano_id=30864&amp;pv_ano_lectivo=2022">Plano Oficial do ano letivo</a></td>',
 '<td rowspan="1" class="l">3</td>',
 '<td rowspan="1" class="l"> - </td>',
 '<td rowspan="1" class="n">1,5</td>',
 '<td rowspan="1" class="l"> - </td>',
 '<td rowspan="1" class="n">4</td>',
 '<td rowspan="1" class="k t"><a href="cur_geral.cur_view?pv_curso_id=22803&amp;pv_ano_lectivo=2022">L.EA</a></td>',
 '<td rowspan="1" class="n">10</td>',
 '<td rowspan="1" class="t"><a href="cur_geral.cur_planos_estudos_view?pv_plano_id=30904&amp;pv_ano_lectivo=2022">Plano Oficial</a></td>',
 '<td rowspan="1" class="l">2</td>',
 '<td rowspan="1" class="l"> - </td>',
 '<td rowspan="1" class="n">1,5</td>',
 '<td rowspan="1" class="l"> - </td>',
 '<td rowspan="1" class="n">4</td>',
 '<td rowspan="1" class="k t"><a href="cur_geral.cur_view?pv_curso_id=22802&amp;pv_ano_lectivo=2022">L.EC</a></td>',
 '<td rowspan="1" class="n">51</td>',
 '<td rowspan="1" class="t"><a href="cur_geral.cur_planos_estudos_view?pv_plano_id=31004&amp;pv_ano_lectivo=2022">Plano de estudos oficial</a></td>',
 '<td rowspan="1" class="l">2</td>',
 '<td rowspan="1" class="l"> - </td>',
 '<td rowspan="1" class="n">1,5</td>',
 '<td rowspan="1" class="l"> - </td>',
 '<td rowspan="1" class="n">4</td>',
 '<td rowspan="1" class="k t"><a href="cur_geral.cur_view?pv_curso_id=22823&amp;pv_ano_lectivo=2022">L.EEC</a></td>',
 '<td rowspan="1" class="n">118</td>',
 '<td rowspan="1" class="t"><a href="cur_geral.cur_planos_estudos_view?pv_plano_id=31024&amp;pv_ano_lectivo=2022">Plano Oficial</a></td>',
 '<td rowspan="1" class="l">2</td>',
 '<td rowspan="1" class="l"> - </td>',
 '<td rowspan="1" class="n">1,5</td>',
 '<td rowspan="1" class="l"> - </td>',
 '<td rowspan="1" class="n">4</td>',
 '<td rowspan="1" class="k t"><a href="cur_geral.cur_view?pv_curso_id=22863&amp;pv_ano_lectivo=2022">L.EGI</a></td>',
 '<td rowspan="1" class="n">26</td>',
 '<td rowspan="1" class="t"><a href="cur_geral.cur_planos_estudos_view?pv_plano_id=30664&amp;pv_ano_lectivo=2022">Plano Oficial do ano letivo</a></td>',
 '<td rowspan="1" class="l">2</td>',
 '<td rowspan="1" class="l"> - </td>',
 '<td rowspan="1" class="n">1,5</td>',
 '<td rowspan="1" class="l"> - </td>',
 '<td rowspan="1" class="n">4</td>',
 '<td rowspan="2" class="k t"><a href="cur_geral.cur_view?pv_curso_id=22841&amp;pv_ano_lectivo=2022">L.EIC</a></td>',
 '<td rowspan="2" class="n">127</td>',
 '<td rowspan="2" class="t"><a href="cur_geral.cur_planos_estudos_view?pv_plano_id=31224&amp;pv_ano_lectivo=2022">Plano Oficial</a></td>',
 '<td rowspan="1" class="l">2</td>',
 '<td rowspan="2" class="l"> - </td>',
 '<td rowspan="2" class="n">1,5</td>',
 '<td rowspan="2" class="l"> - </td>',
 '<td rowspan="2" class="n">4</td>',
 '<td rowspan="1" class="l">3</td>',
 '<td rowspan="1" class="k t"><a href="cur_geral.cur_view?pv_curso_id=22882&amp;pv_ano_lectivo=2022">L.EM</a></td>',
 '<td rowspan="1" class="n">11</td>',
 '<td rowspan="1" class="t"><a href="cur_geral.cur_planos_estudos_view?pv_plano_id=30744&amp;pv_ano_lectivo=2022">Plano de Estudos Oficial</a></td>',
 '<td rowspan="1" class="l">3</td>',
 '<td rowspan="1" class="l"> - </td>',
 '<td rowspan="1" class="n">1,5</td>',
 '<td rowspan="1" class="l"> - </td>',
 '<td rowspan="1" class="n">4</td>',
 '<td rowspan="1" class="k t"><a href="cur_geral.cur_view?pv_curso_id=22902&amp;pv_ano_lectivo=2022">L.EMAT</a></td>',
 '<td rowspan="1" class="n">2</td>',
 '<td rowspan="1" class="t"><a href="cur_geral.cur_planos_estudos_view?pv_plano_id=31284&amp;pv_ano_lectivo=2022">Plano Oficial do ano letivo 2021</a></td>',
 '<td rowspan="1" class="l">3</td>',
 '<td rowspan="1" class="l"> - </td>',
 '<td rowspan="1" class="n">1,5</td>',
 '<td rowspan="1" class="l"> - </td>',
 '<td rowspan="1" class="n">4</td>',
 '<td rowspan="2" class="k t"><a href="cur_geral.cur_view?pv_curso_id=738&amp;pv_ano_lectivo=2022">L.EMG</a></td>',
 '<td rowspan="2" class="n">0</td>',
 '<td rowspan="2" class="t"><a href="cur_geral.cur_planos_estudos_view?pv_plano_id=2788&amp;pv_ano_lectivo=2022">Plano de estudos oficial a partir de 2008/09</a></td>',
 '<td rowspan="1" class="l">2</td>',
 '<td rowspan="2" class="l"> - </td>',
 '<td rowspan="2" class="n">1,5</td>',
 '<td rowspan="2" class="l"> - </td>',
 '<td rowspan="2" class="n">4</td>',
 '<td rowspan="1" class="l">3</td>']

r'>.*</a>'

i = 0
tds_len = len(tds)

course_units = {}

while (i < tds_len):

    acronym = re.search('>(\D*)<\/a>', tds[i]).group(1)
    course_units[acronym] = []
    num_rows = int(re.search('rowspan="(\d)"', tds[i]).group(1))
    for j in range(7 + num_rows - 1):
        if (j == 1 or j >= 7):
            course_units[acronym].append(tds[i][tds[i].find('>')+1])
        i+=1
    
    print(acronym)
    i+=1

print(course_units)

