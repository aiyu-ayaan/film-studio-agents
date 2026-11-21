"""Natural Earth 50m admin-0 -> Europe SVG paths (Lambert conformal conic). Output: assets/maps/europe.json
Usage: python3 assets/maps/make_europe.py"""
import json, math
from pathlib import Path
root = Path(__file__).resolve().parents[2]
G = json.load(open(root/"assets/images/naturalearth/ne_50m_admin_0_countries.geojson"))
LON0, LAT0, P1, P2 = math.radians(18), math.radians(52), math.radians(38), math.radians(66)
n = math.log(math.cos(P1)/math.cos(P2))/math.log(math.tan(math.pi/4+P2/2)/math.tan(math.pi/4+P1/2))
F = math.cos(P1)*math.tan(math.pi/4+P1/2)**n/n
rho0 = F/math.tan(math.pi/4+LAT0/2)**n
SCALE = 3000  # world units per radian-ish: Europe fills ~2100 x 2600
def proj(lon, lat):
    lam, ph = math.radians(lon), math.radians(lat)
    rho = F/math.tan(math.pi/4+ph/2)**n
    th = n*(lam-LON0)
    return (SCALE*rho*math.sin(th)+1080, -SCALE*(rho0-rho*math.cos(th))+1500)  # centre of map ~ (1080,1500)
def dp(pts, tol):
    if len(pts) < 3: return pts
    (x1,y1),(x2,y2) = pts[0], pts[-1]
    dx,dy = x2-x1,y2-y1; L = math.hypot(dx,dy) or 1e-9
    m,i = 0,0
    for k in range(1,len(pts)-1):
        d = abs(dy*pts[k][0]-dx*pts[k][1]+x2*y1-y2*x1)/L
        if d>m: m,i=d,k
    if m>tol: return dp(pts[:i+1],tol)[:-1]+dp(pts[i:],tol)
    return [pts[0],pts[-1]]
def area(r): return abs(sum(r[i][0]*r[(i+1)%len(r)][1]-r[(i+1)%len(r)][0]*r[i][1] for i in range(len(r))))/2
out = {}
for f in G["features"]:
    nm = f["properties"]["NAME"]
    g = f["geometry"]; polys = g["coordinates"] if g["type"]=="MultiPolygon" else [g["coordinates"]]
    parts=[]; cx=cy=ca=0
    for poly in polys:
        ring = poly[0]
        if not any(-30<=x<=70 and 25<=y<=75 for x,y in ring): continue
        # drop antimeridian wraps (Russia, Fiji): keep rings inside window only
        if any(x>75 or x<-35 for x,y in ring) and nm=="Russia": ring=[(min(max(x,-35),75),y) for x,y in ring]
        p=[proj(x,y) for x,y in ring]
        a=area(p)
        if a<250: continue
        h=len(p)//2; p=dp(p[:h+1],1.2)[:-1]+dp(p[h:],1.2)  # ring: split in two so the closed loop does not collapse
        parts.append("M"+"L".join(f"{x:.0f},{y:.0f}" for x,y in p)+"Z")
        cx+=sum(x for x,_ in p)/len(p)*a; cy+=sum(y for _,y in p)/len(p)*a; ca+=a
    if parts: out[nm]={"d":"".join(parts),"c":[round(cx/ca),round(cy/ca)]}
pts = {"Berlin":(13.4,52.5),"Vienna":(16.4,48.2),"Prague":(14.4,50.1),"Sudetenland":(13.0,50.3),"Warsaw":(21.0,52.2),"Gdansk":(18.65,54.35),"Paris":(2.35,48.85),"London":(-0.1,51.5),"Moscow":(37.6,55.75),"Stalingrad":(44.5,48.7),"Normandy":(-0.6,49.35),"Oslo":(10.75,59.9),"Brussels":(4.35,50.85),"Amsterdam":(4.9,52.4),"Cologne":(6.96,50.94),"Munich":(11.6,48.1),"Dover":(1.3,51.1),"Copenhagen":(12.57,55.68),"Lviv":(24.0,49.84),"Kyiv":(30.5,50.45),"Rome":(12.5,41.9)}
out_pts = {k:[round(v) for v in proj(*ll)] for k,ll in pts.items()}
json.dump({"size":[2160,3000],"center":[1080,1500],"scale":SCALE,"countries":out,"points":out_pts,"note":"Modern borders; Natural Earth public domain. proj = Lambert conformal conic lon0 18 lat0 52 p1 38 p2 66."},open(root/"assets/maps/europe.json","w"),separators=(",",":"))
b=[v for c in out.values() for v in c["c"]]
print(len(out),"countries; points",out_pts["Berlin"],out_pts["Moscow"],out_pts["London"],"size KB",round((root/"assets/maps/europe.json").stat().st_size/1024))
