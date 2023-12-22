from datetime import datetime, timedelta, date

def get_today_or_tomorrow(date_str):
    madate = date(int(date_str[0:4]), int( date_str[5:7]), int(date_str[-2:]))
    today = datetime.now().date()
    tomorrow = today + timedelta(days=1)
    
    if madate == today:
        return "Aujourd'hui"
    elif madate == tomorrow:
        return "Demain"
    else:
        listejours = ['Lundi', 'Mardi', 'Mercredi', 'Jeudi', 'Vendredi', 'Samedi', 'Dimanche']
        listemois = ['Janvier', 'Février', 'Mars', 'Avril', 'Mai', 'Juin', 'Juillet', 'Août', 'Septembre', 'Octobre', 'Novembre', 'Décembre']
        return "%s %s %s" % (listejours[madate.weekday()], madate.day, listemois[madate.month])

