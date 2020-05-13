from fdfs_client.client import Fdfs_client, get_tracker_conf

if __name__ == '__main__':
    con_file = get_tracker_conf('./client.conf')
    client = Fdfs_client(con_file)
    ret = client.upload_by_filename('./1.jpg')
    print(ret)
    pass


