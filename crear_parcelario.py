#!/usr/bin/env python

# Fichero con la lista de referencias catastrales
REFS_IN = 'refs.lst'

# Fichero GML del municipio donde deberían estar esas referencias
#
# Estos ficheros los ofrece catastro y se descargan en varios pasos.
# Para descargar el fichero de Guijo de Granadilla
# 1. http://www.catastro.minhap.es/INSPIRE/CadastralParcels/ES.SDGC.CP.atom.xml
# 2. http://www.catastro.minhap.es/INSPIRE/CadastralParcels/10/ES.SDGC.CP.atom_10.xml
# 3. http://www.catastro.minhap.es/INSPIRE/CadastralParcels/10/10093-GUIJO DE GRANADILLA/A.ES.SDGC.CP.10093.zip
# 4. Descomprimir el zip
# 5. Usar el fichero llamado "*cadastralparcel.gml"
GML_IN = "catastro_guijo.gml"

# Fichero GML de salida
GML_OUT = "fincas_guijo.gml"


def print_ln(lines, total_lines, members, r_found, r_left):
    """Imprime a stdout el progreso del proceso"""
    total_refs = len(r_found) + len(r_left)
    print(">> Lineas leídas: {}/{}".format(lines, total_lines))
    print(">> Miembros procesados: {}".format(members))
    print(">> REFERENCIAS Catastrales")

    refs_head_found = 'Encontradas ({}/{})'.format(
            len(r_found),
            total_refs)
    refs_head_left = 'Por encontrar ({})'.format(len(r_left))
 
    fmt = '{:<30}{}'
    print(fmt.format(refs_head_found, refs_head_left))


    print("*" * 40)
    print("")
    print("")


def write_out(msg):
    """Escribe al final del fichero de GML_OUT de forma segura"""
    global GML_OUT
    with open(GML_OUT, "a+") as f_out:
        f_out.write(msg)
        f_out.flush()

def write_beginning(msg):
    """Escribe al principio del fichero de GML_OUT de forma segura"""
    global GML_OUT
    with open(GML_OUT, "r+") as f:
        s = f.read();
        f.seek(0)
        f.write(msg + s)


# Iniciación de variables
# -----------------------

# Ya se han leido las cabeceras?
after_headers = False

# La posicion en el fichero de entrada está dentro de un "member"
in_member = False

# Cadena por la que empieza un "member"
member_start = "<member>"

# Cadena por la que termina un "member"
member_end = "</member>"

# Variable donde se acumulan las lineas de un member segun se avanza en GML_IN
member = ""

# Lineas leidas
ln = 0

# Conteo de members procesados
members_count = 0

# Referencias encontradas
refs_found = []


# Se leen las referencias catastrales de REFS_IN
with open(REFS_IN) as f:
    refs = f.read().splitlines()

# Las referencias catastrales en GML_IN vienen sin los últimos 6 caracteres,
# con lo cual se eliminan de cada referencia en la lista
for i, ref in enumerate(refs):
    refs[i] = ref[:-6]

# Se cuenta el número de líneas en GML_IN para poder indicar el progreso
total_lines = sum(1 for line in open(GML_IN))


# Se procesa el fichero GML_IN en busca de members.
# Si la referencia del member encontrado está en la lista de referencias,
# se inserta en GML_OUT.
with open(GML_IN) as f_in:
    line = f_in.readline()
    # Mientras haya lineas sin leer y referencias que procesar...
    while line and refs:
        # Se comprueba si empieza un member
        if member_start in line:
            in_member = True
            members_count += 1

        # Se comprueba si termina un member
        if member_end in line:
            in_member = False
            member += line

            # Se busca si alguna referencia aparece en
            # el contenido del member en cuestión
            for ref in refs:
                if ref in member:
                    # Referencia encontrada
                    # print("Encontrada referencia: {}".format(ref))
                    # Se escribe el member en GML_OUT
                    write_out(member)
                    # Se elimina la referencia de la lista de referencias
                    # pendiente y se inserta en la lista de referencias encontradas
                    refs.remove(ref)
                    refs_found.append(ref)
            print_ln(ln, total_lines, members_count, refs_found, refs)
 
        if in_member:
            member += line
        else:
            member = ""

        line = f_in.readline()
        ln += 1
    # Se escriben la cabecera
    # En la plantilla de la cabecera hay que sustituir la cadena {count} por
    # el número total de members (referencias encontradas) que hay en GML_OUT,
    # es un mecanismo de control del formato GML
    header = open("head.tpl").read().replace("{count}",str(len(refs_found)))
    write_beginning(header)

    # Se escribe el footer
    footer = open("foot.tpl").read()
    write_out(footer)

# Si no se han encontrado todas las referencias, se avisa al usuario
if refs:
    print("*" * 60)
    print("Referencias no encontradas:")
    print(refs)
