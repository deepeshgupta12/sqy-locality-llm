import re
from typing import List, Dict, Any

def slugify(s: str) -> str:
    s = s.lower()
    s = re.sub(r'[^a-z0-9]+', '-', s)
    s = re.sub(r'-{2,}', '-', s).strip('-')
    return s

def build_breadcrumbs_html(trail: List[str], slug: str) -> str:
    parts = ["<nav aria-label='Breadcrumb'><ol>"]
    base_city = slug.split('/')[0] if '/' in slug else slug
    url_city = f"/{slugify(base_city)}"
    if trail:
        parts.append(f"<li><a href='{url_city}'>{trail[0]}</a></li>")
        if len(trail) == 3:
            micro = slugify(trail[1])
            parts.append(f"<li><a href='{url_city}/{micro}'>{trail[1]}</a></li>")
        parts.append(f"<li aria-current='page'>{trail[-1]}</li>")
    parts.append("</ol></nav>")
    return "".join(parts)

def build_schema_graph(locality: Dict[str, Any], faqs: List[Dict[str, str]]) -> Dict[str, Any]:
    place = locality.get("schema_place", {})
    canonical = f"https://www.squareyards.com/locality/{locality['slug']}"

    # Breadcrumb
    items = []
    city = locality["breadcrumb_trail"][0] if locality.get("breadcrumb_trail") else locality["city_name"]
    city_url = f"https://www.squareyards.com/{slugify(city)}"
    pos = 1
    items.append({"@type":"ListItem","position":pos,"name":city,"item":city_url}); pos += 1
    if len(locality.get("breadcrumb_trail", [])) == 3:
        micro = locality["breadcrumb_trail"][1]
        micro_url = f"{city_url}/{slugify(micro)}"
        items.append({"@type":"ListItem","position":pos,"name":micro,"item":micro_url}); pos += 1
    items.append({"@type":"ListItem","position":pos,"name":locality['locality_name'],"item":canonical})
    breadcrumb = {"@type":"BreadcrumbList","itemListElement": items}

    # FAQPage
    faq_entities = []
    for qa in (faqs or []):
        q = qa.get("q","").strip()
        a = qa.get("a","").strip()
        if not q or not a: continue
        faq_entities.append({"@type":"Question","name": q,"acceptedAnswer":{"@type":"Answer","text": a}})
    faqpage = {"@type":"FAQPage","mainEntity": faq_entities} if faq_entities else {}

    # Nearby localities ItemList
    nearby = locality.get("nearby_localities", [])
    itemlist = {
      "@type":"ItemList",
      "name": f"Nearby Localities to {locality['locality_name']}",
      "itemListElement": [
        {"@type":"ListItem","position": i+1,"url": f"https://www.squareyards.com/{slugify(locality['city_name'])}/{slugify(n['name'])}","name": n["name"]}
        for i, n in enumerate(nearby[:10])
      ]
    }

    # News ItemList (if provided)
    news = locality.get("local_news") or []
    news_items = []
    for i, n in enumerate(news[:10]):
        title = n.get("title","")
        url = n.get("source_url","")
        if not title or not url: continue
        news_items.append({"@type":"ListItem","position": i+1,"name": title,"url": url})
    news_list = {"@type":"ItemList","name": f"{locality['locality_name']} – Local News","itemListElement": news_items} if news_items else {}

    graph = {"@context":"https://schema.org","@graph":[]}
    if place: graph["@graph"].append(place)
    if items: graph["@graph"].append(breadcrumb)
    if faq_entities: graph["@graph"].append(faqpage)
    if nearby: graph["@graph"].append(itemlist)
    if news_items: graph["@graph"].append(news_list)
    return graph
