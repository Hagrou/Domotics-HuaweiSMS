******************************************************************************************
Comment envoyer des sms via un dongle Huawei qui ne veut pas se mapper sur un device USB ?
******************************************************************************************

Petit article décrivant une solution transverse à l'envoie de sms dans un cadre "domoticz".

Utilisateur de Domoticz depuis 2 ou 3 ans, je complète petit à petit mon installation. Le
dernier ajout concerne l'utilisation des sms pour me prévenir d'évènements dans la maison.


1ere idée, passer par un site web d'envoie de sms
--------------------------------------------------

La première solution que j'ai utilisé a consisté à utiliser un service web permettant
d'envoyer des sms directement depuis Domoticz (ou autres) en appelant une simple url https.
Disposant d'un abonnement à free, j'ai commandé une sim gratuite et activé le service sms
qui permet de "s'auto envoyé" un sms.

Une fois le service activé, il suffit d'utiliser une url reprenant l'identificant et le mot
de passe donné par free pour s'envoyer un sms :

        https://smsapi.free-mobile.fr/sendmsg?user=000000pass=xxxxxxxxx&msg=Hello%20World%20!

Il suffit ensuite de placer la sim de free dans son téléphone pour recevoir les sms.

De nombreux blogs présentes cette solution comme : la, ici et la

A priori cette solution est parfaite. Simple, d'un cout nul (ou 2€/mois si vous n'avez pas de
box free), elle repond bien au besoin. Mais après un an d'usage je suis revenu sur cette solution :

- il faut tout d'abord un téléphone avec une double carte Sim. Mais utilisateur de l'application
  signal, celle-ci n'arretait pas de changer de sim pour envoyer mes messages, ce qui ne manqua pas
  de provoquer quelques incompréhension dans mon entourage...

- plus sérieusement, le service web n'envoie pas forcement immediatement les messages. Il m'est arrivé
  de recevoir des sms de domoticz plusieurs heures après leurs émissions (dommage pour une alarme passive).

- enfin l'ordre des messages n'est pas garanti, ce qui peut être problématique pour certaines applications
  (la porte de garage est ouverte ou fermée !?)

2eme idée, utiliser un dongle 3G
--------------------------------

Pour réduire la latence d'envoie de sms, j'ai décidé d'utiliser un dongle 3G que je connecte directement
au raspberry supportant Domoticz. La solution est déjà éprouvée par de nombreuses personnes et semble simple
à mettre en oeuvre... quand on arrive à faire reconnaitre correctement le dongle comme un device USB.

Mais malheureusement, il semble que la facilité d'intégrer un dongle 3G sous linux depend beaucoup de la
version du firmware de celui-ci :

Une fois installé, on recherche le device qui lui est associé :

    $ sudo lsusb -v | grep 'idVendor\|idProduct\|iProduct\|iSerial'

On retrouve bien le dongle ainsi que mon module de réception radio RFX 433Mhz :


    - le dongle USB Huawei
             idVendor           0x12d1 Huawei Technologies Co., Ltd.

             idProduct          0x14dc E33372 LTE/UMTS/GSM HiLink Modem/Networkcard

             iProduct                2 HUAWEI Mobile

             iSerial                 0

    - le RFXtrx433
             idVendor           0x0403 Future Technology Devices International, Ltd

             idProduct          0x6001 FT232 Serial (UART) IC

             iProduct                2 RFXtrx433

             iSerial                 3 A1QEL7T


Le soucis des dongles Huawei est :

- ils sont considérés comme des clés USB de stockage par le système
- les numéros de devices d'association des périphériques USB peut changer en fonction de l'ordre de chargement des drivers au boot. Il faut donc créer un device "nommé" qui sera associés aux idProduct de chaque périphérique usb.

ce qui se fait avec les opérations suivantes :

Clé 3G considérée comme stockage...
===================================

1) Ajouter la ligne suivante dans le fichier

    $ sudo emacs /lib/udev/rules.d/40-usb_modeswitch.rules
 
    # Huawei E33372 Modem
    ATTRS{idVendor}=="12d1", ATTRS{idProduct}=="14dc", RUN+="usb_modeswitch '/%k'"

2) Ajouter à la fin du fichier /etc/usb_modeswitch.conf

    # Huawei E33372 (3.se) and others                                                                   
    TargetVendor=0x12d1
    TargetProductList="14db,14dc"
    HuaweiNewMode=1
    NoDriverLoading=1


Affectation permanente des ports usb
====================================

Créer un fichier de règle avec le contenu suivant:

    $ sudo nano /etc/udev/rules.d/99-usb-serial.rules

    SUBSYSTEM=="tty", ATTRS{idVendor}=="0403", ATTRS{idProduct}=="6001",    ATTRS{serial}=="A1QEL7T", SYMLINK+="ttyUSB-RFX433-A"
    SUBSYSTEM=="tty", ATTRS{idVendor}=="12d1", ATTRS{idProduct}=="14dc", SYMLINK+="ttyUSB-GSM"

La commande suivante permet de prendre en compte le fichier:

    $ sudo udevadm control --reload

Normalement 2 nouveaux devices usb apparaissent :

    ttyUSB-RFX433-A

    ttyUSB-GSM  (non présent !?)

En fait après quelques heures d'essais infructueux, je n'ai jamais réussi à faire reconnaitre
le dongle correctement par mon linux !? Pourtant d'autre y sont arrivés, comme par exemple ici##.
Il semble que cela fonctione pour certaines clés mais pas forcement toutes ? On peut trouver sur le net
des listes de références de dongles qui fonctionnent... malheureusement il s'agit souvent de vieux produits
qui ne sont plus en vente.

Au final, j'ai essayé mon dongle sur un windows en me disant qu'avec les bons drivers, le système allait s'en sortir..
mais non, même windows n'arrive pas a se dépétrer de ce firmware :/

Control du dongle via son interface réseau
------------------------------------------

Par contre, que ce soit depuis Windows ou Linux, l'ajout du dongle créer automatiquement un nouvelle
interface réseau, sur laquelle on peut trouver un serveur web permettant de configurer quelques paramètres
de la clé et envoyer / recevoir des sms.

::

  $ ip addr
  ...
  2: eth0: <BROADCAST,MULTICAST,UP,LOWER_UP> mtu 1500 qdisc pfifo_fast state UP group default qlen 1000
    link/ether b8:27:eb:8e:33:26 brd ff:ff:ff:ff:ff:ff
    inet 192.168.1.41/24 brd 192.168.1.255 scope global noprefixroute eth0
       valid_lft forever preferred_lft forever
    inet6 2a01:cb08:8c7e:2400:4258:f10b:d89b:83fc/64 scope global dynamic mngtmpaddr noprefixroute
       valid_lft 1756sec preferred_lft 556sec
    inet6 fe80::c4b4:a453:627f:b489/64 scope link 
       valid_lft forever preferred_lft forever
  ...
  4: eth1: <BROADCAST,MULTICAST,UP,LOWER_UP> mtu 1500 qdisc pfifo_fast state UP group default qlen 1000
    link/ether 00:1e:10:1f:00:00 brd ff:ff:ff:ff:ff:ff
    inet 192.168.8.100/24 brd 192.168.8.255 scope global noprefixroute eth1
       valid_lft forever preferred_lft forever
    inet6 fe80::2ca1:8e5f:6bec:dd8b/64 scope link 
    valid_lft forever preferred_lft forever

On peut ainsi accéder au serveur web présent sur la clé à l'adresse: http://192.168.8.1

Utilisation d'une API WEB ?
===========================

Aussi j'ai décidé de regarder du côté de l'interface web... Puisqu'il est possible d'envoyer et de lire des
sms depuis cette interface, il doit bien y avoir une api 'web' permettant de contrôler la clé ?
Aussi j'ai commencé a regarder les échanges de paquets http entre mon browser et le donc. Et puis... je me
suis dit qu'il y avait forcément quelqu'un qui avait du y penser avant moi... et après une petite recherche
je suis tombé sur le projet `huawei-lte-api <https://pypi.org/project/huawei-lte-api/>` :

::

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


L'installation est triviale, il suffit d'importer via pip3 le bon module python :

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

Projet SMS Box
==============

Du coup je suis parti de cette API pour enfin réussir à contrôler mon dongle Huawei et pouvoir m'envoyer des
notifications par Sms. Pour cela, j'ai développé un peu de code en python (cf ###). Ce projet contient essentiellement
un fichier SmsBox.py qui définit :

- une classe SmsBox
- un programme principal permettant d'envoyer et recevoir des sms depuis une ligne de commande (pour l'intégration dans domoticz).

Ainsi l'envoie d'un sms peut se faire par la commande suivante :

    $ python3 SmsBox.py send +33065643446 "Hello!"

Afin d'avoir une idée de l'ordre des messages, chaque message reçu contient la date et l'heure d'émission du message.
De même, pour éviter de saturer la boite d'émission, les sms envoyés sont effacés des boites "Draft" et "Sent".









APN
====

https://lecrabeinfo.net/installer-configurer-mini-box-4g-lte-tp-link-tl-wr902ac-huawei-e3372.html


https://github.com/rishavanand/huawei-e355-sms-api

https://support.huaweicloud.com/intl/en-us/api-msgsms/sms_05_0001.html

https://pypi.org/project/huawei-lte-api/

Problème de route
#################

L'ajout du dongle a eu un effet que je n'avais pas anticipé... Mon domoticz n'arrive plus a sortir sur le web... 


Un accès web à google passe maintenant par le dongle... ce qui n'est pas souhaitable vue que je n'ai pas de forfait data...

::

    $ wget www.google.com
    --2020-06-15 10:59:49--  http://www.google.com/
    Résolution de www.google.com (www.google.com)… 192.168.8.1
    Connexion à www.google.com (www.google.com)|192.168.8.1|:80… connecté.
    requête HTTP transmise, en attente de la réponse… 307 Temporary Redirect
    Emplacement : http://192.168.8.1/html/index.html?url=www.google.com [suivant]
    --2020-06-15 11:00:04--  http://192.168.8.1/html/index.html?url=www.google.com
    Connexion à 192.168.8.1:80… connecté.


si l'on regarde les routes, on peut voir qu'il y a maintenant 2 chemins pour sortir du réseau local : eth1 et wlan0

::

    $ route -n
    Table de routage IP du noyau
    Destination     Passerelle      Genmask         Indic Metric Ref    Use Iface
    0.0.0.0         192.168.8.1     0.0.0.0         UG    204    0        0 eth1
    0.0.0.0         192.168.1.1     0.0.0.0         UG    303    0        0 wlan0
    192.168.1.0     0.0.0.0         255.255.255.0   U     303    0        0 wlan0
    192.168.8.0     0.0.0.0         255.255.255.0   U     204    0        0 eth1


du coup il faut penser à supprimer la default gateway 192.168.8.1 puis rajouter la bonne

::

    $ sudo ip route flush 0/0
    $ sudo ip route add default via 192.168.1.1

Mes besoins pour domotics
#########################

Mes besoins sont simples :

- Je dois pouvoir envoyer des sms depuis domoticz

- Eventuellement, je dois pouvoir envoyer des commandes sms à mon Domoticz afin d'exécuter des opérations (reboot du
  domoticz par exemple, ouverture du forward de port, etc.)





