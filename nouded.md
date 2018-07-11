# Rakenduse nõuded

Rakenduse kasutamise eeldused:

* Võrgukommutaatoris töötab ja on seadistatud SNMP
* Võrgukommutaator jagab üle SNMP LLDP/CDP infot

---

Rakenduse nõuded:

1. Rakenduse käivitamine toimub käsurealt, vajalik python (koos vähemalt ühe SNMP teegiga) ja SNMP
2. Rakenduse sisendiks on ühe või mitme võrgukommutaatori aadress ja seadmetes seadistatud SNMP kommuuni nimi
3. Kui antakse ette mitu seadet, on võimalus määrata erinevatele seadmetele erinevad SNMP kommuunide nimed

4. Rakendus küsib igalt sisendiks saadud seadmelt LLDP/CDP andmed (nimi, ip, mac; ühenduste füüsiline port, nimi, ip, mac)
5. Kui seadmega on ühendatud veel kommutaatoreid, küsitakse ka neilt andmed
6. Rakendus töötleb ja vormindab saadud andmed
7. Tekkinud vead kuvatakse kasutajale mõistlikult (mis juhtus, mida teha)

8. Rakendus loob antud andmete põhjal staatilise veebilehe (.html), kus kuvatakse graaf võrgukommutaatorite kohta
9. Staatilise veebilehe vaatamiseks pole vaja internetiühendust (CSS ja JS lokaalsed)
10. Graafi tipud on võrgukommutaatorid
11. ? Graafi väiksemad (vähem silmapaistvavad) tipud on võrgukommutaatoritesse ühendatud seadmed (mis pole kommutaatorid)
12. Graafi servad tippude vahel on võrgukommutaatorite ühendused
13. Graafis on vaikimisi paigutus mõistlik, see tähendab, et tipud ei kattu ja kui tekib mitu graafi, kuvatakse need üksteisest pisut eemal

14. Graafis on võimalik seadmeid enda suva järgi lohistada
15. Graafis kuvatakse tippudes seadme nimi (aadress), aga peale vajutades on võimalik näha ka ülejäänud infot (ip, mac, port)
16. Kasutaja graafile tehtud muudatused salvestatakse kasutaja brauseriga lokaalselt (küpsised või localstorage) ja taastatakse järgmisel avamisel
