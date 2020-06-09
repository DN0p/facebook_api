import requests
import json
import csv

my_token = 'enter_token'
url = 'https://graph.facebook.com/me?fields=feed&access_token=' + my_token


def get_json(req_url):
    return json.loads(requests.get(req_url).text)


posts_data = get_json(url)['feed']['data']
created_date = []
posts_id = []
links_posts = []
end_data = []

for i in posts_data:
    posts_id.append(i['id'])
    created_date.append(i['created_time'])


def get_batch_requests(local_post_id, req_string):
    url_get_batch = []

    for x in local_post_id:
        dict_batch = {}
        dict_batch['method'] = 'GET'
        dict_batch['relative_url'] = x + req_string
        url_get_batch.append(dict_batch)

    batch_to_json = json.dumps(url_get_batch)
    url_by_posts = 'https://graph.facebook.com/me?batch=' + batch_to_json + '&include_headers=false&access_token=' + my_token
    req = requests.post(url_by_posts)
    return json.loads(req.text)


def get_req_repost(repost_id):
    url = 'https://graph.facebook.com/' + repost_id + '?fields=from&access_token=' + my_token
    req = requests.get(url)
    return json.loads(req.text)['from']['id']


permalink_url = get_batch_requests(posts_id, '?fields=permalink_url,place,timeline_visibility')
like = get_batch_requests(posts_id, '/reactions/')
comments = get_batch_requests(posts_id, '/comments')
reposts = get_batch_requests(posts_id, '/sharedposts/')


def like_cycle(i):
    like_inner = ''
    like_json = json.loads(like[i]['body'])
    if not like_json['data']:
        like_inner = 'No_like'
    else:
        for j in range(len(like_json['data'])):
            like_inner += (str(like_json['data'][j]['id']) + ',')
    return like_inner


def comment_cycle(i):
    comment_inner = ''
    comments_json = json.loads(comments[i]['body'])
    if not comments_json['data']:
        comment_inner = 'No_comment'
    else:
        for j in range(len(comments_json['data'])):
            comment_inner += (str(comments_json['data'][j]['from']['id']) + ',')
    return comment_inner


def reposts_cycle(i):
    reposts_inner = ''
    reposts_json = json.loads(reposts[i]['body'])
    if not reposts_json['data']:
        reposts_inner = 'No_reposts'
    else:
        for j in range(len(reposts_json['data'])):
            # сделано для теста. При большом кол-ве репостов нужно формировать batch запрос
            reposts_inner += (str(get_req_repost(reposts_json['data'][j]['id'])) + ',')
    return reposts_inner


for i in range(len(permalink_url)):
    x = []
    per_json = json.loads(permalink_url[i]['body'])
    x.append(per_json['permalink_url'])
    x.append(per_json['timeline_visibility'])
    x.append(created_date[i])
    try:
        x.append(per_json['place']['location']['city'])
    except:
        x.append('No_location')
    x.append(like_cycle(i))
    x.append(comment_cycle(i))
    x.append(reposts_cycle(i))
    end_data.append(x)


def csv_writer(data, path):
    with open(path, 'w', newline='') as csv_file:
        csv_file.write('ссылка на пост;статус видимости;дата публикации;локация;id кто лайкнул запись;id кто прокомментировал запись;id кто репостнул запись;\n')
        writer = csv.writer(csv_file, delimiter=';')
        for line in data:
            writer.writerow(line)


path = 'output.csv'
csv_writer(end_data, path)
