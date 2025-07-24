import re
from datetime import datetime


# --- Auxiliary Funcs ---
def parse_amount(value: str) -> float:
    """Convert amount string to float, keeping negatives as negatives."""
    if not value:
        return 0.0
    clean = re.sub(r"[^\d,.-]", "", str(value))
    clean = clean.replace(",", "")  # handle thousand separators
    try:
        return float(clean)
    except ValueError:
        return 0.0

def parse_date(value: str) -> str:
    for fmt in ("%d/%m/%Y", "%d-%m-%Y", "%Y-%m-%d", "%d/%m/%y"):
        try:
            return datetime.strptime(value.strip(), fmt).strftime("%Y-%m-%d")
        except Exception:
            continue
    return value.strip()



# Headers for extraction
fields_to_extract = ["Número de Autorización", "Fecha de Transacción", "Descripción", "Valor Original", "Cargos y Abonos", "Saldo a Diferir", "Cuotas"]




# --- Raw Strings Transformation ---

# FOREIGN

# ['Número de Autorización', 'Fecha de Transacción', 'Descripción', 'Valor Original', 'Tasa Pactada', 'Tasa EA Facturada', 'Cargos y Abonos', 'Saldo a Diferir', 'Cuotas']
foreign_exp = [       
    ['T05372', '25/02/2025', 'APPLE.COM/BILL VR MONEDA ORIG 27800.0 USA', '6.82', '1,9598', '26,2256', '0.19', '6.63', '1/36'],
    ['T06950', '23/02/2025', 'APPLE.COM/BILL VR MONEDA ORIG 61400.0 USA', '15.06', '1,9598', '26,2256', '0.42', '14.64', '1/36'],
    ['T09849', '22/02/2025', 'APPLE.COM/BILL VR MONEDA ORIG 28900.0 USA', '7.05', '1,9598', '26,2256', '0.20', '6.85', '1/36'],
    ['T09072', '22/02/2025', 'APPLE.COM/BILL VR MONEDA ORIG 54500.0 USA', '13.36', '1,9598', '26,2256', '0.37', '12.99', '1/36'],
    ['T03350', '22/02/2025', 'Nintendo CA1361206913', '3.74', '1,9598', '26,2256', '0.10', '3.64', '1/36'],
    ['T03633', '19/02/2025', 'APPLE.COM/BILL VR MONEDA ORIG 44900.0 USA', '10.95', '1,9598', '26,2256', '0.30', '10.65', '1/36'],
    ['T00212', '19/02/2025', 'APPLE.COM/BILL VR MONEDA ORIG 29900.0 USA', '7.29', '1,9598', '26,2256', '0.20', '7.09', '1/36'],
    ['R04404', '14/02/2025', 'Dlocal *UBER RIDES VR MONEDA ORIG 31809.0 MLT', '7.64', '1,9598', '26,2256', '0.21', '7.43', '1/36'],
    ['R02609', '14/02/2025', 'AMAZON MKTPL*7116O2OJ3', '79.99', '1,9598', '26,2256', '2.22', '77.77', '1/36'],
    ['R08748', '14/02/2025', 'OPENAI *CHATGPT SUBSCR', '20.00', '1,9598', '26,2256', '0.56', '19.44', '1/36'],
    ['R09375', '10/02/2025', 'SPLICE.COM* SOUNDS 100', '12.99', '1,9598', '26,2256', '0.36', '12.63', '1/36'],
    ['R06526', '09/02/2025', 'Disney PLUS VR MONEDA ORIG 23450.0 USA', '5.65', '1,9598', '26,2256', '0.16', '5.49', '1/36'],
    ['R05406', '09/02/2025', 'DISNEY DTC LATAM INC. VR MONEDA ORIG 46900.0 USA', '11.30', '1,9598', '26,2256', '0.31', '10.99', '1/36'],
    ['R03502', '07/02/2025', 'NADEL', '1.00', '1,9598', '26,2256', '0.03', '0.97', '1/36'],
    ['T05964', '06/02/2025', 'Scribd Inc *496589665', '10.70', '1,9598', '26,2256', '0.30', '10.40', '1/36'],
    ['T01736', '05/02/2025', 'APPLE.COM/BILL VR MONEDA ORIG 15900.0 USA', '3.79', '1,9598', '26,2256', '0.11', '3.68', '1/36'],
    ['T07880', '05/02/2025', 'APPLE.COM BILL VR MONEDA ORIG 124900.0 USA', '29.75', '1,9598', '26,2256', '0.83', '28.92', '1/36'],
    ['T00259', '04/02/2025', 'Nintendo CA1351525990', '19.99', '1,9598', '26,2256', '0.56', '19.43', '1/36'],
    ['R00562', '04/02/2025', 'NEBULA SUBSCRIPTION', '6.00', '1,9598', '26,2256', '0.17', '5.83', '1/36'],
    ['R07628', '03/02/2025', 'AMAZON MKTPL*N55XV0773', '86.90', '1,9598', '26,2256', '2.41', '84.22', '1/36']
]

foreign_transformed = [
    [x[0]]+
    [parse_date(x[1])]+
    [x[2]]+
    [parse_amount(x[3])]+
    [parse_amount(x[6])]+
    [parse_amount(x[7])]+
    [x[8]] for x in foreign_exp
    ]

total_fo_vo = sum([x[3] for x in foreign_transformed])
total_fo_cya = sum([x[4] for x in foreign_transformed])
total_fo_sad = sum([x[5] for x in foreign_transformed])



# DOMESTIC
domestic_exp = [
    ['', '28/02/2025', 'INTERESES CORRIENTES', '6,598.04', '', '', '6,598.04', '0.00', ''],
    ['000000', '28/02/2025', 'CUOTA DE MANEJO', '48,490.00', '', '', '48,490.00', '0.00', ''],
    ['T04877', '27/02/2025', 'DLO*Spotify', '26,400.00', '0,0000', '00,0000', '26,400.00', '0.00', '1/1'],
    ['R01915', '25/02/2025', 'UBER RIDES', '29,492.00', '0,0000', '00,0000', '29,492.00', '0.00', '1/1'],
    ['R08071', '25/02/2025', 'UBER RIDES', '29,555.00', '0,0000', '00,0000', '29,555.00', '0.00', '1/1'],
    ['R04507', '25/02/2025', 'UBER RIDES', '30,203.00', '0,0000', '00,0000', '30,203.00', '0.00', '1/1'],
    ['H07367', '25/02/2025', 'SANTA MARTA MARRIOT RE', '947,722.00', '0,0000', '00,0000', '947,722.00', '0.00', '1/1'],
    ['H06043', '25/02/2025', 'SANTA MARTA MARRIOT RE', '272,055.00', '0,0000', '00,0000', '272,055.00', '0.00', '1/1'],
    ['000000', '24/02/2025', 'COMISION AVANCE CAJERO', '7,460.00', '', '', '7,460.00', '0.00', ''],
    ['R06381', '24/02/2025', 'UBER RIDES', '10,774.00', '0,0000', '00,0000', '10,774.00', '0.00', '1/1'],
    ['R07715', '24/02/2025', 'UBER RIDES', '9,610.00', '0,0000', '00,0000', '9,610.00', '0.00', '1/1'],
    ['R00697', '24/02/2025', 'UBER RIDES', '29,563.00', '0,0000', '00,0000', '29,563.00', '0.00', '1/1'],
    ['F07063', '24/02/2025', 'SAMARIAN CO SAS', '209,778.00', '0,0000', '00,0000', '209,778.00', '0.00', '1/1'],
    ['R06018', '24/02/2025', 'INGLESA 300', '68,900.00', '0,0000', '00,0000', '68,900.00', '0.00', '1/1'],
    ['R00770', '24/02/2025', 'COMCEL PAGO DE FACTURA', '208,578.00', '0,0000', '00,0000', '208,578.00', '0.00', '1/1'],
    ['X07118', '24/02/2025', 'LATAM AIRLINES COLOMBI', '91,900.00', '0,0000', '00,0000', '91,900.00', '0.00', '1/1'],
    ['F04982', '24/02/2025', 'LULO CAFE BAR', '120,230.00', '0,0000', '00,0000', '120,230.00', '0.00', '1/1'],
    ['F05289', '22/02/2025', 'GUASIMO RESTAURANTE SA', '346,352.00', '0,0000', '00,0000', '346,352.00', '0.00', '1/1'],
    ['R02869', '22/02/2025', 'UBER RIDES', '29,573.00', '0,0000', '00,0000', '29,573.00', '0.00', '1/1'],
    ['H06921', '22/02/2025', 'SANTA MARTA MARRIOT RE', '1,144,404.00', '0,0000', '00,0000', '1,144,404.00', '0.00', '1/1'],
    ['R04902', '22/02/2025', 'ANANDA TALLER DULCE 11', '49,500.00', '0,0000', '00,0000', '49,500.00', '0.00', '1/1'],
    ['H08960', '22/02/2025', 'SANTA MARTA MARRIOT RE', '90,685.00', '0,0000', '00,0000', '90,685.00', '0.00', '1/1'],
    ['Z06486', '22/02/2025', 'AVANCE CAJERO BANCOLOMBIA', '500,000.00', '1,9598', '26,2256', '20,833.33', '479,166.67', '1/24'],
    ['R04852', '19/02/2025', 'CDA CAPRI', '302,673.00', '0,0000', '00,0000', '302,673.00', '0.00', '1/1'],     
    ['R00807', '18/02/2025', 'DLO*RAPPI COLOMBIA', '261,316.00', '0,0000', '00,0000', '261,316.00', '0.00', '1/1'],
    ['U03368', '18/02/2025', 'CTRO DIAGNOST AUTOM VA', '644,130.00', '0,0000', '00,0000', '644,130.00', '0.00', '1/1'],
    ['R00078', '16/02/2025', 'DLO*RAPPI COLOMBIA', '121,150.00', '0,0000', '00,0000', '121,150.00', '0.00', '1/1'],
    ['R02687', '16/02/2025', 'DLO*RAPPI COLOMBIA', '17,250.00', '0,0000', '00,0000', '17,250.00', '0.00', '1/1'],
    ['R00958', '15/02/2025', 'CARULLA TRADE CENTER', '69,754.00', '0,0000', '00,0000', '69,754.00', '0.00', '1/1'],
    ['R00214', '15/02/2025', 'RAPPI*RAPPI COLOMBIA', '135,200.00', '0,0000', '00,0000', '135,200.00', '0.00', '1/1'],
    ['R03326', '14/02/2025', 'UBER RIDES', '25,216.00', '0,0000', '00,0000', '25,216.00', '0.00', '1/1'],
    ['R01654', '14/02/2025', 'RAPPI*PRO COLOMBIA', '23,490.00', '0,0000', '00,0000', '23,490.00', '0.00', '1/1'],
    ['R08218', '14/02/2025', 'AMAZON.COM', '317,687.00', '0,0000', '00,0000', '317,687.00', '0.00', '1/1'],
    ['R09099', '14/02/2025', 'DLO*RAPPI COLOMBIA', '18,950.00', '0,0000', '00,0000', '18,950.00', '0.00', '1/1'],
    ['R09123', '13/02/2025', 'DLO*RAPPI COLOMBIA', '14,400.00', '0,0000', '00,0000', '14,400.00', '0.00', '1/1'],
    ['R09237', '12/02/2025', 'UBER RIDES', '26,651.00', '0,0000', '00,0000', '26,651.00', '0.00', '1/1'],
    ['R08723', '12/02/2025', 'UBER RIDES', '26,762.00', '0,0000', '00,0000', '26,762.00', '0.00', '1/1'],
    ['R02726', '12/02/2025', 'ADOBE', '333,200.00', '0,0000', '00,0000', '333,200.00', '0.00', '1/1'],
    ['R05583', '11/02/2025', 'MOVISTAR PAGOSEPAYCO', '167,087.00', '0,0000', '00,0000', '167,087.00', '0.00', '1/1'],
    ['F09183', '10/02/2025', 'DiDi co Food', '28,809.00', '0,0000', '00,0000', '28,809.00', '0.00', '1/1'],
    ['T07215', '09/02/2025', 'PPRO*MICROSOFT', '42,990.00', '0,0000', '00,0000', '42,990.00', '0.00', '1/1'],
    ['R00970', '09/02/2025', 'EDS ROOSEVELT', '183,535.00', '0,0000', '00,0000', '183,535.00', '0.00', '1/1'],
    ['R05440', '09/02/2025', 'DLO*RAPPI COLOMBIA', '46,350.00', '0,0000', '00,0000', '46,350.00', '0.00', '1/1'],
    ['R07896', '08/02/2025', 'EL MOLINO LA 14 CENTEN', '14,900.00', '0,0000', '00,0000', '14,900.00', '0.00', '1/1'],
    ['R01686', '08/02/2025', 'SC CENTENARIO', '730,793.00', '0,0000', '00,0000', '730,793.00', '0.00', '1/1'],
    ['000000', '07/02/2025', 'COMISION AVANCE CAJERO', '7,460.00', '', '', '7,460.00', '0.00', ''],
    ['R03058', '07/02/2025', 'INVERSIONES TNS CHIPIC', '59,400.00', '0,0000', '00,0000', '59,400.00', '0.00', '1/1'],
    ['R02943', '07/02/2025', 'BOSI CHIPICHAPE N 2', '524,900.00', '0,0000', '00,0000', '524,900.00', '0.00', '1/1'],
    ['F07100', '07/02/2025', 'HAMBURGUESAS EL CORRAL', '88,800.00', '0,0000', '00,0000', '88,800.00', '0.00', '1/1'],
    ['R02775', '07/02/2025', 'UBER RIDES', '12,952.00', '0,0000', '00,0000', '12,952.00', '0.00', '1/1'],
    ['R08838', '07/02/2025', 'VELEZ 5030 CHIPICHAPE', '329,900.00', '0,0000', '00,0000', '329,900.00', '0.00', '1/1'],
    ['F09124', '07/02/2025', 'SUSHI GREEN 4', '41,300.00', '0,0000', '00,0000', '41,300.00', '0.00', '1/1'],
    ['Z03019', '07/02/2025', 'AVANCE CAJERO BANCOLOMBIA', '300,000.00', '1,9598', '26,2256', '12,500.00', '287,500.00', '1/24'],
    ['F07816', '06/02/2025', 'DiDi co Food', '25,105.00', '0,0000', '00,0000', '25,105.00', '0.00', '1/1'],
    ['F00265', '05/02/2025', 'DiDi CO Food', '17,670.00', '0,0000', '00,0000', '17,670.00', '0.00', '1/1'],
    ['R01075', '04/02/2025', 'RAPPI*RAPPI COLOMBIA', '259,300.00', '0,0000', '00,0000', '259,300.00', '0.00', '1/1'],
    ['R06088', '04/02/2025', 'DLO*RAPPI COLOMBIA', '36,300.00', '0,0000', '00,0000', '36,300.00', '0.00', '1/1'],
    ['R04890', '02/02/2025', 'COCINA COREANA URIMURI', '152,416.00', '0,0000', '00,0000', '152,416.00', '0.00', '1/1'],
    ['R08076', '02/02/2025', 'CALATHEA', '34,500.00', '0,0000', '00,0000', '34,500.00', '0.00', '1/1'],
    ['F03778', '01/02/2025', 'BENGALA Y BANDOLERO', '40,000.00', '0,0000', '00,0000', '40,000.00', '0.00', '1/1'],
    ['R03434', '01/02/2025', 'UBER RIDES', '11,905.00', '0,0000', '00,0000', '11,905.00', '0.00', '1/1'],
    ['R05755', '01/02/2025', 'UBER RIDES', '13,196.00', '0,0000', '00,0000', '13,196.00', '0.00', '1/1'],
    ['R03528', '01/02/2025', 'DLO*RAPPI COLOMBIA', '140,750.00', '0,0000', '00,0000', '140,750.00', '0.00', '1/1'],
    ['R03244', '01/02/2025', 'DLO*RAPPI COLOMBIA', '44,250.00', '0,0000', '00,0000', '44,250.00', '0.00', '1/1'],
    ['R06337', '01/02/2025', 'DROGUERIA NATURFARMA D', '6,800.00', '0,0000', '00,0000', '6,800.00', '0.00', '1/1'],
    ['F05421', '01/02/2025', 'DISCO BANDOLEROS S A S', '94,600.00', '0,0000', '00,0000', '94,600.00', '0.00', '1/1'],
    ['F09754', '31/01/2025', 'TAQUERIA EL BUEN PASTO', '103,250.00', '0,0000', '00,0000', '103,250.00', '0.00', '1/1'],
    ['R09903', '31/01/2025', 'DLO*RAPPI COLOMBIA', '167,820.00', '0,0000', '00,0000', '167,820.00', '0.00', '1/1'],
    ['F08942', '30/01/2025', 'DiDi co Food', '49,127.00', '0,0000', '00,0000', '49,126.71', '0.00', '1/1']
]

domestic_transformed = [
    [x[0]]+
    [parse_date(x[1])]+
    [x[2]]+
    [parse_amount(x[3])]+
    [parse_amount(x[6])]+
    [parse_amount(x[7])]+
    [x[8]] for x in domestic_exp
    ]

total_do_vo = sum([x[3] for x in domestic_transformed])
total_do_cya = sum([x[4] for x in domestic_transformed])
total_do_sad = sum([x[5] for x in domestic_transformed])




# --- Format Aligning ---
#   From Nested list to a List of dicts (Which is the same output of the app's function)

# FOREIGN
fo_trans = [
    ['T05372', '2025-02-25', 'APPLE.COM/BILL VR MONEDA ORIG 27800.0 USA', 6.82, 0.19, 6.63, '1/36'],
    ['T06950', '2025-02-23', 'APPLE.COM/BILL VR MONEDA ORIG 61400.0 USA', 15.06, 0.42, 14.64, '1/36'],
    ['T09849', '2025-02-22', 'APPLE.COM/BILL VR MONEDA ORIG 28900.0 USA', 7.05, 0.2, 6.85, '1/36'],
    ['T09072', '2025-02-22', 'APPLE.COM/BILL VR MONEDA ORIG 54500.0 USA', 13.36, 0.37, 12.99, '1/36'],
    ['T03350', '2025-02-22', 'Nintendo CA1361206913', 3.74, 0.1, 3.64, '1/36'],
    ['T03633', '2025-02-19', 'APPLE.COM/BILL VR MONEDA ORIG 44900.0 USA', 10.95, 0.3, 10.65, '1/36'],
    ['T00212', '2025-02-19', 'APPLE.COM/BILL VR MONEDA ORIG 29900.0 USA', 7.29, 0.2, 7.09, '1/36'],
    ['R04404', '2025-02-14', 'Dlocal *UBER RIDES VR MONEDA ORIG 31809.0 MLT', 7.64, 0.21, 7.43, '1/36'],
    ['R02609', '2025-02-14', 'AMAZON MKTPL*7116O2OJ3', 79.99, 2.22, 77.77, '1/36'],
    ['R08748', '2025-02-14', 'OPENAI *CHATGPT SUBSCR', 20.0, 0.56, 19.44, '1/36'],
    ['R09375', '2025-02-10', 'SPLICE.COM* SOUNDS 100', 12.99, 0.36, 12.63, '1/36'],
    ['R06526', '2025-02-09', 'Disney PLUS VR MONEDA ORIG 23450.0 USA', 5.65, 0.16, 5.49, '1/36'],
    ['R05406', '2025-02-09', 'DISNEY DTC LATAM INC. VR MONEDA ORIG 46900.0 USA', 11.3, 0.31, 10.99, '1/36'],
    ['R03502', '2025-02-07', 'NADEL', 1.0, 0.03, 0.97, '1/36'],
    ['T05964', '2025-02-06', 'Scribd Inc *496589665', 10.7, 0.3, 10.4, '1/36'],
    ['T01736', '2025-02-05', 'APPLE.COM/BILL VR MONEDA ORIG 15900.0 USA', 3.79, 0.11, 3.68, '1/36'],
    ['T07880', '2025-02-05', 'APPLE.COM BILL VR MONEDA ORIG 124900.0 USA', 29.75, 0.83, 28.92, '1/36'],
    ['T00259', '2025-02-04', 'Nintendo CA1351525990', 19.99, 0.56, 19.43, '1/36'],
    ['R00562', '2025-02-04', 'NEBULA SUBSCRIPTION', 6.0, 0.17, 5.83, '1/36'],
    ['R07628', '2025-02-03', 'AMAZON MKTPL*N55XV0773', 86.9, 2.41, 84.22, '1/36']
]

# List holder
fo_exp_ls = []

# Expenses reformatting
for exp in fo_trans:
    temp = {}
    for i, field in enumerate(fields_to_extract):
        temp[field] = exp[i]
    fo_exp_ls.append(temp)



# DOMESTIC
do_trans = [
    ['', '2025-02-28', 'INTERESES CORRIENTES', 6598.04, 6598.04, 0.0, ''],
    ['000000', '2025-02-28', 'CUOTA DE MANEJO', 48490.0, 48490.0, 0.0, ''],
    ['T04877', '2025-02-27', 'DLO*Spotify', 26400.0, 26400.0, 0.0, '1/1'],
    ['R01915', '2025-02-25', 'UBER RIDES', 29492.0, 29492.0, 0.0, '1/1'],
    ['R08071', '2025-02-25', 'UBER RIDES', 29555.0, 29555.0, 0.0, '1/1'],
    ['R04507', '2025-02-25', 'UBER RIDES', 30203.0, 30203.0, 0.0, '1/1'],
    ['H07367', '2025-02-25', 'SANTA MARTA MARRIOT RE', 947722.0, 947722.0, 0.0, '1/1'],
    ['H06043', '2025-02-25', 'SANTA MARTA MARRIOT RE', 272055.0, 272055.0, 0.0, '1/1'],
    ['000000', '2025-02-24', 'COMISION AVANCE CAJERO', 7460.0, 7460.0, 0.0, ''],
    ['R06381', '2025-02-24', 'UBER RIDES', 10774.0, 10774.0, 0.0, '1/1'],
    ['R07715', '2025-02-24', 'UBER RIDES', 9610.0, 9610.0, 0.0, '1/1'],
    ['R00697', '2025-02-24', 'UBER RIDES', 29563.0, 29563.0, 0.0, '1/1'],
    ['F07063', '2025-02-24', 'SAMARIAN CO SAS', 209778.0, 209778.0, 0.0, '1/1'],
    ['R06018', '2025-02-24', 'INGLESA 300', 68900.0, 68900.0, 0.0, '1/1'],
    ['R00770', '2025-02-24', 'COMCEL PAGO DE FACTURA', 208578.0, 208578.0, 0.0, '1/1'],
    ['X07118', '2025-02-24', 'LATAM AIRLINES COLOMBI', 91900.0, 91900.0, 0.0, '1/1'],
    ['F04982', '2025-02-24', 'LULO CAFE BAR', 120230.0, 120230.0, 0.0, '1/1'],
    ['F05289', '2025-02-22', 'GUASIMO RESTAURANTE SA', 346352.0, 346352.0, 0.0, '1/1'],
    ['R02869', '2025-02-22', 'UBER RIDES', 29573.0, 29573.0, 0.0, '1/1'],
    ['H06921', '2025-02-22', 'SANTA MARTA MARRIOT RE', 1144404.0, 1144404.0, 0.0, '1/1'],        
    ['R04902', '2025-02-22', 'ANANDA TALLER DULCE 11', 49500.0, 49500.0, 0.0, '1/1'],
    ['H08960', '2025-02-22', 'SANTA MARTA MARRIOT RE', 90685.0, 90685.0, 0.0, '1/1'],
    ['Z06486', '2025-02-22', 'AVANCE CAJERO BANCOLOMBIA', 500000.0, 20833.33, 479166.67, '1/24'],
    ['R04852', '2025-02-19', 'CDA CAPRI', 302673.0, 302673.0, 0.0, '1/1'],
    ['R00807', '2025-02-18', 'DLO*RAPPI COLOMBIA', 261316.0, 261316.0, 0.0, '1/1'],
    ['U03368', '2025-02-18', 'CTRO DIAGNOST AUTOM VA', 644130.0, 644130.0, 0.0, '1/1'],
    ['R00078', '2025-02-16', 'DLO*RAPPI COLOMBIA', 121150.0, 121150.0, 0.0, '1/1'],
    ['R02687', '2025-02-16', 'DLO*RAPPI COLOMBIA', 17250.0, 17250.0, 0.0, '1/1'],
    ['R00958', '2025-02-15', 'CARULLA TRADE CENTER', 69754.0, 69754.0, 0.0, '1/1'],
    ['R00214', '2025-02-15', 'RAPPI*RAPPI COLOMBIA', 135200.0, 135200.0, 0.0, '1/1'],
    ['R03326', '2025-02-14', 'UBER RIDES', 25216.0, 25216.0, 0.0, '1/1'],
    ['R01654', '2025-02-14', 'RAPPI*PRO COLOMBIA', 23490.0, 23490.0, 0.0, '1/1'],
    ['R08218', '2025-02-14', 'AMAZON.COM', 317687.0, 317687.0, 0.0, '1/1'],
    ['R09099', '2025-02-14', 'DLO*RAPPI COLOMBIA', 18950.0, 18950.0, 0.0, '1/1'],
    ['R09123', '2025-02-13', 'DLO*RAPPI COLOMBIA', 14400.0, 14400.0, 0.0, '1/1'],
    ['R09237', '2025-02-12', 'UBER RIDES', 26651.0, 26651.0, 0.0, '1/1'],
    ['R08723', '2025-02-12', 'UBER RIDES', 26762.0, 26762.0, 0.0, '1/1'],
    ['R02726', '2025-02-12', 'ADOBE', 333200.0, 333200.0, 0.0, '1/1'],
    ['R05583', '2025-02-11', 'MOVISTAR PAGOSEPAYCO', 167087.0, 167087.0, 0.0, '1/1'],
    ['F09183', '2025-02-10', 'DiDi co Food', 28809.0, 28809.0, 0.0, '1/1'],
    ['T07215', '2025-02-09', 'PPRO*MICROSOFT', 42990.0, 42990.0, 0.0, '1/1'],
    ['R00970', '2025-02-09', 'EDS ROOSEVELT', 183535.0, 183535.0, 0.0, '1/1'],
    ['R05440', '2025-02-09', 'DLO*RAPPI COLOMBIA', 46350.0, 46350.0, 0.0, '1/1'],
    ['R07896', '2025-02-08', 'EL MOLINO LA 14 CENTEN', 14900.0, 14900.0, 0.0, '1/1'],
    ['R01686', '2025-02-08', 'SC CENTENARIO', 730793.0, 730793.0, 0.0, '1/1'],
    ['000000', '2025-02-07', 'COMISION AVANCE CAJERO', 7460.0, 7460.0, 0.0, ''],
    ['R03058', '2025-02-07', 'INVERSIONES TNS CHIPIC', 59400.0, 59400.0, 0.0, '1/1'],
    ['R02943', '2025-02-07', 'BOSI CHIPICHAPE N 2', 524900.0, 524900.0, 0.0, '1/1'],
    ['F07100', '2025-02-07', 'HAMBURGUESAS EL CORRAL', 88800.0, 88800.0, 0.0, '1/1'],
    ['R02775', '2025-02-07', 'UBER RIDES', 12952.0, 12952.0, 0.0, '1/1'],
    ['R08838', '2025-02-07', 'VELEZ 5030 CHIPICHAPE', 329900.0, 329900.0, 0.0, '1/1'],
    ['F09124', '2025-02-07', 'SUSHI GREEN 4', 41300.0, 41300.0, 0.0, '1/1'],
    ['Z03019', '2025-02-07', 'AVANCE CAJERO BANCOLOMBIA', 300000.0, 12500.0, 287500.0, '1/24'],
    ['F07816', '2025-02-06', 'DiDi co Food', 25105.0, 25105.0, 0.0, '1/1'],
    ['F00265', '2025-02-05', 'DiDi CO Food', 17670.0, 17670.0, 0.0, '1/1'],
    ['R01075', '2025-02-04', 'RAPPI*RAPPI COLOMBIA', 259300.0, 259300.0, 0.0, '1/1'],
    ['R06088', '2025-02-04', 'DLO*RAPPI COLOMBIA', 36300.0, 36300.0, 0.0, '1/1'],
    ['R04890', '2025-02-02', 'COCINA COREANA URIMURI', 152416.0, 152416.0, 0.0, '1/1'],
    ['R08076', '2025-02-02', 'CALATHEA', 34500.0, 34500.0, 0.0, '1/1'],
    ['F03778', '2025-02-01', 'BENGALA Y BANDOLERO', 40000.0, 40000.0, 0.0, '1/1'],
    ['R03434', '2025-02-01', 'UBER RIDES', 11905.0, 11905.0, 0.0, '1/1'],
    ['R05755', '2025-02-01', 'UBER RIDES', 13196.0, 13196.0, 0.0, '1/1'],
    ['R03528', '2025-02-01', 'DLO*RAPPI COLOMBIA', 140750.0, 140750.0, 0.0, '1/1'],
    ['R03244', '2025-02-01', 'DLO*RAPPI COLOMBIA', 44250.0, 44250.0, 0.0, '1/1'],
    ['R06337', '2025-02-01', 'DROGUERIA NATURFARMA D', 6800.0, 6800.0, 0.0, '1/1'],
    ['F05421', '2025-02-01', 'DISCO BANDOLEROS S A S', 94600.0, 94600.0, 0.0, '1/1'],
    ['F09754', '2025-01-31', 'TAQUERIA EL BUEN PASTO', 103250.0, 103250.0, 0.0, '1/1'],
    ['R09903', '2025-01-31', 'DLO*RAPPI COLOMBIA', 167820.0, 167820.0, 0.0, '1/1'],
    ['F08942', '2025-01-30', 'DiDi co Food', 49127.0, 49126.71, 0.0, '1/1']
]

# List holder
do_exp_ls = []

for exp in do_trans:
    temp = {}
    for i, field in enumerate(fields_to_extract):
        temp[field] = exp[i]
    do_exp_ls.append(temp)


[print(x) for x in do_exp_ls]


# --- Final Testing Data Extracted ---
fo_exp = [
    {'Número de Autorización': 'T05372', 'Fecha de Transacción': '2025-02-25', 'Descripción': 'APPLE.COM/BILL VR MONEDA ORIG 27800.0 USA', 'Valor Original': 6.82, 'Cargos y Abonos': 0.19, 'Saldo a Diferir': 6.63, 'Cuotas': '1/36'},
    {'Número de Autorización': 'T06950', 'Fecha de Transacción': '2025-02-23', 'Descripción': 'APPLE.COM/BILL VR MONEDA ORIG 61400.0 USA', 'Valor Original': 15.06, 'Cargos y Abonos': 0.42, 'Saldo a Diferir': 14.64, 'Cuotas': '1/36'},
    {'Número de Autorización': 'T09849', 'Fecha de Transacción': '2025-02-22', 'Descripción': 'APPLE.COM/BILL VR MONEDA ORIG 28900.0 USA', 'Valor Original': 7.05, 'Cargos y Abonos': 0.2, 'Saldo a Diferir': 6.85, 'Cuotas': '1/36'},
    {'Número de Autorización': 'T09072', 'Fecha de Transacción': '2025-02-22', 'Descripción': 'APPLE.COM/BILL VR MONEDA ORIG 54500.0 USA', 'Valor Original': 13.36, 'Cargos y Abonos': 0.37, 'Saldo a Diferir': 12.99, 'Cuotas': '1/36'},
    {'Número de Autorización': 'T03350', 'Fecha de Transacción': '2025-02-22', 'Descripción': 'Nintendo CA1361206913', 'Valor Original': 3.74, 'Cargos y Abonos': 0.1, 'Saldo a Diferir': 3.64, 'Cuotas': '1/36'},
    {'Número de Autorización': 'T03633', 'Fecha de Transacción': '2025-02-19', 'Descripción': 'APPLE.COM/BILL VR MONEDA ORIG 44900.0 USA', 'Valor Original': 10.95, 'Cargos y Abonos': 0.3, 'Saldo a Diferir': 10.65, 'Cuotas': '1/36'},
    {'Número de Autorización': 'T00212', 'Fecha de Transacción': '2025-02-19', 'Descripción': 'APPLE.COM/BILL VR MONEDA ORIG 29900.0 USA', 'Valor Original': 7.29, 'Cargos y Abonos': 0.2, 'Saldo a Diferir': 7.09, 'Cuotas': '1/36'},
    {'Número de Autorización': 'R04404', 'Fecha de Transacción': '2025-02-14', 'Descripción': 'Dlocal *UBER RIDES VR MONEDA ORIG 31809.0 MLT', 'Valor Original': 7.64, 'Cargos y Abonos': 0.21, 'Saldo a Diferir': 7.43, 'Cuotas': '1/36'},
    {'Número de Autorización': 'R02609', 'Fecha de Transacción': '2025-02-14', 'Descripción': 'AMAZON MKTPL*7116O2OJ3', 'Valor Original': 79.99, 'Cargos y Abonos': 2.22, 'Saldo a Diferir': 77.77, 'Cuotas': '1/36'},
    {'Número de Autorización': 'R08748', 'Fecha de Transacción': '2025-02-14', 'Descripción': 'OPENAI *CHATGPT SUBSCR', 'Valor Original': 20.0, 'Cargos y Abonos': 0.56, 'Saldo a Diferir': 19.44, 'Cuotas': '1/36'},
    {'Número de Autorización': 'R09375', 'Fecha de Transacción': '2025-02-10', 'Descripción': 'SPLICE.COM* SOUNDS 100', 'Valor Original': 12.99, 'Cargos y Abonos': 0.36, 'Saldo a Diferir': 12.63, 'Cuotas': '1/36'},
    {'Número de Autorización': 'R06526', 'Fecha de Transacción': '2025-02-09', 'Descripción': 'Disney PLUS VR MONEDA ORIG 23450.0 USA', 'Valor Original': 5.65, 'Cargos y Abonos': 0.16, 'Saldo a Diferir': 5.49, 'Cuotas': '1/36'},
    {'Número de Autorización': 'R05406', 'Fecha de Transacción': '2025-02-09', 'Descripción': 'DISNEY DTC LATAM INC. VR MONEDA ORIG 46900.0 USA', 'Valor Original': 11.3, 'Cargos y Abonos': 0.31, 'Saldo a Diferir': 10.99, 'Cuotas': '1/36'},
    {'Número de Autorización': 'R03502', 'Fecha de Transacción': '2025-02-07', 'Descripción': 'NADEL', 'Valor Original': 1.0, 'Cargos y Abonos': 0.03, 'Saldo a Diferir': 0.97, 'Cuotas': '1/36'},
    {'Número de Autorización': 'T05964', 'Fecha de Transacción': '2025-02-06', 'Descripción': 'Scribd Inc *496589665', 'Valor Original': 10.7, 'Cargos y Abonos': 0.3, 'Saldo a Diferir': 10.4, 'Cuotas': '1/36'},
    {'Número de Autorización': 'T01736', 'Fecha de Transacción': '2025-02-05', 'Descripción': 'APPLE.COM/BILL VR MONEDA ORIG 15900.0 USA', 'Valor Original': 3.79, 'Cargos y Abonos': 0.11, 'Saldo a Diferir': 3.68, 'Cuotas': '1/36'},
    {'Número de Autorización': 'T07880', 'Fecha de Transacción': '2025-02-05', 'Descripción': 'APPLE.COM BILL VR MONEDA ORIG 124900.0 USA', 'Valor Original': 29.75, 'Cargos y Abonos': 0.83, 'Saldo a Diferir': 28.92, 'Cuotas': '1/36'},
    {'Número de Autorización': 'T00259', 'Fecha de Transacción': '2025-02-04', 'Descripción': 'Nintendo CA1351525990', 'Valor Original': 19.99, 'Cargos y Abonos': 0.56, 'Saldo a Diferir': 19.43, 'Cuotas': '1/36'},
    {'Número de Autorización': 'R00562', 'Fecha de Transacción': '2025-02-04', 'Descripción': 'NEBULA SUBSCRIPTION', 'Valor Original': 6.0, 'Cargos y Abonos': 0.17, 'Saldo a Diferir': 5.83, 'Cuotas': '1/36'},
    {'Número de Autorización': 'R07628', 'Fecha de Transacción': '2025-02-03', 'Descripción': 'AMAZON MKTPL*N55XV0773', 'Valor Original': 86.9, 'Cargos y Abonos': 2.41, 'Saldo a Diferir': 84.22, 'Cuotas': '1/36'}
]

do_exp = [
    {'Número de Autorización': '', 'Fecha de Transacción': '2025-02-28', 'Descripción': 'INTERESES CORRIENTES', 'Valor Original': 6598.04, 'Cargos y Abonos': 6598.04, 'Saldo a Diferir': 0.0, 'Cuotas': ''},
    {'Número de Autorización': '000000', 'Fecha de Transacción': '2025-02-28', 'Descripción': 'CUOTA DE MANEJO', 'Valor Original': 48490.0, 'Cargos y Abonos': 48490.0, 'Saldo a Diferir': 0.0, 'Cuotas': ''},
    {'Número de Autorización': 'T04877', 'Fecha de Transacción': '2025-02-27', 'Descripción': 'DLO*Spotify', 'Valor Original': 26400.0, 'Cargos y Abonos': 26400.0, 'Saldo a Diferir': 0.0, 'Cuotas': '1/1'},
    {'Número de Autorización': 'R01915', 'Fecha de Transacción': '2025-02-25', 'Descripción': 'UBER RIDES', 'Valor Original': 29492.0, 'Cargos y Abonos': 29492.0, 'Saldo a Diferir': 0.0, 'Cuotas': '1/1'},
    {'Número de Autorización': 'R08071', 'Fecha de Transacción': '2025-02-25', 'Descripción': 'UBER RIDES', 'Valor Original': 29555.0, 'Cargos y Abonos': 29555.0, 'Saldo a Diferir': 0.0, 'Cuotas': '1/1'},
    {'Número de Autorización': 'R04507', 'Fecha de Transacción': '2025-02-25', 'Descripción': 'UBER RIDES', 'Valor Original': 30203.0, 'Cargos y Abonos': 30203.0, 'Saldo a Diferir': 0.0, 'Cuotas': '1/1'},
    {'Número de Autorización': 'H07367', 'Fecha de Transacción': '2025-02-25', 'Descripción': 'SANTA MARTA MARRIOT RE', 'Valor Original': 947722.0, 'Cargos y Abonos': 947722.0, 'Saldo a Diferir': 0.0, 'Cuotas': '1/1'},
    {'Número de Autorización': 'H06043', 'Fecha de Transacción': '2025-02-25', 'Descripción': 'SANTA MARTA MARRIOT RE', 'Valor Original': 272055.0, 'Cargos y Abonos': 272055.0, 'Saldo a Diferir': 0.0, 'Cuotas': '1/1'},
    {'Número de Autorización': '000000', 'Fecha de Transacción': '2025-02-24', 'Descripción': 'COMISION AVANCE CAJERO', 'Valor Original': 7460.0, 'Cargos y Abonos': 7460.0, 'Saldo a Diferir': 0.0, 'Cuotas': ''},
    {'Número de Autorización': 'R06381', 'Fecha de Transacción': '2025-02-24', 'Descripción': 'UBER RIDES', 'Valor Original': 10774.0, 'Cargos y Abonos': 10774.0, 'Saldo a Diferir': 0.0, 'Cuotas': '1/1'},
    {'Número de Autorización': 'R07715', 'Fecha de Transacción': '2025-02-24', 'Descripción': 'UBER RIDES', 'Valor Original': 9610.0, 'Cargos y Abonos': 9610.0, 'Saldo a Diferir': 0.0, 'Cuotas': '1/1'},
    {'Número de Autorización': 'R00697', 'Fecha de Transacción': '2025-02-24', 'Descripción': 'UBER RIDES', 'Valor Original': 29563.0, 'Cargos y Abonos': 29563.0, 'Saldo a Diferir': 0.0, 'Cuotas': '1/1'},
    {'Número de Autorización': 'F07063', 'Fecha de Transacción': '2025-02-24', 'Descripción': 'SAMARIAN CO SAS', 'Valor Original': 209778.0, 'Cargos y Abonos': 209778.0, 'Saldo a Diferir': 0.0, 'Cuotas': '1/1'},
    {'Número de Autorización': 'R06018', 'Fecha de Transacción': '2025-02-24', 'Descripción': 'INGLESA 300', 'Valor Original': 68900.0, 'Cargos y Abonos': 68900.0, 'Saldo a Diferir': 0.0, 'Cuotas': '1/1'},
    {'Número de Autorización': 'R00770', 'Fecha de Transacción': '2025-02-24', 'Descripción': 'COMCEL PAGO DE FACTURA', 'Valor Original': 208578.0, 'Cargos y Abonos': 208578.0, 'Saldo a Diferir': 0.0, 'Cuotas': '1/1'},
    {'Número de Autorización': 'X07118', 'Fecha de Transacción': '2025-02-24', 'Descripción': 'LATAM AIRLINES COLOMBI', 'Valor Original': 91900.0, 'Cargos y Abonos': 91900.0, 'Saldo a Diferir': 0.0, 'Cuotas': '1/1'},
    {'Número de Autorización': 'F04982', 'Fecha de Transacción': '2025-02-24', 'Descripción': 'LULO CAFE BAR', 'Valor Original': 120230.0, 'Cargos y Abonos': 120230.0, 'Saldo a Diferir': 0.0, 'Cuotas': '1/1'},
    {'Número de Autorización': 'F05289', 'Fecha de Transacción': '2025-02-22', 'Descripción': 'GUASIMO RESTAURANTE SA', 'Valor Original': 346352.0, 'Cargos y Abonos': 346352.0, 'Saldo a Diferir': 0.0, 'Cuotas': '1/1'},
    {'Número de Autorización': 'R02869', 'Fecha de Transacción': '2025-02-22', 'Descripción': 'UBER RIDES', 'Valor Original': 29573.0, 'Cargos y Abonos': 29573.0, 'Saldo a Diferir': 0.0, 'Cuotas': '1/1'},
    {'Número de Autorización': 'H06921', 'Fecha de Transacción': '2025-02-22', 'Descripción': 'SANTA MARTA MARRIOT RE', 'Valor Original': 1144404.0, 'Cargos y Abonos': 1144404.0, 'Saldo a Diferir': 0.0, 'Cuotas': '1/1'},        
    {'Número de Autorización': 'R04902', 'Fecha de Transacción': '2025-02-22', 'Descripción': 'ANANDA TALLER DULCE 11', 'Valor Original': 49500.0, 'Cargos y Abonos': 49500.0, 'Saldo a Diferir': 0.0, 'Cuotas': '1/1'},
    {'Número de Autorización': 'H08960', 'Fecha de Transacción': '2025-02-22', 'Descripción': 'SANTA MARTA MARRIOT RE', 'Valor Original': 90685.0, 'Cargos y Abonos': 90685.0, 'Saldo a Diferir': 0.0, 'Cuotas': '1/1'},
    {'Número de Autorización': 'Z06486', 'Fecha de Transacción': '2025-02-22', 'Descripción': 'AVANCE CAJERO BANCOLOMBIA', 'Valor Original': 500000.0, 'Cargos y Abonos': 20833.33, 'Saldo a Diferir': 479166.67, 'Cuotas': '1/24'},
    {'Número de Autorización': 'R04852', 'Fecha de Transacción': '2025-02-19', 'Descripción': 'CDA CAPRI', 'Valor Original': 302673.0, 'Cargos y Abonos': 302673.0, 'Saldo a Diferir': 0.0, 'Cuotas': '1/1'},
    {'Número de Autorización': 'R00807', 'Fecha de Transacción': '2025-02-18', 'Descripción': 'DLO*RAPPI COLOMBIA', 'Valor Original': 261316.0, 'Cargos y Abonos': 261316.0, 'Saldo a Diferir': 0.0, 'Cuotas': '1/1'},
    {'Número de Autorización': 'U03368', 'Fecha de Transacción': '2025-02-18', 'Descripción': 'CTRO DIAGNOST AUTOM VA', 'Valor Original': 644130.0, 'Cargos y Abonos': 644130.0, 'Saldo a Diferir': 0.0, 'Cuotas': '1/1'},
    {'Número de Autorización': 'R00078', 'Fecha de Transacción': '2025-02-16', 'Descripción': 'DLO*RAPPI COLOMBIA', 'Valor Original': 121150.0, 'Cargos y Abonos': 121150.0, 'Saldo a Diferir': 0.0, 'Cuotas': '1/1'},
    {'Número de Autorización': 'R02687', 'Fecha de Transacción': '2025-02-16', 'Descripción': 'DLO*RAPPI COLOMBIA', 'Valor Original': 17250.0, 'Cargos y Abonos': 17250.0, 'Saldo a Diferir': 0.0, 'Cuotas': '1/1'},
    {'Número de Autorización': 'R00958', 'Fecha de Transacción': '2025-02-15', 'Descripción': 'CARULLA TRADE CENTER', 'Valor Original': 69754.0, 'Cargos y Abonos': 69754.0, 'Saldo a Diferir': 0.0, 'Cuotas': '1/1'},
    {'Número de Autorización': 'R00214', 'Fecha de Transacción': '2025-02-15', 'Descripción': 'RAPPI*RAPPI COLOMBIA', 'Valor Original': 135200.0, 'Cargos y Abonos': 135200.0, 'Saldo a Diferir': 0.0, 'Cuotas': '1/1'},
    {'Número de Autorización': 'R03326', 'Fecha de Transacción': '2025-02-14', 'Descripción': 'UBER RIDES', 'Valor Original': 25216.0, 'Cargos y Abonos': 25216.0, 'Saldo a Diferir': 0.0, 'Cuotas': '1/1'},
    {'Número de Autorización': 'R01654', 'Fecha de Transacción': '2025-02-14', 'Descripción': 'RAPPI*PRO COLOMBIA', 'Valor Original': 23490.0, 'Cargos y Abonos': 23490.0, 'Saldo a Diferir': 0.0, 'Cuotas': '1/1'},
    {'Número de Autorización': 'R08218', 'Fecha de Transacción': '2025-02-14', 'Descripción': 'AMAZON.COM', 'Valor Original': 317687.0, 'Cargos y Abonos': 317687.0, 'Saldo a Diferir': 0.0, 'Cuotas': '1/1'},
    {'Número de Autorización': 'R09099', 'Fecha de Transacción': '2025-02-14', 'Descripción': 'DLO*RAPPI COLOMBIA', 'Valor Original': 18950.0, 'Cargos y Abonos': 18950.0, 'Saldo a Diferir': 0.0, 'Cuotas': '1/1'},
    {'Número de Autorización': 'R09123', 'Fecha de Transacción': '2025-02-13', 'Descripción': 'DLO*RAPPI COLOMBIA', 'Valor Original': 14400.0, 'Cargos y Abonos': 14400.0, 'Saldo a Diferir': 0.0, 'Cuotas': '1/1'},
    {'Número de Autorización': 'R09237', 'Fecha de Transacción': '2025-02-12', 'Descripción': 'UBER RIDES', 'Valor Original': 26651.0, 'Cargos y Abonos': 26651.0, 'Saldo a Diferir': 0.0, 'Cuotas': '1/1'},
    {'Número de Autorización': 'R08723', 'Fecha de Transacción': '2025-02-12', 'Descripción': 'UBER RIDES', 'Valor Original': 26762.0, 'Cargos y Abonos': 26762.0, 'Saldo a Diferir': 0.0, 'Cuotas': '1/1'},
    {'Número de Autorización': 'R02726', 'Fecha de Transacción': '2025-02-12', 'Descripción': 'ADOBE', 'Valor Original': 333200.0, 'Cargos y Abonos': 333200.0, 'Saldo a Diferir': 0.0, 'Cuotas': '1/1'},
    {'Número de Autorización': 'R05583', 'Fecha de Transacción': '2025-02-11', 'Descripción': 'MOVISTAR PAGOSEPAYCO', 'Valor Original': 167087.0, 'Cargos y Abonos': 167087.0, 'Saldo a Diferir': 0.0, 'Cuotas': '1/1'},
    {'Número de Autorización': 'F09183', 'Fecha de Transacción': '2025-02-10', 'Descripción': 'DiDi co Food', 'Valor Original': 28809.0, 'Cargos y Abonos': 28809.0, 'Saldo a Diferir': 0.0, 'Cuotas': '1/1'},
    {'Número de Autorización': 'T07215', 'Fecha de Transacción': '2025-02-09', 'Descripción': 'PPRO*MICROSOFT', 'Valor Original': 42990.0, 'Cargos y Abonos': 42990.0, 'Saldo a Diferir': 0.0, 'Cuotas': '1/1'},
    {'Número de Autorización': 'R00970', 'Fecha de Transacción': '2025-02-09', 'Descripción': 'EDS ROOSEVELT', 'Valor Original': 183535.0, 'Cargos y Abonos': 183535.0, 'Saldo a Diferir': 0.0, 'Cuotas': '1/1'},
    {'Número de Autorización': 'R05440', 'Fecha de Transacción': '2025-02-09', 'Descripción': 'DLO*RAPPI COLOMBIA', 'Valor Original': 46350.0, 'Cargos y Abonos': 46350.0, 'Saldo a Diferir': 0.0, 'Cuotas': '1/1'},
    {'Número de Autorización': 'R07896', 'Fecha de Transacción': '2025-02-08', 'Descripción': 'EL MOLINO LA 14 CENTEN', 'Valor Original': 14900.0, 'Cargos y Abonos': 14900.0, 'Saldo a Diferir': 0.0, 'Cuotas': '1/1'},
    {'Número de Autorización': 'R01686', 'Fecha de Transacción': '2025-02-08', 'Descripción': 'SC CENTENARIO', 'Valor Original': 730793.0, 'Cargos y Abonos': 730793.0, 'Saldo a Diferir': 0.0, 'Cuotas': '1/1'},
    {'Número de Autorización': '000000', 'Fecha de Transacción': '2025-02-07', 'Descripción': 'COMISION AVANCE CAJERO', 'Valor Original': 7460.0, 'Cargos y Abonos': 7460.0, 'Saldo a Diferir': 0.0, 'Cuotas': ''},
    {'Número de Autorización': 'R03058', 'Fecha de Transacción': '2025-02-07', 'Descripción': 'INVERSIONES TNS CHIPIC', 'Valor Original': 59400.0, 'Cargos y Abonos': 59400.0, 'Saldo a Diferir': 0.0, 'Cuotas': '1/1'},
    {'Número de Autorización': 'R02943', 'Fecha de Transacción': '2025-02-07', 'Descripción': 'BOSI CHIPICHAPE N 2', 'Valor Original': 524900.0, 'Cargos y Abonos': 524900.0, 'Saldo a Diferir': 0.0, 'Cuotas': '1/1'},
    {'Número de Autorización': 'F07100', 'Fecha de Transacción': '2025-02-07', 'Descripción': 'HAMBURGUESAS EL CORRAL', 'Valor Original': 88800.0, 'Cargos y Abonos': 88800.0, 'Saldo a Diferir': 0.0, 'Cuotas': '1/1'},
    {'Número de Autorización': 'R02775', 'Fecha de Transacción': '2025-02-07', 'Descripción': 'UBER RIDES', 'Valor Original': 12952.0, 'Cargos y Abonos': 12952.0, 'Saldo a Diferir': 0.0, 'Cuotas': '1/1'},
    {'Número de Autorización': 'R08838', 'Fecha de Transacción': '2025-02-07', 'Descripción': 'VELEZ 5030 CHIPICHAPE', 'Valor Original': 329900.0, 'Cargos y Abonos': 329900.0, 'Saldo a Diferir': 0.0, 'Cuotas': '1/1'},
    {'Número de Autorización': 'F09124', 'Fecha de Transacción': '2025-02-07', 'Descripción': 'SUSHI GREEN 4', 'Valor Original': 41300.0, 'Cargos y Abonos': 41300.0, 'Saldo a Diferir': 0.0, 'Cuotas': '1/1'},
    {'Número de Autorización': 'Z03019', 'Fecha de Transacción': '2025-02-07', 'Descripción': 'AVANCE CAJERO BANCOLOMBIA', 'Valor Original': 300000.0, 'Cargos y Abonos': 12500.0, 'Saldo a Diferir': 287500.0, 'Cuotas': '1/24'},  
    {'Número de Autorización': 'F07816', 'Fecha de Transacción': '2025-02-06', 'Descripción': 'DiDi co Food', 'Valor Original': 25105.0, 'Cargos y Abonos': 25105.0, 'Saldo a Diferir': 0.0, 'Cuotas': '1/1'},
    {'Número de Autorización': 'F00265', 'Fecha de Transacción': '2025-02-05', 'Descripción': 'DiDi CO Food', 'Valor Original': 17670.0, 'Cargos y Abonos': 17670.0, 'Saldo a Diferir': 0.0, 'Cuotas': '1/1'},
    {'Número de Autorización': 'R01075', 'Fecha de Transacción': '2025-02-04', 'Descripción': 'RAPPI*RAPPI COLOMBIA', 'Valor Original': 259300.0, 'Cargos y Abonos': 259300.0, 'Saldo a Diferir': 0.0, 'Cuotas': '1/1'},
    {'Número de Autorización': 'R06088', 'Fecha de Transacción': '2025-02-04', 'Descripción': 'DLO*RAPPI COLOMBIA', 'Valor Original': 36300.0, 'Cargos y Abonos': 36300.0, 'Saldo a Diferir': 0.0, 'Cuotas': '1/1'},
    {'Número de Autorización': 'R04890', 'Fecha de Transacción': '2025-02-02', 'Descripción': 'COCINA COREANA URIMURI', 'Valor Original': 152416.0, 'Cargos y Abonos': 152416.0, 'Saldo a Diferir': 0.0, 'Cuotas': '1/1'},
    {'Número de Autorización': 'R08076', 'Fecha de Transacción': '2025-02-02', 'Descripción': 'CALATHEA', 'Valor Original': 34500.0, 'Cargos y Abonos': 34500.0, 'Saldo a Diferir': 0.0, 'Cuotas': '1/1'},
    {'Número de Autorización': 'F03778', 'Fecha de Transacción': '2025-02-01', 'Descripción': 'BENGALA Y BANDOLERO', 'Valor Original': 40000.0, 'Cargos y Abonos': 40000.0, 'Saldo a Diferir': 0.0, 'Cuotas': '1/1'},
    {'Número de Autorización': 'R03434', 'Fecha de Transacción': '2025-02-01', 'Descripción': 'UBER RIDES', 'Valor Original': 11905.0, 'Cargos y Abonos': 11905.0, 'Saldo a Diferir': 0.0, 'Cuotas': '1/1'},
    {'Número de Autorización': 'R05755', 'Fecha de Transacción': '2025-02-01', 'Descripción': 'UBER RIDES', 'Valor Original': 13196.0, 'Cargos y Abonos': 13196.0, 'Saldo a Diferir': 0.0, 'Cuotas': '1/1'},
    {'Número de Autorización': 'R03528', 'Fecha de Transacción': '2025-02-01', 'Descripción': 'DLO*RAPPI COLOMBIA', 'Valor Original': 140750.0, 'Cargos y Abonos': 140750.0, 'Saldo a Diferir': 0.0, 'Cuotas': '1/1'},
    {'Número de Autorización': 'R03244', 'Fecha de Transacción': '2025-02-01', 'Descripción': 'DLO*RAPPI COLOMBIA', 'Valor Original': 44250.0, 'Cargos y Abonos': 44250.0, 'Saldo a Diferir': 0.0, 'Cuotas': '1/1'},
    {'Número de Autorización': 'R06337', 'Fecha de Transacción': '2025-02-01', 'Descripción': 'DROGUERIA NATURFARMA D', 'Valor Original': 6800.0, 'Cargos y Abonos': 6800.0, 'Saldo a Diferir': 0.0, 'Cuotas': '1/1'},
    {'Número de Autorización': 'F05421', 'Fecha de Transacción': '2025-02-01', 'Descripción': 'DISCO BANDOLEROS S A S', 'Valor Original': 94600.0, 'Cargos y Abonos': 94600.0, 'Saldo a Diferir': 0.0, 'Cuotas': '1/1'},
    {'Número de Autorización': 'F09754', 'Fecha de Transacción': '2025-01-31', 'Descripción': 'TAQUERIA EL BUEN PASTO', 'Valor Original': 103250.0, 'Cargos y Abonos': 103250.0, 'Saldo a Diferir': 0.0, 'Cuotas': '1/1'},
    {'Número de Autorización': 'R09903', 'Fecha de Transacción': '2025-01-31', 'Descripción': 'DLO*RAPPI COLOMBIA', 'Valor Original': 167820.0, 'Cargos y Abonos': 167820.0, 'Saldo a Diferir': 0.0, 'Cuotas': '1/1'},
    {'Número de Autorización': 'F08942', 'Fecha de Transacción': '2025-01-30', 'Descripción': 'DiDi co Food', 'Valor Original': 49127.0, 'Cargos y Abonos': 49126.71, 'Saldo a Diferir': 0.0, 'Cuotas': '1/1'}
]




