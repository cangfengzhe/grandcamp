#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
基于python docxtpl，word版报告自动化
"""

# ---------
# Change Logs:
#
# ---------

__author__ = 'Li Pidong'
__email__ = 'lipidong@126.com'
__version__ = '1.0.1'
__status__ = 'Production'

import os
import sys
if sys.version < '3':  # 兼容2/3
    reload(sys)
    sys.setdefaultencoding('utf-8')
import argparse
import logging
import time

from docxtpl import DocxTemplate, RichText
#  from docx.shared import Mm
#  from docx.enum.section import WD_ORIENT, WD_SECTION
import requests
from requests.packages.urllib3.exceptions import InsecureRequestWarning
# 禁用安全请求警告
requests.packages.urllib3.disable_warnings(InsecureRequestWarning)


USER = 'grandbox'
PASSWD = 'grandbox123'

def read_table(_file_name):
    """
    :_file_name: file name
    :returns: list

    """
    with open(_file_name, 'r') as f:
        for line in f:
            if line.startswith('#'):
                continue
            yield line.split('\t')


def get_data(sample_id='LPM170050_LM17A1000'):
    url = 'https://analyze.grandbox.site/report/reportsnvnew/?datafile={sample_id}&app=grandmgd'.format(sample_id=sample_id)
    r = requests.get(url, auth=(USER, PASSWD), verify=False)
    return r.json()


def proc_dis(info):
    """处理其他变异信息中的遗传方式和表型
    """
    update_info = []
    for gene in info:
        dis_info = '\n'.join([xx['disease'] for xx in gene['diseases']])
        inheritance = '\n'.join([xx['inheritance'] or '-'  for xx in gene['diseases']])
        gene['dis_info'] = RichText(dis_info)
        gene['inheritance'] = RichText(inheritance)
        update_info.append(gene)
    return update_info


def proc_gene_list(dt):
    """处理基因列表，将基因list变成表格
    """
    gene_list = dt['genes']
    gene_list_info = {}
    gene_table = {}
    length = len(gene_list)
    ncol = 8
    nrow = int(length / ncol)
    gene_table = [gene_list[ii * ncol: (ii + 1) * ncol] for ii in range(nrow)]
    if length > nrow * ncol:
        gene_table.append(gene_list[nrow * ncol:] + [''] * (ncol - (length - nrow * ncol)))
    gene_list_info['len'] = length
    gene_list_info['data'] = gene_table
    return gene_list_info


def get_disease_detail2(dis_id):
    """(弃用）获取疾病简介信息
    """
    detail = {}
    # print(dis_id)
    url = 'https://biomeddb.grandbox.site/knowledge/omim/{dis_id}/?format=json'.format(dis_id=dis_id)
    # https://biomeddb.grandbox.site/knowledge/omim/613001/?format=json
    r = requests.get(url, auth=(USER, PASSWD), verify=False)
    json_data = r.json()
    detail['header'] = json_data['titles']['chinese']
    if not detail['header']:
        detail['header'] = json_data['titles']['preferred']
    dis_type = [xx['titles']['chinese'].strip() for xx in json_data['hpos']]
    if dis_type:
        detail['content'] = '疾病概述：典型的临床症状包括{sub_type}。'.format(main_type=dis_type[0], sub_type='、'.join(dis_type))
    else:
        detail['content'] = ''
    return detail


def get_disease_detail(dt):
    """获取疾病简介信息
    """
    detail_list = []
    for key, values in dt['diseaseDes'].items():
        detail = {}
        detail['header'] = values['title']['chinese'] or values['title']['english']
        dis_type = [values['inheritance']] + values['phenotypes']
        detail['content'] = '疾病概述：典型的临床症状包括{sub_type}。'.format(main_type=dis_type[0], sub_type='、'.join(dis_type))
        detail_list.append(detail)
    return detail_list


def get_disease_id(dt):
    """(弃用）获取疾病的id信息
    """
    return dt['diseaseDes'].keys()


def get_var_detail(dt):
    """获取变异详情
    """
    majors = dt['majors']
    var_detail = []
    for xx in majors:
        header = '{gene}基因的{aa}变异'.format(gene=xx['gene'], aa=xx['changes']['NA_changes'])
        if 'fs' in xx['changes']['AA_change']:
            aa_info = '为移码变异，导致蛋白编码提前终止，可能影响蛋白功能;'
        else:
            aa_info = ''
        content = """
        该变异在ExAC普通人数据库东亚人群中的频率为{freq}（*）；{aa_info}生物信息学软件SIFT和Polyphen2预测该变异分别为;该变异目前无文献报道。基于以上证据，我们建议判定该变异为{intervar}变异。
        """.format(freq=xx['freq'], aa_info=aa_info, intervar=xx['intervar'])
        var_detail.append({'header': header, 'content': content.strip()})
    return var_detail


def get_result_desc(dt):
    """获取结果描述
    """
    result_desc = []
    inheritances = dt['resultDes']['inheritances']
    var_gene_list = [xx['gene'] for xx in dt['majors']]

    for k, v in dt['resultDes']['genes'].items():
        count = var_gene_list.count(k)
        content = '{gene}基因是{disease}的致病基因。我们检测到受检者{count}个变异位点。{inheritances}'.format(gene=k, disease=','.join(v),
                                                                                                              inheritances=';'.join(inheritances), count=count)
        result_desc.append(content)

    return result_desc


def log(file_name, logger_name='lipidong', verbose=False):
    logger = logging.getLogger(logger_name)
    formatter = logging.Formatter("%(asctime)s - %(levelname)s - %(message)s")
    handler = logging.FileHandler(file_name)
    handler.setFormatter(formatter)
    logger.addHandler(handler)
    logger.setLevel(logging.INFO)
    if verbose:
        console = logging.StreamHandler()
        console.setLevel(logging.INFO)
        logger.addHandler(console)
    return logger


def create_report(sample_id, template_file, output_path, output_file):
    """生成报告
    """
    dt = get_data(sample_id)
    # dis_detail = get_disease_detail('600974')
    gene_table = proc_gene_list(dt)
    minors_info = proc_dis(dt['minors'])
    var_detail = get_var_detail(dt)
    tpl = DocxTemplate(template_file)
    # read the mutation table
    #  majors_info = [xx for xx in dt['majors']]
    #  dis_details = map(get_disease_detail, get_disease_id(dt))
    result_desc = get_result_desc(dt)
    dis_details = get_disease_detail(dt)

    content = {
        'mut_info': dt['majors'],
        'patient_info': dt['patient']['data'],
        'minors_info': minors_info,
        'null': '无',
        'gene_table': gene_table,
        'var_detail': var_detail,  # 变异详情
        'dis_details': dis_details,  # 疾病简介
        'result_desc': result_desc,
        'gene_info': []
    }
    tpl.render(content)
    if not output_file:
        patient_name = dt['patient']['data']['name']
        output_file = '基因分析报告-{sample_id}-{patient_name}-{date}.docx'.format(sample_id=dt['patient']['data']['sn'],
                                                                                  patient_name=patient_name,
                                                                                  date=time.strftime('%Y-%m-%d', time.localtime(time.time())))
    tpl.save(os.path.join(output_path, output_file))
    # logger.info('报告路径：{path}'.format(path=os.path.join(output_path, output_file)))
    return open(os.path.join(output_path, output_file), 'rb')


def get_args():
    parser = argparse.ArgumentParser(prog='基于python docxtpl，word版报告自动化')
    parser.add_argument('--sample_id', help='Sample ID such as LPM170056_LM17A1180')
    parser.add_argument('--output_path', help='The path of outputfile')
    parser.add_argument('--output_file', help='The file name of word report', default=None)
    parser.add_argument('--template_file', help='docx template file, default=/data/lipidong/work/word-report/grandbox/template.docx',
                        default='/data/lipidong/work/word-report/grandbox/template.docx')
    parser.add_argument('--log', help='log file, default=log.log', default='log.log')
    parser.add_argument("--verbose", help="increase output verbosity",
                        action="store_false")
    if len(sys.argv) == 1:
        parser.print_help()
        exit()
    return parser.parse_args()


def main():
    args = get_args()
    sample_id = args.sample_id
    template_file = args.template_file
    output_path = args.output_path
    output_file = args.output_file
    log_file = args.log
    verbose = args.verbose
    global logger
    logger = log(log_file, verbose=verbose)
    logger.info('正在生成 {sample_id} 报告，请等待……'.format(sample_id=sample_id))
    create_report(sample_id, template_file, output_path, output_file)
    logger.info('报告生成完成')



if __name__ == '__main__':
    main()