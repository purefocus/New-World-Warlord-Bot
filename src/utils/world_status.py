import requests

def get_status():
    sess = requests.Session()
    sess.cookies.set('com_nws_persist__favoriteWorlds', '["Ohonoo"]')
    sess.cookies.set('com_nws_persist__favouriteWorldsOnly', 'true')
    result = sess.get('https://newworldstatus.com/regions/us-east')
    print(result.content)

if __name__ == '__main__':
    get_status()
