import datetime
import json
import urllib.request
import sys
import configparser

import constants


def url_builder(city_id: int, user_api: str, unit: str) -> str:
    """
    Build complete API url.
    :param city_id: City ID.
    :param user_api: User API key.
    :param unit: Unit preferred.
    :return:
    """
    api = 'http://api.openweathermap.org/data/2.5/weather?id='
    full_api_url = \
        api + str(city_id) + '&mode=json&units=' + unit + '&APPID=' + user_api
    return full_api_url


def data_fetch(full_api_url: str) -> dict:
    """
    Fetch data from API server.
    :param full_api_url: Full api url.
    :return: Unorganized dict data.
    """
    with urllib.request.urlopen(full_api_url) as url:
        output = url.read().decode('utf-8')
        raw_api_dict = json.loads(output)
    return raw_api_dict


def data_organizer(raw_data: dict) -> dict:
    """
    Take unorganized dict data and produce an organized dict data.
    :param raw_data: Unorganized dict.
    :return: Organized dict.
    """
    main = raw_data.get('main')
    sys = raw_data.get('sys')
    data = dict(
        city=raw_data.get('name'),
        country=sys.get('country'),
        temp=main.get('temp'),
        temp_max=main.get('temp_max'),
        temp_min=main.get('temp_min'),
        humidity=main.get('humidity'),
        pressure=main.get('pressure'),
        sky=raw_data['weather'][0]['main'],
        sunrise=time_converter(sys.get('sunrise')),
        sunset=time_converter(sys.get('sunset')),
        wind=raw_data.get('wind').get('speed'),
        wind_deg=raw_data.get('deg'),
        dt=time_converter(raw_data.get('dt')),
        cloudiness=raw_data.get('clouds').get('all')
    )
    return data


def time_converter(time: int) -> str:
    """
    Convert time from server format (unix timestamp), to readable human format.
    :param time: server unix timestamp.
    :return: readable human time format.
    """
    converted_time = datetime.datetime.fromtimestamp(
        int(time)
    ).strftime('%I:%M %p')
    return converted_time


def send_collected_data_to_display(
        city_id=constants.OpenWeatherMap.ahmedabad_city_id,
        user_api=constants.OpenWeatherMap.api_key,
        prefer_unit="metric"
):
    """
    Send final result collected data from open weather map based on your configuration file, to display function.
    :param city_id: your city id.
    :param user_api: your api key.
    :param prefer_unit: metric or imperial.
    """
    setting = url_builder(city_id=city_id,
                          user_api=user_api,
                          unit=prefer_unit)
    raw_data = data_fetch(setting)
    data = data_organizer(raw_data)
    # display(data)
    return data


def display(data: dict):
    """
    Displaying weather data in terminal.
    :param data: dictionary.
    """
    m_symbol = '\xb0' + 'C'
    print('---------------------------------------')
    print('Current weather in: {}, {}:'.format(data['city'], data['country']))
    print(data['temp'], m_symbol, data['sky'])
    print('Max: {}, Min: {}'.format(data['temp_max'], data['temp_min']))
    print('')
    print('Wind Speed: {}, Degree: {}'.format(data['wind'], data['wind_deg']))
    print('Humidity: {}'.format(data['humidity']))
    print('Cloud: {}'.format(data['cloudiness']))
    print('Pressure: {}'.format(data['pressure']))
    print('Sunrise at: {}'.format(data['sunrise']))
    print('Sunset at: {}'.format(data['sunset']))
    print('')
    print('Last update from the server: {}'.format(data['dt']))
    print('---------------------------------------')


def save_config():
    """
    Save input setting (City ID, User API, and Preferred unit) into a configuration file.
    :return:
    """

    print('City ID: ')
    city_id = input()
    print('User API: ')
    user_api = input()
    print('Prefer Unit: metric, imperial, or kelvin')
    prefer_unit = input()

    config = configparser.ConfigParser()
    config['DEFAULT'] = {'city_id': city_id,
                         'user_api': user_api,
                         'prefer_unit': prefer_unit}

    with open('weather_config.ini', 'w') as configfile:
        config.write(configfile)


def load_config():
    """
    Load setting from configuration file.
    """
    try:
        config = configparser.ConfigParser()
        config.read('weather_config.ini')
        city_id = config.get('DEFAULT', 'city_id')
        user_api = config.get('DEFAULT', 'user_api')
        prefer_unit = config.get('DEFAULT', 'prefer_unit')

        send_collected_data_to_display(city_id, user_api, prefer_unit)

    except AttributeError as missing_data:
        print('Missing city_id or prefer_unit in config file!', missing_data)

    except urllib.error.HTTPError as apiError:
        print('Error: Missing or Unauthorized API!', apiError)

    except IOError as e:
        print('Error: No internet! ', e)

    except configparser.NoOptionError as fi:
        print('''Error:
        Configuration file \'weather_config.ini\' is missing or corrupted!
        \nTo fix it, run:
        python3 weather.py --config, to enter your configuration.
        ''' '''\nMore Details:
        ''', fi)


def argv():
    """
    Catch args from the terminal, by manual way to.
    """
    args = sys.argv
    args.pop(0)
    if len(args) != 0:
        if args[0] == '--config':
            save_config()
        elif args[0] == '--help':
            print(__doc__)
            exit(0)
        else:
            print("Unknown Command, available command: --help and --config")
            exit(0)

