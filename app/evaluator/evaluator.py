import numpy as np
import pickle


field_names = [
    '血白细胞计数(WBC)', 
    '淋巴细胞百分比(LY)',
    '单核细胞百分比(MO)',
    '粒细胞百分比',
    '嗜酸性细胞比例(EO)',
    '嗜碱性细胞比例(BASO)',
    '粒细胞绝对值(Neu#)',
    '单核细胞绝对值(MO#)',
    '嗜酸细胞绝对值(EO#)',
    '嗜碱细胞绝对值(BASO#)',
    '淋巴细胞绝对值(LY#)',
    '血红细胞计数(RBC)',
    '血红蛋白(HGB)',
    '红细胞积压(HCT)',
    '平均RBC体积(MCV)',
    '平均RBC血红蛋白(MCH)',
    '血红蛋白浓度(MCHC)',
    '红细胞变异系数(RDW-CV)',
    '红细胞分布宽度(RDW-SD)',
    '血小板计数(PLT)',
    '平均血小板体积(MPV)',
    '葡萄糖(Glu)',
    '总蛋白(TP)',
    '白蛋白(ALB)',
    '球蛋白(GLB)',
    '白蛋白/球蛋白(A/G)',
    '总胆红素(TBIL)',
    '直接胆红素(D-BIL)',
    '谷丙转氨酶(ALT)',
    '谷草转氨酶(AST)',
    '谷氨酰转肽酶(GGT)',
    '碱性磷酸酶(AKP)',
    '总胆固醇(CHO)',
    '低密度脂蛋白胆固醇(LDL-C)',
    '尿素(UREa)',
    '肌酐(CREA)',
    '尿酸(UA)',
    '促甲状腺素(TSH)',
    '甘油三酯(TG)',
    '高密度脂蛋白(HDL-C)',
]


def estimate(record):
    with open('vrci_classify.pickle', 'rb') as file_vrci, \
            open('up_classify.pickle', 'rb') as file_up:
        model_vrci = pickle.load(file_vrci)
        model_up = pickle.load(file_up)

    data_raw = record.get_metrics()
    label = record.label
    up = record.up

    vrci = data_raw.get('VRCI')
    if vrci:
        vrci = float(vrci)
        if vrci > 12.9:
            label = 2
        elif vrci > 9.5:
            label = 1
        else:
            label = 0

    data = []
    for key in field_names:
        data.append(data_raw.get(key, -1))

    if label is None:
        data_0 = (np.array(data, dtype='float64')).reshape((1, -1))
        label = int(model_vrci.predict(data_0))

    if up is None:
        data.insert(0, label)
        data_1 = (np.array(data, dtype='float32')).reshape((1, -1))
        up = int(model_up.predict(data_1))

    record.label = label
    record.up = up
