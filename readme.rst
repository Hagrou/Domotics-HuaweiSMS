******************************************************************************************
Comment envoyer des sms via un dongle Huawei qui ne veut pas se mapper sur un device USB ?
******************************************************************************************

Ca ne marche pas !
##################


Aussi j'ai décidé de regarder du côté de l'interface web... Puisqu'il est possible d'envoyer et de
lire des sms depuis cette interface, il doit bien y avoir une api 'web' permettant de contrôler la clé ?

Effectivement, après un peu de lecture du code du portail, je me suis dit qu'il y avait forcément quelqu'un
qui avait du y penser... et après une petite recherche je suis tombé sur le projet
`huawei-lte-api <https://pypi.org/project/huawei-lte-api/>`::



    huawei-lte-api
    API For huawei LAN/WAN LTE Modems, you can use this to simply send SMS,
    get information about your internet usage, signal, and tons of other stuff

    Tested on:

        Huawei B310s-22
        Huawei B315s-22
        Huawei B525s-23a
        Huawei B525s-65a
        Huawei B715s-23c
        Huawei E3131
        Huawei E5186s-22a
        Huawei B528s
        Huawei E3531
        (probably will work for other Huawei LTE devices too)

    Will NOT work on:

        Huawei B2368-22 (Incompatible firmware, testing device needed!)

    PS: it is funny how many stuff you can request from modem/router without any authentication

    ...
    Donations 250 CZK (9,79 EUR) for B535-232 fund, thx @larsvinc !

L'installation est triviale, il suffit d'importer via pip3 le bon module python::

     $ pip install huawei-lte-api
     Collecting huawei-lte-api
     Downloading https://files.pythonhosted.org/packages/ce/79/32f352155ce8a047997ac124a9185fd9f02239f6c54f12fa49498c6ca1ac/huawei-lte-api-1.4.11.tar.gz
     Collecting requests (from huawei-lte-api)
     ...
     Successfully installed certifi-2020.4.5.1 chardet-3.0.4 dicttoxml-1.7.4 huawei-lte-api-1.4.11 idna-2.9 requests-2.23.0 urllib3-1.25.9 xmltodict-0.12.0

On a ensuite un code d'exemple qui fait l'essentiel::

    from huawei_lte_api.Client import Client
    from huawei_lte_api.AuthorizedConnection import AuthorizedConnection
    from huawei_lte_api.Connection import Connection

    # connection = Connection('http://192.168.8.1/') For limited access, I have valid credentials no need for limited access
    # connection = AuthorizedConnection('http://admin:MY_SUPER_TRUPER_PASSWORD@192.168.8.1/', login_on_demand=True) # If you wish to login on demand (when call requires authorization), pass login_on_demand=True
    connection = AuthorizedConnection('http://admin:MY_SUPER_TRUPER_PASSWORD@192.168.8.1/')

    client = Client(connection) # This just simplifies access to separate API groups, you can use device = Device(connection) if you want

    print(client.device.signal())  # Can be accessed without authorization
    print(client.device.information())  # Needs valid authorization, will throw exception if invalid credentials are passed in URL


    # For more API calls just look on code in the huawei_lte_api/api folder, there is no separate DOC yet

    Result dict

    {'DeviceName': 'B310s-22', 'SerialNumber': 'MY_SERIAL_NUMBER', 'Imei': 'MY_IMEI', 'Imsi': 'MY_IMSI', 'Iccid': 'MY_ICCID', 'Msisdn': None, 'HardwareVersion': 'WL1B310FM03', 'SoftwareVersion': '21.311.06.03.55', 'WebUIVersion': '17.100.09.00.03', 'MacAddress1': 'EHM:MY:MAC', 'MacAddress2': None, 'ProductFamily': 'LTE', 'Classify': 'cpe', 'supportmode': None, 'workmode': 'LTE'}

Du coup je vais partir de cette API pour enfin réussir à contrôler mon dongle Huawei et pouvoir m'envoyer des
notifications par Sms.

Mes besoins pour domotics
#########################

Mes besoins sont simples :

- Je dois pouvoir envoyer des sms depuis domoticz

- Eventuellement, je dois pouvoir envoyer des commandes sms à mon Domoticz afin d'exécuter des opérations (reboot du
  domoticz par exemple, ouverture du forward de port, etc.)





