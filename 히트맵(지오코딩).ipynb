#필요 패키지 import
import pandas as pd
import numpy as np
import folium
from folium import plugins
from folium.plugins import MarkerCluster
import json
import geopy.distance
import cx_Oracle
import os
import googlemaps

#오라클 접속
connect = cx_Oracle.connect("yiji", "1234", "localhost:1521/xe") #오라클 데이터베이스 연결(이름, 비밀번호)
cursor1 = connect.cursor()

#필요 데이터 가져올 쿼리
BOX="""
    SELECT CU_NM, CU_ADD, SUM(BOX_TOT)
    FROM KYO_CU_MST, KYO_OUT
    WHERE STO_NM=CU_NM
    GROUP BY CU_NM, CU_ADD"""
cursor1.execute(BOX)

#가져온 데이터를 데이터프레임으로
df_box=pd.DataFrame(cursor1.fetchall())
df_box.columns = ['납품처명', '주소', '물동량(연)'] #컬럼명 설정
cursor1.close()

df_box['위도']=''
df_box['경도']=''
df_box['SIG_KOR_NM']=''



#위경도로부터 역 지오코딩하여 시군구 추출
gmaps_key = 'AIzaSyBm4ymMNoNW6zoFhGZhAoB_jSUrShAS7KM'
gmaps = googlemaps.Client(key=gmaps_key) #구글맵 인증
#1000건 당 6013원, 누적됨

#주소 구하는 함수
def geocode(x):
    global lat_no
    global lon_no
    global addr1
    global addr2
    global addr3
    global SIG_KOR_NM

    postal_code,addr1,addr2,addr2_2,addr3,addr4,addr6 = '','','','','','',''
    lat_lon = gmaps.geocode(x , language="ko")
        
    lat_no = lat_lon[0]["geometry"]["location"]["lat"] #경도
    #print(lat_no)
    lon_no = lat_lon[0]["geometry"]["location"]["lng"] #위도
    #print(lon_no)
    lat_lon_cnt = len(lat_lon[0]["address_components"]) #주소 요소 수

    for t in range(lat_lon_cnt):
        type = lat_lon[0]["address_components"][t]["types"][0]
        if type == 'postal_code':
            postal_code = lat_lon[0]["address_components"][t]["long_name"]
        elif type == 'premise':
            addr6 = lat_lon[0]["address_components"][t]["long_name"]                
        elif type == 'political':
            if lat_lon[0]["address_components"][t]["types"][2] == 'sublocality_level_4':
                addr4 = lat_lon[0]["address_components"][t]["long_name"]
                #print(addr3)
            elif lat_lon[0]["address_components"][t]["types"][2] == 'sublocality_level_2':
                addr3 = lat_lon[0]["address_components"][t]["long_name"]
                #print(addr3_2)
            elif lat_lon[0]["address_components"][t]["types"][2] == 'sublocality_level_1':
                addr2_2 = lat_lon[0]["address_components"][t]["long_name"]
                #print(addr2_2)                        
        elif type == 'administrative_area_level_1':
            addr1 = lat_lon[0]["address_components"][t]["long_name"]
        elif type == 'locality':
            addr2 = lat_lon[0]["address_components"][t]["long_name"]

        if addr2=='':
            SIG_KOR_NM=addr1+' '+addr2_2
        else:
            SIG_KOR_NM=addr1+' '+addr2

    return lat_no, lon_no, SIG_KOR_NM

#기존 데이터에 위도, 경도, 시군구 추가
for t in range(len(df_box)):
    geocode(df_box.iloc[t, 1])
    df_box.iloc[t, 3]= lat_no
    df_box.iloc[t, 4]= lon_no
    df_box.iloc[t, 5]= SIG_KOR_NM
df_box['SIG_KOR_NM']= df_box['SIG_KOR_NM'].str.replace('충청북도 청원군', '충청북도 청주시')
df_box['SIG_KOR_NM']= df_box['SIG_KOR_NM'].str.replace('인천광역시 남구', '인천광역시 미추홀구')


#수정 시 reverse 지오코딩 돌리지 말고 자료 import
#df_box=pd.read_excel('C:/Users/user/Desktop/히트맵_작업/지오코딩 결과.xlsx')



##정확하지 않은 주소 데이터 중심좌표로 주소 구하기

#부정확한 데이터 걸러내기
df=pd.concat([df_box, df_box['SIG_KOR_NM'].str.split(" ", expand=True)], axis=1)
df_null=pd.concat([df[df[0]==''], df[df[1]=='']])
#정확한 데이터
index0=df[df[0]==''].index
index1=df[df[1]==''].index
df=df.drop(index0)
df=df.drop(index1)



#중심좌표 import
df_coord= pd.read_excel('C:/Users/user/Desktop/히트맵_작업/코드/시군구(중심좌표).xlsx')
df_coord=df_coord.loc[:, ['SIG_KOR_NM', 'x', 'y']]

#중심좌표 구하는 함수
def shortest(i, j):
        dis= [geopy.distance.geodesic((i, j), (x, y)).km for x, y in (zip(df_coord['y'], df_coord['x']))]
        near=min(dis)
        near_cd=dis.index(near)
        short_cd=df_coord['SIG_KOR_NM'][near_cd]
        return short_cd

#중심좌표 이용하여 주소 구하기
for i in range(len(df_null)):
    s=shortest(df_null.iloc[i, 2], df_null.iloc[i, 3])
    df_null.iloc[i, 4]=s

df_null.to_excel('오류값 확인2.xlsx', index=False)
#df_null=pd.read.excel('C:/Users/user/Desktop/히트맵_작업/오류값 확인1.xlsx')

#기존 데이터들 합치기
df_null.drop([0, 1], axis=1, inplace=True)
df.drop([0, 1], axis=1, inplace=True)
df_oracle=pd.concat([df, df_null], ignore_index=True)
df_oracle=df_oracle.sort_values('SIG_KOR_NM')
df_oracle=df_oracle[['납품처명', 'SIG_KOR_NM', '주소', '위도', '경도', '물동량(연)']]
df_oracle=df_oracle.rename(columns={'물동량(연)':'물동량'})




#오라클 데이터베이스에 테이블 업데이트
cursor2 = connect.cursor()
TABLE="""
    CREATE TABLE GEO_BOX 
    ( 
        cu_nm  VARCHAR2(100)
        ,sto  VARCHAR2(100)
        ,ADDR  VARCHAR2(600)
        ,LAT_NO  NUMBER(12, 9)
        ,LON_NO NUMBER(12, 9)
        ,BOX_TOT  NUMBER(38, 3)
   )
"""
cursor2.execute(TABLE)
cursor2.close()

#테이블에 데이터 insert
cursor3 = connect.cursor()
for i in range(len(df_oracle)) :
    query = (
    	f'insert into GEO_BOX (cu_nm, sto, addr, LAT_NO, LON_NO, box_tot)'
    	f'values(\'{df_oracle.납품처명.iloc[i]}\', \'{df_oracle.SIG_KOR_NM.iloc[i]}\', ' 
        f'\'{df_oracle.주소.iloc[i]}\', {df_oracle.위도.iloc[i]},' 
    	f'{df_oracle.경도.iloc[i]}, {df_oracle.물동량.iloc[i]})'
    )
    cursor3.execute(query)
    connect.commit()
cursor3.close()
connect.close()





#시군구 별 물동량 합계
df_oracle=df_oracle.rename(columns={'물동량':'물동량(연)'})
a=df_oracle.drop(['납품처명', '주소', '위도', '경도'], axis=1)
b=a['물동량(연)'].groupby(a['SIG_KOR_NM'])
a=b.sum()
a=pd.DataFrame(a)
a['SIG_KOR_NM']=a.index
a=a.reset_index(drop=True)
a['물동량(연)']=a['물동량(연)'].astype('float')

#지리 정보 파일에 대응되도록 데이터프레임 합치기
df_info=pd.read_excel('C:/Users/user/Desktop/히트맵_작업/시군구(지오코딩).xlsx')
df_heat=pd.merge(a, df_info, on='SIG_KOR_NM', how='outer')
df_heat.drop(['SIG_CD'], axis=1, inplace=True)




#geojson 지리 정보 파일 import
a='C:/Users/user/Desktop/히트맵_작업/지리데이터(지오코딩).geojson'
geo=json.load(open(a, encoding='utf-8'))
m= folium.Map((37.0871367274512, 127.0979525129808),zoom_start=8) #지도 생성





##납품처 위치 표시
df_loc=df_oracle.drop(['물동량(연)', '주소', 'SIG_KOR_NM'], axis=1) #납품처 데이터프레임

mc1 = MarkerCluster() #물류센터 마커
warehouse=(37.0871367274512, 127.0979525129808)
mc1.add_child(folium.Marker(location=warehouse,popup='<pre>물류센터',icon=folium.Icon(color='red',icon='star')))
m.add_child(mc1)

mc2 = MarkerCluster() #납품처 마커
for row in df_loc.itertuples():
    mc2.add_child(folium.Marker(location=[row.위도, row.경도], popup=row.납품처명))
m.add_child(mc2)





##히트맵 시각화
bins=list(df_heat['물동량(연)'].quantile([0, 0.5, 0.9, 1]))

map_heat = folium.Choropleth(
    geo_data=geo,
    data=df_heat,
    columns=('SIG_KOR_NM', '물동량(연)'),
    nan_fill_color='grey',
    nan_fill_opacity=0.4,
    key_on='feature.properties.merged',
    fill_color='Reds',
    fill_opacity=0.7,
    line_weight=0.4,
    bins=bins,
    legend_name='물동량(연)').add_to(m)




#지도 위에 글씨 생성
df_heat=df_heat.fillna(0)
for i, j in enumerate(geo['features']):
    sig_nm=j['properties']['merged']
    boxes=df_heat.loc[(df_heat.SIG_KOR_NM==sig_nm), '물동량(연)'].iloc[0]
    txt=f'<b><h4>{sig_nm}</h4></b>물동량(연) :{boxes}'

    geo['features'][i]['properties']['tooltip1']=txt

map_heat.geojson.add_child(folium.features.GeoJsonTooltip(['tooltip1'], labels=False))
folium.LayerControl().add_to(m)

m.save('히트맵(지오코딩).html')
m

#pyinstaller -w -F 프로그램1.py
#dist 폴더에 import에 필요한 파일 복사해두기