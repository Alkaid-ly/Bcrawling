import json
import requests
import logging

# 设置日志格式和日志级别
logging.basicConfig(level=logging.INFO,
                    format='%(asctime)s - %(levelname)s - %(message)s',
                    datefmt='%Y-%m-%d %H:%M:%S')
# 推荐cookie使用三引号包裹
headers = {
    'cookie': '''在此处放置你的cookie'''
    ,
    'user-agent': '此处放置你的user-agent'
}

BASE_URL = 'https://api.bilibili.com/x/v2/reply/wbi/main'


# 查询参数
def get_query_params(oid, w_rid, wts):
    return {
        'oid': oid,
        'type': '1',
        'mode': '3',
        'pagination_str': '{"offset":""}',
        'plat': '1',
        'seek_rpid': '',
        'web_location': '1315875',
        'w_rid': w_rid,
        'wts': wts
    }


# 获取主评论
def get_main_replies(oid, w_rid, wts):
    response = requests.get(BASE_URL, params=get_query_params(oid, w_rid, wts), headers=headers)
    if response.status_code == 200:
        json_data = response.json()
        return json_data.get('data', {}).get('replies', [])
    else:
        logging.error(f"Failed to fetch main replies: {response.status_code}")
        return []


# 获取子评论
def get_sub_replies(oid, root_id):
    sub_query_data = {
        'oid': oid,
        'type': 1,
        'root': root_id,
        'ps': 10,
        'pn': 1,
        'web_location': '333.788'
    }
    sub_url = 'https://api.bilibili.com/x/v2/reply/reply'
    sub_response = requests.get(sub_url, params=sub_query_data, headers=headers)
    if sub_response.status_code == 200:
        json_sub_data = sub_response.json()
        return json_sub_data.get('data', {}).get('replies', [])
    else:
        logging.error(f"Failed to fetch sub replies for root_id {root_id}: {sub_response.status_code}")
        return []


# 存储数据到文件
def save_to_file(data, filename="output"):
    with open(f'{filename}.json', 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=4)
    logging.info(f"Data saved to {filename}")


# 主函数，负责获取评论并存储
def main(oid, output_file_name, w_rid, wts):
    # oid = '113148950479383'  # 请根据需要修改 oid
    logging.info(f"Fetching main replies for oid: {oid}")

    # 存储所有评论数据
    all_replies = []
    main_replies = get_main_replies(oid, w_rid, wts)

    for reply in main_replies:
        # 获取用户元信息和评论内容
        nickname = reply['member']['uname']
        content = reply['content']['message']
        logging.info(f'用户{nickname}评论：{content}')

        # 构建主评论字典
        reply_data = {
            'nickname': nickname,
            'content': content,
            'sub_replies': []
        }

        # 检查是否有子评论
        sub_reply_count = int(reply['count'])
        if sub_reply_count > 0:
            logging.info(f"Fetching sub replies for root_id: {reply['rpid']}")
            root_id = reply['rpid']
            sub_replies = get_sub_replies(oid, root_id)
            for sub_reply in sub_replies:
                sub_nickname = sub_reply['member']['uname']
                sub_content = sub_reply['content']['message']
                logging.info(f'\t{sub_nickname}回复道：{sub_content}')
                reply_data['sub_replies'].append({
                    'nickname': sub_nickname,
                    'content': sub_content
                })

        all_replies.append(reply_data)

    # 存储所有评论到文件
    save_to_file(all_replies, output_file_name)


if __name__ == "__main__":
    main(oid='', output_file_name='',
         w_rid='', wts='')
