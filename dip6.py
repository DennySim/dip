import json
import logging
import requests
import sys
import time

TOKEN = '7b23e40ad10e08d3b7a8ec0956f2c57910c455e886b480b' \
        '7d9fb59859870658c4a0b8fdc4dd494db19099'

debug = True


def get_logger():

    logger = logging.getLogger('http_request_error')
    logger.setLevel(logging.DEBUG)
    sh = logging.StreamHandler()
    sh.setLevel(logging.DEBUG)
    formatter = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    sh.setFormatter(formatter)
    logger.addHandler(sh)
    return logger


def input_user_id():
    # print('Enter user_id')
    # source_uid = input()
    source_uid = 5030613
    print("USER_ID has been entered")
    return source_uid


def input_n_quantity_friends():
    # print('Enter N quantity friends')
    # input_n_quantity_friends = int(input())
    input_n_quantity_friends = 5
    print("N quantity HAS BEEN SET")
    return input_n_quantity_friends


def merge_api_vk_params(add_params):
    default = dict(
        v='5.74',
        access_token=TOKEN
    )
    return dict(default, **add_params)


class RobustRequest(object):

    def __init__(self, f):
        self.f = f

    def __call__(self, *args):
        if debug is True:
            log_error_request = get_logger()
        t = 0
        result = None
        while True:
            try:
                time.sleep(1/3)
                result = self.f(*args)
                return result
            except BaseException:
                # Only 5 attempts
                if t == 5:
                    sys.exit('Something went wrong, '
                             'check your Internet connection and so on')

                log_error_request.debug('Something went wrong, trying for the {} time'
                                   .format(t+1))

                t += 1


@RobustRequest
def basic_request(url, params):
    params = merge_api_vk_params(params)
    response = requests.get(url, params)
    return response


def get_user_friends():
    source_uid = input_user_id
    url = 'https://api.vk.com/method/friends.get'
    params = dict(
        source_uid=source_uid
    )
    response = basic_request(url, params)
    print('User friend list received')
    return response


def get_user_brief_info(user_id):
    """Return id, first_name, last_name, deactivated"""

    url = 'https://api.vk.com/method/users.get'
    params = dict(
        user_ids=user_id
    )
    response = basic_request(url, params)
    return response


def filter_user_live_friend_list():
    """ Return filtered list of friends without deleted and banned user_ids."""
    user_friends = get_user_friends()
    user_friend_list = user_friends.json()['response']['items']
    user_friend_count = user_friends.json()['response']['count']
    user_live_friend_list = []
    i = 0
    print("User's friends filtering process has begun")
    for user_id in user_friend_list:
        print('* Left {} users to process'.format(user_friend_count-i))
        try:
            if (get_user_brief_info(user_id)
                    .json()['response'][0]['deactivated'] is not None):
                i += 1
                continue
        except:
            user_live_friend_list.append(user_id)
        i += 1
    return user_live_friend_list


def get_user_groups():
    source_uid = input_user_id
    url = 'https://api.vk.com/method/groups.get'
    params = dict(
        source_uid=source_uid,
        extended=1,
        fields='members_count'
    )
    response = basic_request(url, params)
    print("User's groups list received")
    return response


def get_group_members(group_id):
    url = 'https://api.vk.com/method/groups.getMembers'
    params = dict(
        group_id=group_id
    )
    response = basic_request(url, params)
    print("Group member list received")
    return response


def is_user_in_group(friend, group):
    url = 'https://api.vk.com/method/groups.isMember'
    params = dict(
        user_ids=friend,
        group_id=group
    )
    response = basic_request(url, params)
    return response


def create_list_of_group():
    """Returns list of groups that specified user belongs to without friends."""

    user_groups_request = get_user_groups()
    user_groups_list = user_groups_request.json()['response']['items']
    user_groups_count = user_groups_request.json()['response']['count']
    friends = str(filter_user_live_friend_list()).strip('[]')

    groups_wout_friends = []
    groups_with_friends = []

    counter_processed_groups = 0
    for group in user_groups_list:

        data_for_json_layout = {
            'id': group['id'],
            'name': group['name'],
            'members_count': group['members_count']
        }

        print('Left {} groups to process'.format(
            user_groups_count - counter_processed_groups))

        counter_member_is_false = 0
        n = 0
        are_users_in_group_status_list = is_user_in_group(friends, group['id'])
        for member in are_users_in_group_status_list.json()['response']:
            if member['member'] != 0:
                n += 1

                if n > input_n_quantity_friends:
                    groups_with_friends.append(data_for_json_layout)
                    break
            else:
                counter_member_is_false += 1

        if counter_member_is_false == len(
                are_users_in_group_status_list.json()['response']):
            print('Added')
            groups_wout_friends.append(data_for_json_layout)
        counter_processed_groups += 1

    return groups_wout_friends, groups_with_friends


def write_to_json(filename, data):

    with open('{}.txt'.format(filename), 'w', encoding='utf-8') as outfile:
        json.dump(data, outfile, ensure_ascii=False)


if __name__ == '__main__':
    input_user_id = input_user_id()
    input_n_quantity_friends = input_n_quantity_friends()
    both_groups = create_list_of_group()
    groups_wout_friends = both_groups[0]
    groups_with_friends = both_groups[1]
    write_to_json('groups_wout_friends', groups_wout_friends)
    write_to_json('groups_with_friends', groups_with_friends)