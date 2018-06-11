from pprint import pprint
import json
import requests
import time

TOKEN = '7b23e40ad10e08d3b7a8ec0956f2c57910c455e886b480b' \
        '7d9fb59859870658c4a0b8fdc4dd494db19099'


def input_user_id():
    # print('Enter user_id')
    # source_uid = input()
    source_uid = 5030613
    print("USER_ID HAS BEEN ENTERED")
    return source_uid


def get_user_friends():
    source_uid = input_user_id
    response = requests.get(
        'https://api.vk.com/method/friends.get',
        params=dict(
            v='5.74',
            access_token=TOKEN,
            source_uid=source_uid,
        )
    )
    print('User friend list received')
    return response


def filter_user_live_friend_list():
    """ Return filtered list of friends without deleted and banned user_ids."""
    user_friends = get_user_friends()
    user_friend_list = user_friends.json()['response']['items']
    user_friend_count = user_friends.json()['response']['count']
    user_live_friend_list = []
    i = 0
    print("Filtering process user's friends has begun")
    for user_id in user_friend_list:
        time.sleep(1/3)
        print('* Left {} users to process'.format(user_friend_count-i))
        try:

            if (get_user_brief_info(user_id)
               .json()['response'][0]['deactivated'] is not None):
                continue
        except:
            user_live_friend_list.append(user_id)
        i += 1
    return user_live_friend_list


def get_user_brief_info(user_id):
    """Return id, first_name, last_name, deactivated"""
    response = requests.get(
        'https://api.vk.com/method/users.get',
        params=dict(
            v='5.74',
            access_token=TOKEN,
            user_ids=user_id
        )
    )
    return response


def get_user_groups():
    source_uid = input_user_id
    response = requests.get(
        'https://api.vk.com/method/groups.get',
        params=dict(
            v='5.74',
            access_token=TOKEN,
            source_uid=source_uid,
            extended=1,
            fields='members_count'
        )
    )
    print("User's groups list received")
    return response


def get_group_members(group_id):
    response = requests.get(
        'https://api.vk.com/method/groups.getMembers',
        params=dict(
            v='5.74',
            access_token=TOKEN,
            group_id=group_id
        )
    )
    print("Group member list received")
    return response


def is_user_in_group(friend, group):
    response = requests.get(
        'https://api.vk.com/method/groups.isMember',
        params=dict(
            v='5.74',
            access_token=TOKEN,
            #user_id=friend,
            user_ids=friend,
            group_id=group
        )
    )
    return response


def write_to_json(file):
    with open('data.txt', 'w', encoding='utf-8') as outfile:
        json.dump(file, outfile, ensure_ascii=False)


def create_list_of_group():
    """Return list of groups that specified user belongs to without friends"""
    time.sleep(1/3)
    user_groups_request = get_user_groups()
    user_groups_list = user_groups_request.json()['response']['items']
    user_groups_count = user_groups_request.json()['response']['count']

    time.sleep(1/3)
    friends = str(filter_user_live_friend_list()).strip('[]')

    groups_wout_friends = []
    i = 0
    for group in user_groups_list:
        print('Left {} groups to process'.format(user_groups_count - i))
        time.sleep(1/3)
        are_users_in_group_status_list = is_user_in_group(friends, group['id'])

        for member in are_users_in_group_status_list.json()['response']:
            if member['member'] == 0:
                pass
            else:
                print('Added')
                groups_wout_friends.append(
                    {
                        'id': group['id'],
                        'name': group['name'],
                        'members_count': group['members_count']
                    }
                )
                break

        i += 1
    return groups_wout_friends


input_user_id = input_user_id()
groups_wout_friends = create_list_of_group()
write_to_json(groups_wout_friends)

# Checking JSON layout
# with open('data.txt', 'r', encoding='utf-8') as out:
#     text = json.load(out)
#     print(text)