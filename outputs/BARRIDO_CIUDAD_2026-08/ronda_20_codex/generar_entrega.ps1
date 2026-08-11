$ErrorActionPreference = 'Stop'

$destino = $PSScriptRoot
$raiz = Split-Path $destino -Parent
$catalogoPath = Join-Path $raiz 'desde_cowork/evidencia_2026/catalogo_90_estado_final.csv'
$capaPath = Join-Path $raiz 'hitos/hitos_capa_2026.geojson'
$localesPreviosPath = Join-Path $raiz 'ronda_19_codex/verificacion_locales_ronda_19.csv'

$catalogo = Import-Csv -LiteralPath $catalogoPath
$capa = (Get-Content -Raw -LiteralPath $capaPath | ConvertFrom-Json).features
$localesPrevios = Import-Csv -LiteralPath $localesPreviosPath

if ($catalogo.Count -ne 90) { throw "El catálogo esperado tiene 90 filas; se leyeron $($catalogo.Count)." }
if ($capa.Count -ne 215) { throw "La capa esperada tiene 215 objetos; se leyeron $($capa.Count)." }
if (($capa | Where-Object { $null -eq $_.geometry }).Count -ne 0) { throw 'La capa contiene objetos sin geometría.' }
if ($localesPrevios.Count -ne 19) { throw "El insumo previo esperado tiene 19 filas; se leyeron $($localesPrevios.Count)." }

$fuenteKosher = 'https://turismo.buenosaires.gob.ar/sites/turismo/files/establecimientos_KOSHER_2015_0.pdf'
$fuenteVillaLuro = 'https://www.infogastronomica.com.ar/villa-luro-los-nuevos-bares-y-restaurantes-de-un-polo-gastronomico-que-no-para-de-crecer/'
$fuentePasaje = 'https://www.lanacion.com.ar/sabado/pasaje-ruperto-godoy-el-patio-de-comidas-coreano-del-shopping-a-cielo-abierto-que-se-creo-alrededor-nid15062023/'
$fuenteCimino = 'https://www.lanacion.com.ar/la-nacion-revista/sabores-unicos-quienes-son-y-como-trabajan-los-nuevos-alquimistas-del-helado-nid19022022/'
$fuenteMakarios = 'https://www.c5n.com/lifestyle/la-parrilla-buenos-aires-comer-asados-economicos-y-muy-ricos-n146679'

$locales = @(
    [pscustomobject]@{ polo='Flores · Avellaneda y Pasaje Ruperto Godoy'; nombre='American Kosher'; direccion='Av. Avellaneda 2701'; grupo='registro_kosher_2015'; antecedente_fecha='2015'; resultado='sin_evidencia_publica_fechada_posterior'; estado='vigencia_no_verificada'; nivel_de_verificacion='v2'; fuente_valida=$fuenteKosher; fecha_fuente_valida='2015'; consulta_documentada='"American Kosher" "Avellaneda 2701"; "American Kosher" Flores Buenos Aires 2024 2025 2026'; resultado_de_la_busqueda='No se localizó una pieza editorial pública, fechada y posterior a 2015 que individualice nombre y domicilio.'; superficies_no_suficientes='Directorios, mapas y fichas sin fecha editorial; no prueban actividad.'; fecha_revision='2026-08-10'; observaciones='Se conserva el antecedente oficial de 2015. La ausencia de una pieza posterior no se interpreta como cierre.' }
    [pscustomobject]@{ polo='Flores · Avellaneda y Pasaje Ruperto Godoy'; nombre='Kosher City'; direccion='Av. Avellaneda 2395'; grupo='registro_kosher_2015'; antecedente_fecha='2015'; resultado='sin_evidencia_publica_fechada_posterior'; estado='vigencia_no_verificada'; nivel_de_verificacion='v2'; fuente_valida=$fuenteKosher; fecha_fuente_valida='2015'; consulta_documentada='"Kosher City" "Avellaneda 2395"; "Kosher City" Flores Buenos Aires 2024 2025 2026'; resultado_de_la_busqueda='No se localizó una pieza editorial pública, fechada y posterior a 2015 que individualice nombre y domicilio.'; superficies_no_suficientes='Directorios, mapas y fichas sin fecha editorial; no prueban actividad.'; fecha_revision='2026-08-10'; observaciones='Se conserva el antecedente oficial de 2015. La ausencia de una pieza posterior no se interpreta como cierre.' }
    [pscustomobject]@{ polo='Flores · Avellaneda y Pasaje Ruperto Godoy'; nombre='Amltí'; direccion='Bolivia 449'; grupo='registro_kosher_2015'; antecedente_fecha='2015'; resultado='sin_evidencia_publica_fechada_posterior'; estado='vigencia_no_verificada'; nivel_de_verificacion='v2'; fuente_valida=$fuenteKosher; fecha_fuente_valida='2015'; consulta_documentada='("Amltí" OR "Amit") "Bolivia 449" kosher; "Bolivia 449" kosher 2024 2025 2026'; resultado_de_la_busqueda='No se localizó una pieza editorial pública, fechada y posterior a 2015 que individualice nombre y domicilio.'; superficies_no_suficientes='Listados comunitarios sin fecha editorial y directorios; no prueban actividad.'; fecha_revision='2026-08-10'; observaciones='Se buscó también la variante Amit. Se conserva el antecedente oficial de 2015; no se infiere cierre.' }
    [pscustomobject]@{ polo='Flores · Avellaneda y Pasaje Ruperto Godoy'; nombre='Azulay'; direccion='Aranguren 2941'; grupo='registro_kosher_2015'; antecedente_fecha='2015'; resultado='sin_evidencia_publica_fechada_posterior'; estado='vigencia_no_verificada'; nivel_de_verificacion='v2'; fuente_valida=$fuenteKosher; fecha_fuente_valida='2015'; consulta_documentada='"Azulay" "Aranguren 2941" kosher; "Azulay" Flores Buenos Aires 2024 2025 2026'; resultado_de_la_busqueda='No se localizó una pieza editorial pública, fechada y posterior a 2015 que individualice nombre y domicilio.'; superficies_no_suficientes='Un directorio muestra fecha de actualización, no fecha del dato ni prueba de actividad.'; fecha_revision='2026-08-10'; observaciones='Se conserva el antecedente oficial de 2015. La ausencia de una pieza posterior no se interpreta como cierre.' }
    [pscustomobject]@{ polo='Flores · Avellaneda y Pasaje Ruperto Godoy'; nombre='Hamra'; direccion='Aranguren 3192'; grupo='registro_kosher_2015'; antecedente_fecha='2015'; resultado='sin_evidencia_publica_fechada_posterior'; estado='vigencia_no_verificada'; nivel_de_verificacion='v2'; fuente_valida=$fuenteKosher; fecha_fuente_valida='2015'; consulta_documentada='"Hamra" "Aranguren 3192" kosher; "Hamra" Flores Buenos Aires 2024 2025 2026'; resultado_de_la_busqueda='No se localizó una pieza editorial pública, fechada y posterior a 2015 que individualice nombre y domicilio.'; superficies_no_suficientes='Agregadores gastronómicos y directorios; sus estados o fechas de actualización no verifican actividad.'; fecha_revision='2026-08-10'; observaciones='Se conserva el antecedente oficial de 2015. La ausencia de una pieza posterior no se interpreta como cierre.' }
    [pscustomobject]@{ polo='Flores · Avellaneda y Pasaje Ruperto Godoy'; nombre='Behar Almacén'; direccion='Campana 349'; grupo='registro_kosher_2015'; antecedente_fecha='2015'; resultado='sin_evidencia_publica_fechada_posterior'; estado='vigencia_no_verificada'; nivel_de_verificacion='v2'; fuente_valida=$fuenteKosher; fecha_fuente_valida='2015'; consulta_documentada='"Behar Almacén" "Campana 349"; "Behar" "Campana 349" kosher 2024 2025 2026'; resultado_de_la_busqueda='No se localizó una pieza editorial pública, fechada y posterior a 2015 que individualice nombre y domicilio.'; superficies_no_suficientes='Directorio comercial sin fecha editorial; no prueba actividad.'; fecha_revision='2026-08-10'; observaciones='Se conserva el antecedente oficial de 2015. La ausencia de una pieza posterior no se interpreta como cierre.' }
    [pscustomobject]@{ polo='Flores · Avellaneda y Pasaje Ruperto Godoy'; nombre='Soultani'; direccion='Cuenca 515'; grupo='registro_kosher_2015'; antecedente_fecha='2015'; resultado='sin_evidencia_publica_fechada_posterior'; estado='vigencia_no_verificada'; nivel_de_verificacion='v2'; fuente_valida=$fuenteKosher; fecha_fuente_valida='2015'; consulta_documentada='"Soultani" "Cuenca 515" kosher; "Soultani" Flores Buenos Aires 2024 2025 2026'; resultado_de_la_busqueda='No se localizó una pieza editorial pública, fechada y posterior a 2015 que individualice nombre y domicilio.'; superficies_no_suficientes='Listado comunitario con calendario dinámico pero sin fecha editorial de la ficha; no prueba actividad.'; fecha_revision='2026-08-10'; observaciones='Se conserva el antecedente oficial de 2015. La ausencia de una pieza posterior no se interpreta como cierre.' }
    [pscustomobject]@{ polo='Flores · Avellaneda y Pasaje Ruperto Godoy'; nombre='Productos Cohen'; direccion='Cuenca 180'; grupo='registro_kosher_2015'; antecedente_fecha='2015'; resultado='sin_evidencia_publica_fechada_posterior'; estado='vigencia_no_verificada'; nivel_de_verificacion='v2'; fuente_valida=$fuenteKosher; fecha_fuente_valida='2015'; consulta_documentada='"Productos Cohen" "Cuenca 180" kosher; "Cuenca 180" kosher Buenos Aires 2024 2025 2026'; resultado_de_la_busqueda='No se localizó una pieza editorial pública, fechada y posterior a 2015 que individualice nombre y domicilio.'; superficies_no_suficientes='Resultados sin identidad coincidente o sin fecha editorial; no prueban actividad.'; fecha_revision='2026-08-10'; observaciones='Se conserva el antecedente oficial de 2015. La ausencia de una pieza posterior no se interpreta como cierre.' }
    [pscustomobject]@{ polo='Flores · Avellaneda y Pasaje Ruperto Godoy'; nombre='Nacca'; direccion='Argerich 843'; grupo='registro_kosher_2015'; antecedente_fecha='2015'; resultado='sin_evidencia_publica_fechada_posterior'; estado='vigencia_no_verificada'; nivel_de_verificacion='v2'; fuente_valida=$fuenteKosher; fecha_fuente_valida='2015'; consulta_documentada='"Nacca" "Argerich 843" kosher; "Nacca" Flores Buenos Aires 2024 2025 2026'; resultado_de_la_busqueda='No se localizó una pieza editorial pública, fechada y posterior a 2015 que individualice nombre y domicilio.'; superficies_no_suficientes='Ficha de directorio fechada en 2015 y resultados sin fecha editorial posterior; no prueban actividad.'; fecha_revision='2026-08-10'; observaciones='Se conserva el antecedente oficial de 2015. La ausencia de una pieza posterior no se interpreta como cierre.' }
    [pscustomobject]@{ polo='Villa Luro'; nombre='Estación de Milanesas'; direccion='Acassuso 5202'; grupo='locales_con_antecedente_2022_2023'; antecedente_fecha='2023-03-26'; resultado='sin_evidencia_publica_fechada_posterior'; estado='vigencia_no_verificada'; nivel_de_verificacion='v2'; fuente_valida=$fuenteVillaLuro; fecha_fuente_valida='2023-03-26'; consulta_documentada='"Estación de Milanesas" "Acassuso 5202"; "Estación de Milanesas" Villa Luro 2024 2025 2026'; resultado_de_la_busqueda='No se localizó una pieza editorial pública posterior al antecedente de 2023 que individualice el domicilio.'; superficies_no_suficientes='Catálogos de entrega y agregadores, incluido uno con marca de cierre y otro domicilio; no verifican actividad ni cierre.'; fecha_revision='2026-08-10'; observaciones='Se mantiene el antecedente de 2023. La contradicción entre agregadores queda registrada sin adjudicar.' }
    [pscustomobject]@{ polo='Villa Luro'; nombre='García Restaurante'; direccion='García de Cossio 5727'; grupo='locales_con_antecedente_2022_2023'; antecedente_fecha='2023-03-26'; resultado='sin_evidencia_publica_fechada_posterior'; estado='vigencia_no_verificada'; nivel_de_verificacion='v2'; fuente_valida=$fuenteVillaLuro; fecha_fuente_valida='2023-03-26'; consulta_documentada='"García Restaurante" "García de Cossio 5727"; "García Restaurante" Villa Luro 2024 2025 2026'; resultado_de_la_busqueda='No se localizó una pieza editorial pública posterior al antecedente de 2023 que individualice el domicilio.'; superficies_no_suficientes='Agregador gastronómico actualizado en 2023 y directorios; no aportan una prueba posterior.'; fecha_revision='2026-08-10'; observaciones='Se mantiene el antecedente de 2023. No se infiere cierre.' }
    [pscustomobject]@{ polo='Villa Luro'; nombre='Mich Bar'; direccion='Basualdo 103'; grupo='locales_con_antecedente_2022_2023'; antecedente_fecha='2023-03-26'; resultado='sin_evidencia_publica_fechada_posterior'; estado='vigencia_no_verificada'; nivel_de_verificacion='v2'; fuente_valida=$fuenteVillaLuro; fecha_fuente_valida='2023-03-26'; consulta_documentada='"Mich Bar" "Basualdo 103"; "Mich Bar" Villa Luro 2024 2025 2026'; resultado_de_la_busqueda='No se localizó una pieza editorial pública posterior al antecedente de 2023 que individualice el domicilio.'; superficies_no_suficientes='Catálogo de entrega y directorios sin fecha editorial; no prueban actividad.'; fecha_revision='2026-08-10'; observaciones='Se mantiene el antecedente de 2023. No se infiere cierre.' }
    [pscustomobject]@{ polo='Flores · Avellaneda y Pasaje Ruperto Godoy'; nombre='Makarios'; direccion='Felipe Vallese 3130'; grupo='locales_con_antecedente_2022_2023'; antecedente_fecha='2023-06-19'; resultado='evidencia_publica_fechada_localizada'; estado='abierto_a_fecha_fuente'; nivel_de_verificacion='v2'; fuente_valida=$fuenteMakarios; fecha_fuente_valida='2024-02-17'; consulta_documentada='"Makarios" "Felipe Vallese 3130"; "Makarios" Flores parrilla 2024 2025 2026'; resultado_de_la_busqueda='Se localizó una pieza periodística fechada que identifica el establecimiento, el domicilio y su oferta.'; superficies_no_suficientes='No aplica al hallazgo positivo; la pieza no acredita atención al corte de 2026-08-10.'; fecha_revision='2026-08-10'; observaciones='La vigencia documental avanza de 2023-06-19 a 2024-02-17. No equivale a verificación presencial ni a abierto hoy.' }
    [pscustomobject]@{ polo='Flores · Avellaneda y Pasaje Ruperto Godoy'; nombre='Pulpería Norte'; direccion='Felipe Vallese 3123'; grupo='locales_con_antecedente_2022_2023'; antecedente_fecha='2023-06-19'; resultado='sin_evidencia_publica_fechada_posterior'; estado='vigencia_no_verificada'; nivel_de_verificacion='v2'; fuente_valida=$fuentePasaje; fecha_fuente_valida='2023-06-19'; consulta_documentada='"Pulpería Norte" "Felipe Vallese 3123"; "Pulpería Norte" Flores 2024 2025 2026'; resultado_de_la_busqueda='No se localizó una pieza editorial pública posterior al antecedente de 2023 que individualice el domicilio.'; superficies_no_suficientes='Agregador con fecha de actualización 2026 y marca de cierre, más catálogos de entrega; no prueban actividad ni cierre.'; fecha_revision='2026-08-10'; observaciones='Se mantiene el antecedente de 2023. La marca de agregador se registra como indicio no adjudicado.' }
    [pscustomobject]@{ polo='Donado–Holmberg'; nombre='Cimino R'; direccion='Donado 1919'; grupo='locales_con_antecedente_2022_2023'; antecedente_fecha='2022-02-19'; resultado='sin_evidencia_publica_fechada_posterior'; estado='vigencia_no_verificada'; nivel_de_verificacion='v2'; fuente_valida=$fuenteCimino; fecha_fuente_valida='2022-02-19'; consulta_documentada='"Cimino R" "Donado 1919"; "Cimino" "Donado 1919" 2023 2024 2025 2026'; resultado_de_la_busqueda='No se localizó una pieza editorial pública posterior a 2022 que acredite actividad de esa sede.'; superficies_no_suficientes='Permiso municipal otorgado en 2022 por cinco años y directorios actuales: el permiso habilita uso, pero no acredita operación.'; fecha_revision='2026-08-10'; observaciones='Se mantiene el antecedente de 2022. La continuidad de la marca no se atribuye automáticamente a la sede de Donado.' }
)

$locales | Export-Csv -LiteralPath (Join-Path $destino 'verificacion_locales_ronda_20.csv') -NoTypeInformation -Encoding utf8BOM

$fuenteCatalogo = 'https://documentosboletinoficial.buenosaires.gob.ar/publico/PE-RES-MCGC-MCGC-1225-26-ANX.pdf'
$seis = @(
    [pscustomobject]@{ establecimiento='EL ESTANO 1880'; direccion='Aristóbulo del Valle 1100'; polo='fuera_de_soportes'; que_se_busco='"El Estaño 1880" "Aristóbulo del Valle 1100" 2024 2025 2026; sitios oficiales nacional y de la Ciudad'; que_haria_falta='Cumplido para nivel v2; una constatación directa sería necesaria para afirmar abierto al corte.'; por_que_no_aparece='No aplica: se encontró una guía turística oficial, individual, fechada y con domicilio; la búsqueda previa había quedado restringida a fuentes porteñas o fichas sin fecha.'; resultado='abierto_a_fecha_fuente'; fuente='https://www.argentina.travel/novedades/cafes-notables-de-buenos-aires-donde-el-sabor-se-encuentra-con-la-historia'; fecha_fuente='2025-03-25'; nivel_resultante='v2'; observaciones='La pieza usa presente, informa menú, actividades y domicilio. Acredita existencia/actividad a fecha de fuente, no al corte.' }
    [pscustomobject]@{ establecimiento='BAR DEL ALVEAR PALACE HOTEL'; direccion='Av. Alvear 1891'; polo='R06'; que_se_busco='"Bar del Alvear Palace Hotel" 2025 2026; "Lobby Bar" "Alvear 1891" 2025 2026; sitio oficial del hotel y prensa'; que_haria_falta='Pieza individual con fecha editorial o agenda fechada del Lobby Bar que una nombre, domicilio y actividad.'; por_que_no_aparece='La superficie pública lo presenta como servicio interno del hotel dentro de una página general sin fecha editorial. Las notas recuperadas priorizan el hotel o el bar de terraza, no el Bar Notable individual.'; resultado='pendiente_pieza_individual_fechada'; fuente=$fuenteCatalogo; fecha_fuente='2026-02-26'; nivel_resultante='v1'; observaciones='El catálogo confirma pertenencia y domicilio, pero una declaratoria no acredita actividad. No se infiere cierre.' }
    [pscustomobject]@{ establecimiento='PETIT COLON'; direccion='Libertad 505'; polo='R02;R12'; que_se_busco='"Petit Colón" "Libertad 505" 2024 2025 2026; site:buenosaires.gob.ar "Petit Colón"; prensa y agendas culturales'; que_haria_falta='Actividad oficial o pieza editorial fechada posterior al antecedente, con nombre y domicilio.'; por_que_no_aparece='Predominan la ficha turística sin fecha, agregadores y una agenda impresa en 2026 que reproduce un expediente de aniversario de 2023; la fecha de impresión no fecha la actividad del local.'; resultado='pendiente_pieza_individual_fechada'; fuente=$fuenteCatalogo; fecha_fuente='2026-02-26'; nivel_resultante='v1'; observaciones='El catálogo confirma pertenencia y domicilio, pero no actividad. No se infiere cierre.' }
    [pscustomobject]@{ establecimiento='BAR BIDOU'; direccion='Av. Roque Sáenz Peña 858'; polo='R12'; que_se_busco='"Bar Bidou" "Roque Sáenz Peña 858" 2024 2025 2026; "Bidou" "858" prensa'; que_haria_falta='Cumplido para nivel v2; una constatación directa sería necesaria para afirmar abierto al corte.'; por_que_no_aparece='No aplica: se encontró una pieza periodística individual, fechada y con el domicilio exacto.'; resultado='abierto_a_fecha_fuente'; fuente='https://www.infobae.com/sociedad/2025/11/16/cafetines-de-buenos-aires-el-bar-notable-que-desafio-la-cuadricula-portena-y-la-historia-secreta-de-la-avenida-diagonal-norte/'; fecha_fuente='2025-11-16'; nivel_resultante='v2'; observaciones='La pieza describe el establecimiento en presente y ubica el número 858. Acredita actividad a fecha de fuente, no al corte.' }
    [pscustomobject]@{ establecimiento='BOSTON CITY'; direccion='Florida 165 local 3'; polo='fuera_de_soportes'; que_se_busco='"Boston City" "Florida 165" 2025 2026; site:buenosaires.gob.ar "Boston City"; programación de Bares Notables'; que_haria_falta='Cumplido para nivel v2; una constatación directa sería necesaria para afirmar abierto al corte.'; por_que_no_aparece='No aplica: una programación oficial fechada de 2026 lo integra en un recorrido cultural; el catálogo oficial aporta el domicilio exacto.'; resultado='abierto_a_fecha_fuente'; fuente='https://buenosaires.gob.ar/gcaba_historico/noticias/verano-notable-musica-literatura-y-recorridos-culturales-en-los-bares'; fecha_fuente='2026-02-02'; nivel_resultante='v2'; observaciones='La programación individualiza el establecimiento dentro del recorrido. Identidad y domicilio se controlaron con el catálogo oficial de 2026.' }
    [pscustomobject]@{ establecimiento='EL COLECCIONISTA'; direccion='Av. Rivadavia 4929'; polo='fuera_de_soportes'; que_se_busco='"El Coleccionista" "Rivadavia 4929" 2024 2025 2026; site:buenosaires.gob.ar "El Coleccionista"; prensa y agendas culturales'; que_haria_falta='Pieza individual con fecha editorial o actividad oficial fechada que una nombre, domicilio y operación.'; por_que_no_aparece='Los resultados actuales son agregadores con fechas de actualización o reseñas, fichas turísticas sin fecha y registros normativos/patrimoniales. Ninguno fecha la actividad del establecimiento.'; resultado='pendiente_pieza_individual_fechada'; fuente=$fuenteCatalogo; fecha_fuente='2026-02-26'; nivel_resultante='v1'; observaciones='El catálogo confirma pertenencia y domicilio, pero no actividad. No se infiere cierre.' }
)

$seis | Export-Csv -LiteralPath (Join-Path $destino 'seis_pendientes.csv') -NoTypeInformation -Encoding utf8BOM

$saverio = @(
    [pscustomobject]@{ direccion='Av. San Juan 2809'; codigo_calle='20040'; smp='30-083-040A'; pdamatriz='186130'; x='105414.133363'; y='100588.295872'; fuente_tipo='USIG municipal · normalizador y catastro por puerta'; consulta='https://ws.usig.buenosaires.gob.ar/geocoder/2.2/smp?cod_calle=20040&altura=2809'; fecha_consulta='2026-08-10'; resultado='parcela_distinta' }
    [pscustomobject]@{ direccion='Av. San Juan 2816'; codigo_calle='20040'; smp='30-082-004A'; pdamatriz='182937'; x='105450.145098'; y='100575.130453'; fuente_tipo='USIG municipal · normalizador y catastro por puerta'; consulta='https://ws.usig.buenosaires.gob.ar/geocoder/2.2/smp?cod_calle=20040&altura=2816'; fecha_consulta='2026-08-10'; resultado='parcela_distinta' }
)

$saverio | Export-Csv -LiteralPath (Join-Path $destino 'saverio_fuente_municipal.csv') -NoTypeInformation -Encoding utf8BOM

function Nuevo-Caso {
    param($id,$tipo,$canon,$conjuntoA,$nombreA,$direccionA,$idA,$conjuntoB,$nombreB,$direccionB,$idB,$diagnostico,$accion,$fuenteA,$fuenteB)
    [pscustomobject]@{
        caso_id=$id; tipo_hallazgo=$tipo; establecimiento_canonico=$canon
        conjunto_a=$conjuntoA; nombre_a=$nombreA; direccion_a=$direccionA; id_a=$idA
        conjunto_b=$conjuntoB; nombre_b=$nombreB; direccion_b=$direccionB; id_b=$idB
        diagnostico=$diagnostico; accion_sugerida=$accion; fuente_a=$fuenteA; fuente_b=$fuenteB; fecha_revision='2026-08-10'
    }
}

$fc = 'catalogo_90_estado_final.csv'
$fl = 'hitos_capa_2026.geojson'
$cruce = @()
$aliases = @(
    @('ALMACEN Y BAR LAVALLE','Lavalle 1693','Bar Lavalle','H011','variante editorial'),
    @('BARBARO BAR','Tres Sargentos 415','Barbaro','H002','variante editorial'),
    @('BAR BRITANICO','Brasil 399','Britanico','H019','variante editorial'),
    @('BAR EL COLONIAL','Av. Belgrano 599','El Colonial','H008','variante editorial'),
    @('BAR 9 DE JULIO','Larrazabal 1276','9 de Julio','H001','variante editorial'),
    @('BAR OLIMPO','Irigoyen 1491','Café Olimpo','H028','variante confirmada de nombre'),
    @('BAR PORTUARIO','Pinzon 102','El Portuario','H088','variante confirmada de nombre'),
    @('CAFE SAN BERNARDO','Av. Corrientes 5436','San Bernardo','H033','variante editorial'),
    @('CAFE TABAC','Av. del Libertador 2300','Cafetabac','H036','variante confirmada de nombre'),
    @("CLARIDGE'S BAR",'Tucuman 535',"Claridge's",'H039','variante editorial'),
    @('CONFITERIA LA IDEAL','Suipacha 384','Confitería Ideal','H042','variante editorial'),
    @('DON JUAN BAR','Camarones 2702','Don Juan','H025','variante editorial'),
    @('EL BOLICHE DE ROBERTO','Bulnes 331','12 de octubre','H045','alias del mismo establecimiento'),
    @('EL FEDERAL','Carlos Calvo 595','Bar El Federal','H009','variante confirmada de nombre'),
    @('EL HIPOPOTAMO','Brasil 401','Hipopotamo','H051','variante editorial'),
    @('MONTECARLO BAR Y DESPENSA','Paraguay 5491','Café Montecarlo','H027','variante confirmada de nombre'),
    @('MUSEO FOTOGRAFICO SIMIK','Av. Federico Lacroze 3901','Cafe Palacio','H029','renombre confirmado; la capa conserva el nombre anterior'),
    @('OCHO ESQUINAS','Av. Forest 1186','8 Esquinas','H079','variante confirmada de nombre'),
    @("WATSON'S",'Vuelta de Obligado 2072','Casa Watson','H037','variante confirmada de nombre')
)
$i = 1
foreach ($a in $aliases) {
    $cruce += Nuevo-Caso ("C{0:D2}" -f $i) 'nombre_distinto_mismo_domicilio' $a[0] 'catalogo_90' $a[0] $a[1] '' 'capa_reconocimientos_215' $a[2] $a[1] $a[3] $a[4] 'Usar el nombre del catálogo vigente y conservar el otro como alias.' $fc $fl
    $i++
}

$cruce += Nuevo-Caso 'C20' 'domicilio_distinto_entre_conjuntos' 'CAFE ROMA' 'catalogo_90' 'CAFE ROMA' 'Olavarria 409' '' 'capa_reconocimientos_215' 'Café Roma' 'San Luis 3101' 'H032' 'La capa también contiene H031 en Olavarría 409; H032 es una fusión errónea ya documentada con Roma del Abasto.' 'Retirar o corregir H032 en la fuente canónica; no contarla como segundo Café Roma.' $fc $fl
$cruce += Nuevo-Caso 'C21' 'domicilio_distinto_entre_conjuntos' 'LA ACADEMIA' 'catalogo_90' 'LA ACADEMIA' 'Montevideo 341' '' 'capa_reconocimientos_215' 'La Academia' 'Av. Callao 368' 'H060' 'El catálogo vigente aporta Montevideo 341; la capa conserva el domicilio histórico anterior.' 'Actualizar H060 y regenerar derivados desde una fuente canónica única.' $fc $fl

$duplicados = @(
    @('C22','Aramburu','MIC-045 · Dos Estrellas; H153 · ranking regional','Vicente López 1661','múltiples reconocimientos del mismo establecimiento y domicilio','Conservar reconocimientos, pero vincularlos con un identificador de establecimiento para no duplicar conteos.'),
    @('C23','Don Julio','MIC-023 · Una Estrella; H149 · ranking regional; H160 · ranking mundial','Guatemala 4699','tres registros del mismo establecimiento y domicilio','Conservar reconocimientos, pero contar una sola identidad de establecimiento.'),
    @('C24','El Preferido de Palermo','MIC-038 · selección; H151 · ranking regional','Jorge Luis Borges 2108','múltiples reconocimientos del mismo establecimiento y domicilio','Conservar reconocimientos, pero vincularlos con un identificador de establecimiento.'),
    @('C25','Julia','MIC-016 · selección; H156 · ranking regional','Loyola 807','múltiples reconocimientos del mismo establecimiento y domicilio','Conservar reconocimientos, pero vincularlos con un identificador de establecimiento.'),
    @('C26','Mishiguene','MIC-037 · selección; H158 · ranking regional','Lafinur 3368','múltiples reconocimientos del mismo establecimiento y domicilio','Conservar reconocimientos, pero vincularlos con un identificador de establecimiento.'),
    @('C27','Ness','MIC-040 · selección; H157 · ranking regional','Grecia 3691','múltiples reconocimientos del mismo establecimiento y domicilio','Conservar reconocimientos, pero vincularlos con un identificador de establecimiento.'),
    @('C28','Niño Gordo','MIC-034 · selección; H150 · ranking regional','Thames 1810','múltiples reconocimientos; además hay una variante sin tilde','Conservar reconocimientos, normalizar el nombre y vincularlos con un identificador de establecimiento.'),
    @('C29','Trescha','MIC-002 · Una Estrella; H154 · ranking regional','Murillo 725','múltiples reconocimientos del mismo establecimiento y domicilio','Conservar reconocimientos, pero vincularlos con un identificador de establecimiento.'),
    @('C30','Café Roma','H032 · San Luis 3101; H031 · Olavarria 409','dos domicilios; misma geometría','duplicado erróneo: H032 repite las coordenadas de H031 y proviene de una fusión equivocada','Corregir H032 como Roma del Abasto en Anchorena 806 o retirarla de esta versión antes de medir.'),
    @('C31','Crizia','MIC-009 · Fitz Roy 1819; H155 · Gorriti 5143','dos domicilios y dos geometrías','conflicto temporal de domicilio entre dos reconocimientos; la consulta de identidad previa devolvió Fitz Roy 1819 para el registro de Gorriti','Resolver la cronología de la mudanza y marcar el domicilio aplicable a cada edición; no fusionar espacialmente sin fecha.'),
    @('C32','Miramar','ICO-012 · Av. San Juan 1999; H078 · Sarandi 1190','dos puertas de la misma ochava','par intencional: un establecimiento con dos reconocimientos oficiales y dos direcciones de esquina','Conservar ambas filas y agregar una marca explícita de par para no duplicar el establecimiento.')
)
foreach ($d in $duplicados) {
    $cruce += Nuevo-Caso $d[0] 'repeticion_interna_capa' $d[1] 'capa_reconocimientos_215' $d[1] $d[3] $d[2] 'capa_reconocimientos_215' $d[1] $d[3] $d[2] $d[4] $d[5] $fl $fl
}

$cruce | Export-Csv -LiteralPath (Join-Path $destino 'cruce_de_los_cuatro_conjuntos.csv') -NoTypeInformation -Encoding utf8BOM

$informe = @'
# Verificación complementaria de locales y consistencia de registros

## Resultado que cambia

La cobertura documental fechada mejora en cuatro casos: **Makarios** avanza de 2023-06-19 a 2024-02-17 y el bloque histórico pasa de **48/54 a 51/54** por **El Estaño 1880**, **Bar Bidou** y **Boston City**. La evidencia es de nivel v2: acredita existencia o actividad a la fecha de cada fuente, no atención al 10 de agosto de 2026.

Además, la duda de domicilio de Saverio queda resuelta administrativamente: San Juan 2809 y 2816 corresponden a parcelas diferentes. El cruce de registros detecta 19 variantes de nombre entre catálogo y capa, dos domicilios desactualizados o erróneos y 11 grupos repetidos por nombre dentro de la capa de reconocimientos.

Fecha de revisión: **2026-08-10**. No se usaron APIs pagas ni datos personales.

## 1. Locales de Flores, Villa Luro y Donado–Holmberg

Se revisaron 15 casos. El único avance con una pieza pública fechada posterior al antecedente fue Makarios: una nota del **2024-02-17** individualiza nombre, oferta y **Felipe Vallese 3130** ([fuente](https://www.c5n.com/lifestyle/la-parrilla-buenos-aires-comer-asados-economicos-y-muy-ricos-n146679)). El resultado se registra como `abierto_a_fecha_fuente`, no como abierto al corte.

Los otros 14 permanecen en `vigencia_no_verificada`: los nueve del registro kosher sólo conservan la prueba oficial de **2015** ([listado oficial](https://turismo.buenosaires.gob.ar/sites/turismo/files/establecimientos_KOSHER_2015_0.pdf)); Estación de Milanesas, García Restaurante, Mich Bar y Pulpería Norte no obtuvieron una pieza editorial posterior a 2023; Cimino R no obtuvo una pieza posterior a 2022 que acredite la sede de Donado 1919. El permiso municipal de Cimino y los estados de agregadores se registraron como indicios, pero no se convirtieron en veredictos.

El CSV de verificación deja por fila las consultas exactas, lo encontrado, las superficies insuficientes y el límite de cada conclusión. En ningún caso “no localizado” se interpreta como inexistente o cerrado.

## 2. Seis históricos que seguían pendientes

Tres casos alcanzan v2:

- **El Estaño 1880**: una guía oficial nacional publicada el **2025-03-25** lo describe en presente, informa oferta y actividades y consigna Aristóbulo del Valle 1100 ([fuente](https://www.argentina.travel/novedades/cafes-notables-de-buenos-aires-donde-el-sabor-se-encuentra-con-la-historia)).
- **Bar Bidou**: una pieza periodística del **2025-11-16** lo individualiza en Av. Roque Sáenz Peña 858 ([fuente](https://www.infobae.com/sociedad/2025/11/16/cafetines-de-buenos-aires-el-bar-notable-que-desafio-la-cuadricula-portena-y-la-historia-secreta-de-la-avenida-diagonal-norte/)).
- **Boston City**: una programación oficial del **2026-02-02** lo incluye en un recorrido cultural; la identidad y Florida 165 local 3 se controlaron contra el catálogo oficial firmado el **2026-02-26** ([programación](https://buenosaires.gob.ar/gcaba_historico/noticias/verano-notable-musica-literatura-y-recorridos-culturales-en-los-bares), [catálogo](https://documentosboletinoficial.buenosaires.gob.ar/publico/PE-RES-MCGC-MCGC-1225-26-ANX.pdf)).

Siguen pendientes Bar del Alvear Palace Hotel, Petit Colón y El Coleccionista. En los tres, el catálogo oficial de **2026-02-26** confirma pertenencia y domicilio, pero no operación. Para el primero predominan una página general del hotel sin fecha y piezas sobre otros espacios del edificio; para Petit Colón, una ficha sin fecha, agregadores y una agenda de 2026 que reproduce un expediente de 2023; para El Coleccionista, agregadores con fechas de actualización, fichas sin fecha y registros patrimoniales. El archivo `seis_pendientes.csv` detalla qué se buscó y qué evidencia faltaría.

## 3. Saverio: 2809 frente a 2816

La consulta al normalizador municipal asignó a Av. San Juan el código de calle **20040**. Con ese código, el servicio catastral por puerta devolvió:

| Puerta | SMP | Partida matriz | Coordenadas planas |
|---|---|---:|---|
| Av. San Juan 2809 | 30-083-040A | 186130 | 105414.133363, 100588.295872 |
| Av. San Juan 2816 | 30-082-004A | 182937 | 105450.145098, 100575.130453 |

Las puertas están separadas aproximadamente **38 metros** y tienen SMP y partida matriz distintos. Por lo tanto, no son dos accesos catastrales del mismo inmueble: son parcelas diferentes, en lados opuestos de la avenida. La conclusión se apoya en consultas municipales realizadas el **2026-08-10** ([2809](https://ws.usig.buenosaires.gob.ar/geocoder/2.2/smp?cod_calle=20040&altura=2809), [2816](https://ws.usig.buenosaires.gob.ar/geocoder/2.2/smp?cod_calle=20040&altura=2816)). `saverio_fuente_municipal.csv` conserva la respuesta mínima necesaria.

Esta resolución es catastral. No fija por sí sola la fecha de una eventual mudanza ni acredita operación comercial en ninguna puerta.

## 4. Cruce de los cuatro conjuntos

Universos controlados el **2026-08-10**: catálogo vigente de 90 establecimientos; capa de 215 objetos, todos con geometría; nueve locales nombrados en páginas periodísticas; y diez establecimientos del registro kosher, incluido Matok. Los dos últimos grupos no presentan coincidencias ocultas por nombre normalizado o domicilio con el catálogo de 90 ni con la capa de 215.

El archivo `cruce_de_los_cuatro_conjuntos.csv` contiene 32 hallazgos auditables:

- **19 nombres distintos en el mismo domicilio** entre catálogo y capa. Diecisiete son variantes o alias; Museo Fotográfico Simik/Cafe Palacio es un renombre confirmado y El Boliche de Roberto/12 de octubre es un alias del mismo establecimiento.
- **Dos conflictos de domicilio entre conjuntos**: Café Roma figura correctamente en Olavarría 409 en el catálogo y en H031, mientras H032 conserva la fusión errónea “Café Roma / San Luis 3101”; La Academia figura en Montevideo 341 en el catálogo, pero H060 conserva Av. Callao 368.
- **11 grupos repetidos por nombre dentro de la capa**. Ocho son establecimientos con más de un reconocimiento y el mismo domicilio; Don Julio tiene tres registros. Los otros tres requieren trato explícito: Café Roma es un duplicado erróneo, Crizia presenta un conflicto temporal de domicilio y Miramar es un par intencional del mismo local en ochava con dos reconocimientos y dos direcciones.

La acción recomendada no es borrar reconocimientos: es separar `establecimiento_id` de `reconocimiento_id`, marcar pares y alias, y corregir las dos filas obsoletas antes de volver a contar establecimientos o medir cobertura espacial.

## Pendientes finales

Quedan **14/15** locales sin nueva prueba fechada y **3/6** históricos sin pieza individual fechada. Se mantienen como pendientes porque las búsquedas devolvieron directorios, agregadores, páginas sin fecha editorial o actos normativos que no acreditan actividad. Para cerrarlos haría falta una actividad oficial fechada, una pieza periodística individual con domicilio o una constatación directa documentada.

No se modificaron fuentes originales, datos crudos, pipelines ni archivos de otras entregas. Los archivos producidos no contienen correos, teléfonos, identificadores técnicos de plataformas privadas, enlaces privados ni claves.
'@

Set-Content -LiteralPath (Join-Path $destino 'INFORME.md') -Value $informe -Encoding utf8

Write-Output "Generados: $($locales.Count) locales; $($seis.Count) históricos; $($saverio.Count) puertas; $($cruce.Count) hallazgos de cruce."
