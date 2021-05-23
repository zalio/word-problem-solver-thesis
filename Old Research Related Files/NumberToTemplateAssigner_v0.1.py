
# BERT contextual embedding araştır!!!

import pandas as pd
import re

df = pd.read_json('./data/alg514.json')

df = df[['sQuestion', 'templateType']]

predicted_template_types = []
for t in df['templateType']:
    predicted_template_types.append(t)


class TemplateType:
    def __init__(self, type_num, eq1, eq2=None):
        self.type_num = type_num
        self.eq1 = eq1
        self.eq2 = eq2

    # bunu kullanıp eq1 ve eq2 içinde kaç adet n (rakamla yazılan sayı değeri için bilinmeyen) var onu bul.
    # bunun sonucunu aşağıda important_num_from_each_question'da gezerken içindeki type eşleşmelerine göre bulup karşılaştır.
    def get_num_of_n_values(self):

        return


def read_and_fill_template_type_dict():
    file1 = open('./data/templates0_27.txt', 'r')
    lines = file1.readlines()
    all_template_types = []
    for i in range(1, len(lines)-1):
        temp_type_num = lines[i].split(',')[-2][:-1].strip()
        pattern_match = re.findall(r"\'.+\'", lines[i])
        temp_eq1 = pattern_match[0].split(', ')[0][1:-1]
        if len(pattern_match[0].split(', ')) == 2:
            temp_eq2 = pattern_match[0].split(', ')[1][1:-1]
            temp_type_object = TemplateType(temp_type_num, temp_eq1, temp_eq2)
        else:
            temp_type_object = TemplateType(temp_type_num, temp_eq1)
        all_template_types.append(temp_type_object)
    return all_template_types


# burası tamam!!! burada sadece sayıları çıkart. kalan iş alignment problemi!!!
def extract_important_num_from_df(dataframe, predicted_template_type_list, all_template_types):
    important_num_from_each_question = []
    for i in dataframe['sQuestion']:
        matches = re.findall(r"[-+]?\d*\.\d+|\d+", i)
        # print("matches:", i, "-->", matches)
        important_num_from_each_question.append(matches)
        print(matches)
    # for j in range(len(important_num_from_each_question)):
    return important_num_from_each_question


all_template_type_list = read_and_fill_template_type_dict()
extract_important_num_from_df(df, predicted_template_types, all_template_type_list)


# ************** BURADAKİ İŞİ TEMPLATECLASSIFIER İÇİNDE YAP. ORANIN EN ALTINA BUNU EKLE.
# TANIMLADIĞIN FONKSİYON AYRICA TAHMİN EDİLEN TEMPLATE TYPE NUMARALARINI DA VER.
# BU ŞEKİLDE QUESTINUN İÇİNDEKİ RAKAMLA YAZILMIŞ HER SAYIYI ÇIKART, one YA DA two OLARAK YAZILMIŞSA BİLE.
# SONRA AİT OLDUĞU TEMPLATE TYPE'IN İÇİNDEN KAÇ SAYI GEREKTİĞİNİ BUL
# VE O KADARINI QUESTİONS'UN İÇİNDEKİ one, two GİBİLER HARİCİ SAYILARDAN ÇIKART.
# EĞER PREDİCTED TEMPLATE İÇİNDEKİ YETERİNCE BOŞLUK DOLMAMIŞSA ÖNCE one, two GİBİ KELİMELERİ SAYI OLARAK EKLE.
# BU DA YETMEZSE "a", "an" GİBİ KELİMELERE BAK.
# EN KÖTÜ İHTİMAL: EĞER SORU İÇİNDE İSTENENDEN DAHA FAZLA RAKAMLA YAZILMIŞ SAYI VARSA one, two GİBİLERİ DİREKT UNUT,
# RAKAMLA YAZILMIŞLARIN VERİLDİĞİ SIRAYA GÖRE ONLARA ÖNCELİK VER. YA DA ALTERNATİF YOL BUL.
