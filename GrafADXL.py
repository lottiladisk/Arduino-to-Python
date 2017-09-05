
import socket
import matplotlib.pyplot as plt
import numpy as np
import time

def Povezava(port_num = 5021):
    """
    Return server socket connection through selected port.
    / Vrne vzpostavitev socket server povezave.

    Parameters
    -------------
    port_num: number of the port. Default is 5021. Must be non-negative.
    / port_num: Številka vhodnih vrat. Privzeta so vrata 5021.
    Zahteva pozitivno Število.

    Returns
    -------------
    connection and address number.

    """

    serversocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    serversocket.bind((' ', port_num))
    serversocket.listen(5)
    connection, address = serversocket.accept()

    return connection, address


def Meritve(tk=10000000):
    """"
    Returns generates data in form of strings and plots the to a graph.
    The execution of the plot delays the receiving of next data packet.
    /Funkcija generira podatke v obliki nizov in jih za tem zelo hitro izriše.
    Gre za slab približek izrisovanja v
    realnem času, saj izvedba izrisa zakasni prejetje naslednjega paketa podatkov.

    Parameters
    ---------------
    tk: time of the measurement [us]
    /tk: Čas, ki ga popisuje meritev [us]
    dt: time between readings. Equals to "delta_t" in Arduino IDE. [us]
    /dt: Čas med podatki, ustreza vrednosti "delta_t" v Arduinu IDE. [us]
    stp: number of readings in a packet.
    /stp: Število podatkov v paketu.
    """


    conn, add = Povezava()

    dt = 50000                                                                                                          #Načeloma bi tukaj prišla komun. Pyt - Ard
    stp = 19
    i = 1                                                                                                               #Števec paketov
    t = np.array([], dtype=int)                                                                                         #Prazen numerični seznam časov
    a = np.array([], dtype=int)                                                                                         #Prazen numerični seznam pospeškov

    fig, ax = plt.subplots()                                                                                            #Nov izris
    os, = ax.plot(np.linspace(0, stp * dt/1000000, stp),
                  np.random.randint(100, 140, stp))                              #Začetno stanje
    ax.set_ylim([0,150])

    while i <= 1+ tk / (dt * stp):                                                                                       #Prejemanje paketov

        paket = ""                                                                                                      #Prazen paket
        buf = conn.recv(4096)
        if len(buf) > 0:                                                                                                #Se izpolni, ce paket ni prazen
            paket = buf.decode()

        tocke = paket.split("\n")                                                                                       #Ločevanje točk
        for tocka in tocke:                                                                                             #Ločevanje pospeška in časa
            if len(tocka) > 1:
                y, x = tocka.split('\t')
                t = np.append(t, float(x)/1000000)                                                                      #Pripenjanje časov v skupno tabelo
                a = np.append(a, int(y))                                                                                #Pripenjanje pospeškov v skupno tabelo

        os.set_data((t[(i-1)*stp:(i-1)*stp+stp]-t[0]),
                    a[(i - 1) * stp:(i-1) * stp + stp])                                                     #Osveževanje grafa
        ax.set_xlim((t[(i-1)*stp]-t[0]),(t[(i-1)*stp+stp]-t[0]))                                                        #Meje x osi
        plt.pause(0.001)

        i += 1


        #Inkrement števca paketov