                                                Fonctionnement de l'application Snmp_Ipmi                                                         



L'application permet de récupérer des informations sur le système ou sur le serveur, grâce à l'utilisation du protocole SNMP par le biais des OIDS, ou grâce à l'utilisation du protocole IPMI par le biais des capteurs.

L'utilisateur de l'application peut rechercher la valeur d'un ou de plusieurs OIDS spécifiques, ainsi que des capteurs IPMI, en inscrivant leur id dans le fichier de configuration (conf.json).

La valeur des paramètres recherchés, est ensuite envoyée dans une API réalisée en php (apiSnmpIpmi.php), qui va les enregistrer dans une base de donnée.



Etape 1 : Modification des champs SNMP du fichier de configuration "conf.json"

    Dans le dictionnaire "SNMP", l'utilisateur doit remplacer les valeurs par l'ip de son serveur, le port SNMP du serveur, la communauté SNMP, 
    et  dans les champs "metrics" il peut modifier les OIDS dont il souhaiterait connaître et enregistrer les valeurs.
    Il peut choisir d'ajouter plusieurs serveurs, ou plusieurs oids, il serait néanmoins préférable de renommer les variables "srv1"/"srv2", 
    correspondantes aux noms du ou des serveurs et de renommer les variables "metric1"/"metric2", correspondantes aux noms du ou des OIDS.

    Exemple :           
                "SNMP": {
                    "srv1": {
                        "ip": "xxx.xxx.xxx.xx",
                        "port" : "161",
                        "communaute" : "changeme",
                        "metrics" : {
                            "metric1": "1.3.6.1.2.1.1.5.0",
                            "metric2": "1.3.6.1.2.1.1.1.0"
                    }
                },

                "SNMP": {
                    "nouveauServeur": {
                        "ip": "255.255.255.14",
                        "port" : "22",
                        "communaute" : "nouvelleCommunaute14",
                        "metrics" : {
                            "interfaces": "1.3.6.1.2.1.2 ",
                            "sysDescr": "1.3.6.1.2.1.1.1.0"
                    }
                },

    Il n'est pas obligatoire de renseigner les champs des deux dictionnaires si l'utilisateur ne souhaite utiliser que l'IPMI.


Etape 2 : Modification des champs IPMI du fichier de configuration "conf.json"

    Dans le dictionnaire "IPMI", l'utilisateur doit remplacer les valeurs par l'ip de son serveur, le nom d'utilisateur ayant accès à l'IPMI et son
    mot de passe, et  dans les champs "metrics" il peut modifier les capteurs/metrics dont il souhaiterait connaître et enregistrer les valeurs.
    Il peut choisir d'ajouter plusieurs serveurs, ou plusieurs capteurs/metrics, il serait néanmoins préférable de renommer la variable "srv1"
    correspondant au nom du ou des serveurs et de renommer les variables "metric1"/"metric2"/"metric3"/"metric4", correspondantes aux noms du ou
    des capteurs.

    Exemple :
                "IPMI": {
                    "srv1": {
                        "ip": "xx.xxx.xxx.x",
                        "user": "changeme",
                        "password": "changeme",
                        "metrics": {
                            "metric1": "Watts",
                            "metric2": "Inlet Ambient",
                            "metric3": "CPU 1",
                            "metric4": "Battery Zone"
                        }
                    }
                }

                "IPMI": {
                    "nouveauServeur": {
                        "ip": "255.255.255.14",
                        "user": "samsam28",
                        "password": "Password",
                        "metrics": {
                            "metric1": "T_AMB_FRONT",
                            "metric2": "Inlet Ambient",
                            "metric3": "Hostpower",
                            "metric4": "Battery Zone"
                        }
                    }
                }


Etape 3 : Lancement de l'application
