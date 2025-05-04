from collections import Counter, defaultdict
import matplotlib.pyplot as plt

# 1. Vlož text sem jako vícenásobný řetězec
raw_data = """
germany_chat,access_unit
tech_support,uk_chat
intercom,slovakia_chat,tp_audio,f_nfc,access_unit
intercom,tech_support,poland_chat
intercom,cz_chat
netherlands_chat,tech_support,intercom,tp_audio
tech_support,cz_chat,licencing
netherlands_chat
intercom,access_unit,uk_chat
tech_support,lift,licencing,germany_chat
nordic_chat,tech_support,sweden_chat,indoor_station
cz_chat
tp_audio,m_dimensions,uk_chat,licencing,tech_support
suspect_created,france_chat,f_video,s_home,intercom,ter,licencing
intercom,hungary_chat
germany_chat,tech_support,f_sip
petr,suspect_created,cz_chat
compatibility,intercom,tp_camera,cz_chat,order_number,m_dimensions
intercom,spain_chat,m_dimensions
indoor_station,luxembourg_chat,tech_support
poland_chat
intercom,tech_support,spain_chat
f_sip,middle_east_chat,cyprus_chat,compatibility,intercom
middle_east_chat,software,uae_chat,price
intercom,netherlands_chat
cz_chat
germany_chat
tech_support,france_chat
germany_chat
f_nfc,intercom,germany_chat
italy_chat
uk_chat,tech_support
d_datasheet,italy_chat,intercom,tp_audio
suspect_created,italy_chat,price,petr
italy_chat,intercom
tech_support,switzerland_chat,indoor_station
tp_power_supply,suspect_created,f_video,cz_chat,petr,f_sip
netherlands_chat,licencing,software
france_chat,licencing
indoor_station,uk_chat,tp_power_supply
software,uk_chat,intercom
tech_support,belgium_chat
f_nfc,intercom,slovakia_chat
f_sip,m_dimensions,d_manual,compatibility,germany_chat,f_teams,audio
tp_power_supply,compatibility,f_video,france_chat,f_sip
cz_chat,tech_support
italy_chat,f_video,intercom
audio,tp_colour,f_video,italy_chat,s_hospitality,compatibility,tp_camera,intercom,m_dimensions
switzerland_chat,intercom
italy_chat
africa_chat,angola_chat,software
austria_chat
f_teams,belgium_chat,intercom
germany_chat
tp_audio,cz_chat,intercom,f_bluetooth
sweden_chat,nordic_chat,tech_support,compatibility,s_residential
france_chat,tech_support
compatibility,switzerland_chat,m_dimensions,tech_support
tech_support,india_chat,apac_chat
africa_chat,angola_chat,software
s_residential,m_dimensions,uk_chat,d_manual,intercom
belgium_chat,intercom
france_chat
france_chat
france_chat
tech_support,tp_power_supply,f_sip,intercom,austria_chat
lift,d_datasheet,germany_chat
italy_chat,contact_updated,price,lead,f_video
intercom,tech_support,italy_chat,f_cloud
hungary_chat
suspect_created,intercom,f_nfc,bahrain_chat,indoor_station,middle_east_chat,f_onvif,s_residential,software,f_video,high,lead,s_home
poland_chat
intercom,sweden_chat,nordic_chat
switzerland_chat,indoor_station,f_video
cz_chat,intercom
middle_east_chat,kuwait_chat
s_residential,cz_chat,intercom
cz_chat,tech_support
denmark_chat,nordic_chat
intercom,uk_chat
intercom,contact_updated,tp_power_supply,indoor_station,nordic_chat,latvia_chat,f_video,lead
italy_chat,intercom
italy_chat
suspect_created,s_residential,lead,cz_chat,high,d_other
software,italy_chat,tp_audio
singapore_chat,compatibility,f_teams,tp_camera,apac_chat,f_video
intercom,italy_chat,f_video,software
intercom,tech_support,netherlands_chat
suspect_created,intercom,belgium_chat,lead
d_datasheet,belgium_chat,d_other,f_video
f_video,romania_chat,indoor_station,intercom,balkan_chat,compatibility
f_bluetooth,italy_chat
tech_support,lift
intercom,tech_support,cz_chat,s_hospital
intercom,tp_power_supply,cz_chat
indoor_station,f_video,austria_chat
software,germany_chat
tp_power_supply,cz_chat
f_bluetooth,software,tech_support,austria_chat
spain_chat
s_hospitality,spain_chat,price
spain_chat,s_hospitality,price
intercom,spain_chat
austria_chat,tech_support,tp_power_supply,intercom
suspect_created,tp_power_supply,portugal_chat,ter,compatibility
software,luxembourg_chat,licencing,f_video
tech_support,tp_camera,italy_chat,m_dimensions
italy_chat
cz_chat,tech_support
italy_chat,tech_support
austria_chat,tp_audio,intercom,tp_camera,f_video
tech_support,f_bluetooth,intercom,germany_chat
intercom,tech_support,belgium_chat
d_other,m_dimensions,italy_chat,tech_support
italy_chat
italy_chat
indoor_station,f_teams,lead,compatibility,d_other,f_video,uk_chat,suspect_created,f_sip
cz_chat
suspect_created,lead,uk_chat
nordic_chat,d_manual,m_dimensions,tech_support,intercom,sweden_chat
cz_chat
tech_support,austria_chat,m_dimensions,d_manual
f_video,d_manual,f_cloud,germany_chat
kuwait_chat,f_video,price,middle_east_chat
germany_chat,tech_support
access_unit,germany_chat,software
licencing,belgium_chat,lead,suspect_created
germany_chat,d_other,lift,tech_support
uae_chat,middle_east_chat
"""

# Kategorie podle prefixu
prefix_mapping = {
    'f': 'Function',
    'd': 'Documents',
    'tp': 'Technical parameters',
    's': 'Solution',
    'm': 'Mechanical paramaters',
    'general': 'Request'
}

# Rozdělení do kategorií
categorized = defaultdict(list)
excluded_tags = {'lead', 'lead_h', 'None', 'ter', 'high', 'suspect_created', 'contact_updated', 'petr', 'contact_updated'}

for line in raw_data.strip().split('\n'):
    tags = [tag.strip() for tag in line.split(',') if tag.strip() and not tag.endswith('_chat')]
    for tag in tags:
        if tag in excluded_tags:
            continue  # ← přeskočí nežádoucí tag
        if '_' in tag:
            prefix = tag.split('_')[0]
        else:
            prefix = 'general'

        category = prefix_mapping.get(prefix, 'Request')
        categorized[category].append(tag)

# Vykresli grafy pro každou kategorii
for category, tag_list in categorized.items():
    counter = Counter(tag_list)

    if counter:
        tags, counts = zip(*counter.most_common())
        plt.figure(figsize=(max(10, len(tags) * 0.6), 5))  # dynamická velikost podle počtu tagů
        plt.bar(tags, counts, color='teal')

        # Přidání hodnot nad sloupce
        for i, (tag, count) in enumerate(zip(tags, counts)):
            plt.text(i, count + 0.5, str(count), ha='center', va='bottom', fontsize=9)

        plt.xticks(rotation=45, ha='right')
        plt.title(f'Count – {category}')
        plt.ylabel('Count')
        plt.tight_layout()
        plt.show()
